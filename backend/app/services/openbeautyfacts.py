import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

USER_AGENT = "PersonalCareProductScanner/1.0 (github.com/muhammad-dz/personal-care-product-scanner)"

# Open Beauty Facts first, then Open Food Facts, which also lists some toiletries
SOURCES = [
    ("Open Beauty Facts", "https://world.openbeautyfacts.org/api/v2/product/{barcode}.json"),
    ("Open Food Facts", "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"),
]


class ProductLookupError(Exception):
    pass


def _ingredients(product: dict) -> list:
    names = [i.get("text") or i.get("id", "") for i in product.get("ingredients", [])]
    names = [n for n in names if n]
    if names:
        return names

    text = product.get("ingredients_text_en") or product.get("ingredients_text") or ""
    return [part.strip() for part in text.split(",") if part.strip()]


async def fetch_product(barcode: str, client: Optional[httpx.AsyncClient] = None) -> Optional[dict]:
    """Return the product for a barcode, or None if no source has it.

    Raises ProductLookupError if the upstream APIs can't be reached.
    """
    own_client = client is None
    client = client or httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=10.0,
                                         follow_redirects=True)
    errors = 0
    try:
        for source, url in SOURCES:
            try:
                response = await client.get(url.format(barcode=barcode))
            except httpx.HTTPError as exc:
                logger.warning("%s request failed: %s", source, exc)
                errors += 1
                continue

            if response.status_code == 404:
                continue
            if response.status_code != 200:
                logger.warning("%s returned HTTP %s", source, response.status_code)
                errors += 1
                continue

            data = response.json()
            if data.get("status") != 1:
                continue

            product = data.get("product", {})
            return {
                "barcode": product.get("code", barcode),
                "product_name": product.get("product_name") or "Unknown product",
                "brands": product.get("brands") or None,
                "image_url": product.get("image_url") or None,
                "source": source,
                "ingredients": _ingredients(product),
            }
    finally:
        if own_client:
            await client.aclose()

    if errors == len(SOURCES):
        raise ProductLookupError("product databases are unreachable")
    return None
