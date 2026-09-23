import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import UnidentifiedImageError

from app.config import MAX_UPLOAD_BYTES
from app.services.ocr import OCRUnavailable, parse_ingredients, read_image
from app.services.scoring import score_ingredients

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/scan", tags=["scan"])


@router.post("")
async def scan_label(file: UploadFile = File(...)):
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(415, "Please upload an image")

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Image is too large")

    try:
        text = read_image(data)
    except UnidentifiedImageError:
        raise HTTPException(400, "Couldn't read that file as an image")
    except OCRUnavailable as exc:
        logger.error("OCR unavailable: %s", exc)
        raise HTTPException(503, "Text recognition isn't set up on the server")

    ingredients = parse_ingredients(text)
    if not ingredients:
        raise HTTPException(422, "Couldn't find an ingredient list in that photo. "
                                 "Try a closer, well lit shot of the label.")

    return {"text": text, "ingredients": ingredients, "rating": score_ingredients(ingredients)}
