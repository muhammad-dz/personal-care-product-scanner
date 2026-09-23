import pandas as pd
from fastapi.testclient import TestClient

from app.api import products, reviews, scan
from app.main import app
from app.services.ocr import OCRUnavailable

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_rate():
    res = client.post("/api/rating", json={"ingredients": ["Water", "Niacinamide", "Methylparaben"]})
    assert res.status_code == 200
    assert res.json()["concerns"] == 1


def test_rate_rejects_empty_list():
    assert client.post("/api/rating", json={"ingredients": []}).status_code == 422


def test_ingredient_lookup():
    assert client.get("/api/rating/ingredient/Triclosan").json()["effect"] == "concern"
    assert client.get("/api/rating/ingredient/Water").json()["effect"] == "neutral"


def test_product_lookup(monkeypatch):
    async def fake(barcode):
        return {"barcode": barcode, "product_name": "Cream", "brands": None, "image_url": None,
                "source": "Open Beauty Facts", "ingredients": ["Water", "Glycerin"]}

    monkeypatch.setattr(products, "fetch_product", fake)
    body = client.get("/api/products/12345678").json()
    assert body["product_name"] == "Cream"
    assert body["rating"]["band"] in {"Excellent", "Good"}


def test_product_without_ingredients_has_no_rating(monkeypatch):
    async def fake(barcode):
        return {"barcode": barcode, "product_name": "Mystery", "ingredients": []}

    monkeypatch.setattr(products, "fetch_product", fake)
    assert client.get("/api/products/12345678").json()["rating"] is None


def test_product_not_found(monkeypatch):
    async def fake(barcode):
        return None

    monkeypatch.setattr(products, "fetch_product", fake)
    assert client.get("/api/products/12345678").status_code == 404


def test_bad_barcode():
    assert client.get("/api/products/abc").status_code == 400


def test_scan(monkeypatch):
    monkeypatch.setattr(scan, "read_image", lambda data: "Ingredients: Water, Glycerin, Fragrance")
    res = client.post("/api/scan", files={"file": ("label.jpg", b"fake", "image/jpeg")})
    assert res.status_code == 200
    assert res.json()["ingredients"] == ["Water", "Glycerin", "Fragrance"]
    assert res.json()["rating"]["concerns"] == 1


def test_scan_without_ingredients(monkeypatch):
    monkeypatch.setattr(scan, "read_image", lambda data: "")
    res = client.post("/api/scan", files={"file": ("label.jpg", b"fake", "image/jpeg")})
    assert res.status_code == 422


def test_scan_rejects_non_images():
    res = client.post("/api/scan", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert res.status_code == 415


def test_scan_when_ocr_missing(monkeypatch):
    def broken(data):
        raise OCRUnavailable("no tesseract")

    monkeypatch.setattr(scan, "read_image", broken)
    res = client.post("/api/scan", files={"file": ("label.jpg", b"fake", "image/jpeg")})
    assert res.status_code == 503


def test_reviews_summary(tmp_path, monkeypatch):
    path = tmp_path / "reviews.csv"
    pd.DataFrame([{"product_name": "A", "rating": 1, "text": "Gave me a terrible rash", "source": "test"}]) \
        .to_csv(path, index=False)
    monkeypatch.setattr(reviews, "REVIEWS_FILE", path)
    reviews._cache.clear()

    body = client.get("/api/reviews/summary").json()
    assert body["total_reviews"] == 1
    assert body["top_issues"] == [{"issue": "rash", "count": 1}]


def test_reviews_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(reviews, "REVIEWS_FILE", tmp_path / "nope.csv")
    reviews._cache.clear()
    assert client.get("/api/reviews/summary").status_code == 404
