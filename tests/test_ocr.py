import pytest

from app.services import ocr
from app.services.ocr import OCRUnavailable, parse_ingredients

LABEL = """Hydrating Cleanser 236ml
INGREDIENTS: Aqua, Glycerin, Cetearyl Alcohol,
Sodium Hyal-
uronate, Ceramide NP; Phenoxyethanol.
Directions: massage onto wet skin and rinse.
"""


def test_parses_label_between_heading_and_directions():
    assert parse_ingredients(LABEL) == [
        "Aqua", "Glycerin", "Cetearyl Alcohol", "Sodium Hyaluronate", "Ceramide NP", "Phenoxyethanol",
    ]


def test_works_without_a_heading():
    assert parse_ingredients("Water, Glycerin, Niacinamide") == ["Water", "Glycerin", "Niacinamide"]


def test_keeps_hyphenated_ingredient_names():
    assert parse_ingredients("Ingredients: PEG-40 Stearate, Quaternium-15") == ["PEG-40 Stearate", "Quaternium-15"]


def test_drops_ocr_noise():
    assert parse_ingredients("Ingredients: Water, |, ., 12, Glycerin") == ["Water", "Glycerin"]


def test_other_languages():
    assert parse_ingredients("Ingrédients : Aqua, Glycerin") == ["Aqua", "Glycerin"]


def test_missing_tesseract_is_reported(monkeypatch):
    monkeypatch.setattr(ocr, "pytesseract", None)
    with pytest.raises(OCRUnavailable):
        ocr.read_image(b"not used")
