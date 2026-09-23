import io
import re
from typing import List

from PIL import Image, ImageOps

try:
    import pytesseract
except ImportError:  # optional: only needed for the image scan endpoint
    pytesseract = None


class OCRUnavailable(RuntimeError):
    pass


# where the ingredient list starts on a label (English, French, German, INCI)
_START = re.compile(r"\b(ingredients?|ingr[ée]dients?|inhaltsstoffe|inci)\b\s*[:\-]?", re.IGNORECASE)
# common things printed after the list that we don't want
_STOP = re.compile(r"\b(directions|how to use|warning|caution|made in|best before|may contain)\b",
                   re.IGNORECASE)


def read_image(data: bytes) -> str:
    if pytesseract is None:
        raise OCRUnavailable("pytesseract is not installed")

    image = Image.open(io.BytesIO(data))
    image = ImageOps.exif_transpose(image)
    image = ImageOps.grayscale(image)

    # tesseract struggles with small print, so upscale small photos
    if image.width < 1500:
        scale = 1500 / image.width
        image = image.resize((1500, int(image.height * scale)))

    image = ImageOps.autocontrast(image)

    try:
        return pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError as exc:
        raise OCRUnavailable("tesseract is not installed on this machine") from exc


def parse_ingredients(text: str) -> List[str]:
    """Pull an ingredient list out of raw OCR text."""
    start = _START.search(text)
    if start:
        text = text[start.end():]

    stop = _STOP.search(text)
    if stop:
        text = text[:stop.start()]

    # join words hyphenated across a line break, then flatten the lines
    text = re.sub(r"(?<=[a-z])-\s*\n\s*(?=[a-z])", "", text)
    text = text.replace("\n", " ")

    ingredients = []
    for part in re.split(r"[,;•·]", text):
        part = part.strip(" .*:\t")
        part = re.sub(r"\s+", " ", part)
        # OCR noise tends to be very short or a whole run-on sentence
        if 2 <= len(part) <= 80 and re.search(r"[a-zA-Z]", part):
            ingredients.append(part)
    return ingredients
