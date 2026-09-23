"""API-level tests for the FastAPI backend using TestClient (no real network)."""
import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "healthy"}


def test_rate_product_endpoint():
    res = client.post("/api/rating/rate-product", json={
        "product_name": "Test Serum",
        "ingredients": ["Water", "Niacinamide", "Methylparaben"],
        "product_type": "serum",
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["product_name"] == "Test Serum"
    assert data["risk_ingredients"] == 1
    assert 0 <= data["final_score"] <= 100


def test_rate_product_rejects_invalid_body():
    res = client.post("/api/rating/rate-product", json={"product_name": "No ingredients"})
    assert res.status_code == 422


@pytest.mark.parametrize("name, expected", [
    ("Triclosan", "risk"),
    ("Niacinamide", "beneficial"),
    ("Water", "neutral"),
])
def test_ingredient_info(name, expected):
    assert client.get(f"/api/rating/ingredient-info/{name}").json()["category"] == expected


def test_batch_check_scores_each_ingredient():
    # The frontend sends {"ingredients": [...]}, so the API must accept that shape.
    res = client.post("/api/ocr/batch-check", json={"ingredients": ["Water", "Butylparaben", "Unknownium"]})
    assert res.status_code == 200
    body = res.json()
    assert [r["rating"] for r in body["results"]] == ["Excellent", "Poor", "Good"]
    assert body["total_ingredients"] == 3


def test_barcode_lookup_attaches_rating(monkeypatch):
    async def fake_lookup(self, barcode):
        return {"success": True, "product_name": "Mock Cream", "ingredients_list": ["Water", "Glycerin"]}

    monkeypatch.setattr(main.OpenBeautyFactsClient, "get_product_by_barcode", fake_lookup)
    body = client.get("/api/beauty/lookup/123").json()
    assert body["rating_data"]["product_name"] == "Mock Cream"


def test_barcode_lookup_not_found_has_no_rating(monkeypatch):
    async def fake_lookup(self, barcode):
        return {"success": False, "error": "Product not found", "barcode": barcode}

    monkeypatch.setattr(main.OpenBeautyFactsClient, "get_product_by_barcode", fake_lookup)
    body = client.get("/api/beauty/lookup/000").json()
    assert body["success"] is False
    assert "rating_data" not in body
