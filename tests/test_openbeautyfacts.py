import asyncio

import httpx
import pytest

from app.services.openbeautyfacts import ProductLookupError, fetch_product


def run(handler, barcode="3600523614417"):
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return asyncio.run(fetch_product(barcode, client=client))


def found(product):
    return httpx.Response(200, json={"status": 1, "product": product})


def test_uses_structured_ingredients():
    product = run(lambda r: found({"product_name": "Cream", "brands": "Acme",
                                   "ingredients": [{"text": "Aqua"}, {"id": "en:glycerin"}, {"text": ""}]}))
    assert product["product_name"] == "Cream"
    assert product["source"] == "Open Beauty Facts"
    assert product["ingredients"] == ["Aqua", "en:glycerin"]


def test_falls_back_to_ingredient_text():
    product = run(lambda r: found({"ingredients_text": "Water, Glycerin , ,Niacinamide"}))
    assert product["ingredients"] == ["Water", "Glycerin", "Niacinamide"]
    assert product["product_name"] == "Unknown product"


def test_tries_open_food_facts_when_beauty_has_nothing():
    def handler(request):
        if "openbeautyfacts" in request.url.host:
            return httpx.Response(200, json={"status": 0})
        return found({"product_name": "Hand Soap"})

    product = run(handler)
    assert product["source"] == "Open Food Facts"


def test_not_found_anywhere():
    assert run(lambda r: httpx.Response(404)) is None


def test_one_source_down_is_not_fatal():
    def handler(request):
        if "openbeautyfacts" in request.url.host:
            return httpx.Response(503)
        return httpx.Response(200, json={"status": 0})

    assert run(handler) is None


def test_all_sources_down_raises():
    def handler(request):
        raise httpx.ConnectError("offline", request=request)

    with pytest.raises(ProductLookupError):
        run(handler)
