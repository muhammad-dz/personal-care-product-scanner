import re

from fastapi import APIRouter, HTTPException

from app.services.openbeautyfacts import ProductLookupError, fetch_product
from app.services.scoring import score_ingredients

router = APIRouter(prefix="/api/products", tags=["products"])

BARCODE = re.compile(r"^\d{8,14}$")


@router.get("/{barcode}")
async def get_product(barcode: str):
    if not BARCODE.match(barcode):
        raise HTTPException(400, "Barcode should be 8 to 14 digits")

    try:
        product = await fetch_product(barcode)
    except ProductLookupError:
        raise HTTPException(502, "Couldn't reach the product database, try again shortly")

    if product is None:
        raise HTTPException(404, "No product found for that barcode")

    product["rating"] = score_ingredients(product["ingredients"]) if product["ingredients"] else None
    return product
