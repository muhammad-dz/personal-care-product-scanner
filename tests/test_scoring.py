import pytest

from app.services.scoring import BASE_SCORE, MAX_BENEFIT_BONUS, band_for, classify, score_ingredients


def rule_of(name):
    return classify(name).rule


@pytest.mark.parametrize("ingredient, rule", [
    ("Methylparaben", "paraben"),
    ("ETHYLPARABEN", "paraben"),
    ("Sodium Laureth Sulfate", "sulfate"),
    ("Parfum (Fragrance)", "fragrance"),
    ("Alcohol Denat.", "drying alcohol"),
    ("Alcohol", "drying alcohol"),
    ("PEG-100 Stearate", "peg compound"),
    ("Diethyl Phthalate", "phthalate"),
    ("Niacinamide", "niacinamide"),
    ("Ceramide NP", "ceramide"),
    ("Acetyl Dipeptide-1 Cetyl Ester", "peptide"),
    ("Butyrospermum Parkii (Shea) Butter", "butter"),
])
def test_known_ingredients(ingredient, rule):
    assert rule_of(ingredient) == rule


@pytest.mark.parametrize("ingredient", [
    "Cetearyl Alcohol",  # fatty alcohols are emollients, not drying
    "Cetyl Alcohol",
    "Benzyl Alcohol",
    "Aqua (Water)",
    "Sodium Lauroyl Lactylate",  # not the same as sodium lauryl sulfate
])
def test_harmless_lookalikes_are_not_flagged(ingredient):
    assert classify(ingredient).effect == "neutral"


def test_methylparaben_is_counted_once():
    # "methylparaben" contains "ethylparaben" and used to be penalised twice
    result = score_ingredients(["Methylparaben"])
    assert result["concerns"] == 1
    assert result["penalty"] == -15


def test_score_is_explained_by_its_parts():
    result = score_ingredients(["Water", "Glycerin", "Niacinamide", "Fragrance", "Methylparaben"])
    listed = sum(i["points"] for i in result["ingredients"])
    assert result["penalty"] + result["bonus"] == listed
    assert result["score"] == BASE_SCORE + listed


def test_benefit_bonus_is_capped():
    loaded = ["Niacinamide", "Ascorbic Acid", "Sodium Hyaluronate", "Ceramide NP", "Retinol", "Squalane"]
    result = score_ingredients(loaded)
    assert result["bonus"] == MAX_BENEFIT_BONUS
    assert result["bonus_capped"] is True
    assert result["score"] == 100


def test_score_never_goes_below_zero():
    nasty = ["Methylparaben", "Propylparaben", "Butylparaben", "Triclosan", "Hydroquinone", "Oxybenzone"]
    assert score_ingredients(nasty)["score"] == 0


def test_duplicates_and_blanks_are_ignored():
    result = score_ingredients(["Fragrance", "fragrance ", "", None, "Water"])
    assert result["concerns"] == 1
    assert len(result["ingredients"]) == 2


def test_empty_list():
    result = score_ingredients([])
    assert result["score"] == BASE_SCORE
    assert result["ingredients"] == []


@pytest.mark.parametrize("score, band", [(100, "Excellent"), (80, "Excellent"), (79, "Good"),
                                         (60, "Good"), (45, "Moderate"), (20, "Poor"), (0, "Avoid")])
def test_bands(score, band):
    assert band_for(score) == band
