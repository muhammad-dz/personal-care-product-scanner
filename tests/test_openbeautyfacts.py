"""Unit tests for the Open Beauty Facts client.

The real HTTP API is never called: httpx.AsyncClient is swapped for one that
uses a MockTransport, so these tests are fast and deterministic.
"""
import asyncio

import httpx
import pytest

from app.services import openbeautyfacts
from app.services.openbeautyfacts import OpenBeautyFactsClient


def use_mock_api(monkeypatch, handler):
    real_client = httpx.AsyncClient

    def fake_client(*args, **kwargs):
        return real_client(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(openbeautyfacts.httpx, "AsyncClient", fake_client)


def lookup(barcode="3600523614417"):
    return asyncio.run(OpenBeautyFactsClient().get_product_by_barcode(barcode))


def test_parses_structured_ingredient_list(monkeypatch):
    def handler(request):
        assert request.url.path.endswith("/product/3600523614417.json")
        assert request.headers["User-Agent"].startswith("PersonalCareProductScanner")
        return httpx.Response(200, json={
            "status": 1,
            "product": {
                "code": "3600523614417",
                "product_name": "Test Cream",
                "brands": "TestBrand",
                "ingredients": [{"text": "Aqua"}, {"id": "en:glycerin"}, {"text": ""}],
            },
        })

    use_mock_api(monkeypatch, handler)
    result = lookup()

    assert result["success"] is True
    assert result["product_name"] == "Test Cream"
    assert result["ingredients_list"] == ["Aqua", "en:glycerin"]


def test_falls_back_to_splitting_ingredients_text(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={
            "status": 1,
            "product": {"product_name": "Plain", "ingredients_text": "Water, Glycerin , ,Niacinamide"},
        })

    use_mock_api(monkeypatch, handler)
    assert lookup()["ingredients_list"] == ["Water", "Glycerin", "Niacinamide"]


def test_product_not_found(monkeypatch):
    use_mock_api(monkeypatch, lambda request: httpx.Response(200, json={"status": 0}))
    result = lookup("0000000000000")
    assert result == {"success": False, "error": "Product not found", "barcode": "0000000000000"}


@pytest.mark.parametrize("status", [404, 500, 503])
def test_http_errors_are_reported_not_raised(monkeypatch, status):
    use_mock_api(monkeypatch, lambda request: httpx.Response(status))
    result = lookup()
    assert result["success"] is False
    assert result["error"] == f"HTTP {status}"


def test_network_failure_is_reported_not_raised(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("offline", request=request)

    use_mock_api(monkeypatch, handler)
    result = lookup()
    assert result["success"] is False
    assert "offline" in result["error"]
