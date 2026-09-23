"""Unit tests for the ingredient-based product rating algorithm."""
import pytest

from app.services.rating_algorithm import BatchRatingProcessor, ProductRatingAlgorithm

CLEAN = ["Water", "Glycerin", "Hyaluronic Acid", "Niacinamide", "Ceramide NP", "Panthenol"]
HARSH = ["Water", "Sodium Lauryl Sulfate", "Fragrance", "Alcohol Denat"]
HIGH_RISK = ["Water", "Methylparaben", "Triclosan", "Oxybenzone", "Hydroquinone"]

VALID_RATINGS = {"Excellent", "Good", "Moderate", "Poor", "Avoid"}


@pytest.fixture(scope="module")
def algo():
    return ProductRatingAlgorithm()


def test_clean_formula_scores_higher_than_harsh_formula(algo):
    clean = algo.calculate_product_rating("Clean", CLEAN, "moisturizer")
    harsh = algo.calculate_product_rating("Harsh", HARSH, "moisturizer")
    assert clean["final_score"] > harsh["final_score"]


def test_high_risk_ingredients_are_rated_avoid(algo):
    result = algo.calculate_product_rating("Risky", HIGH_RISK)
    assert result["rating"] == "Avoid"
    assert result["risk_ingredients"] >= 4


def test_clean_formula_has_no_risks_and_counts_benefits(algo):
    result = algo.calculate_product_rating("Clean", CLEAN, "moisturizer")
    assert result["risk_ingredients"] == 0
    assert result["beneficial_ingredients"] >= 3


@pytest.mark.parametrize("ingredients", [[], CLEAN, HARSH, HIGH_RISK, HIGH_RISK * 5])
def test_score_is_always_between_0_and_100(algo, ingredients):
    score = algo.calculate_product_rating("Any", ingredients)["final_score"]
    assert 0 <= score <= 100


def test_score_never_exceeds_product_type_cap(algo):
    # Cleansers are capped at 85 regardless of how many beneficial ingredients they have.
    result = algo.calculate_product_rating("Loaded cleanser", CLEAN * 3, "cleanser")
    assert result["final_score"] <= 85


def test_unknown_product_type_falls_back_to_default(algo):
    result = algo.calculate_product_rating("Mystery", CLEAN, "not-a-real-type")
    assert result["rating"] in VALID_RATINGS


def test_matching_is_case_insensitive(algo):
    lower = algo.calculate_product_rating("a", ["methylparaben"])
    upper = algo.calculate_product_rating("a", ["METHYLPARABEN"])
    assert lower["final_score"] == upper["final_score"]
    assert lower["risk_ingredients"] == upper["risk_ingredients"] == 1


def test_overlapping_names_are_not_double_counted(algo):
    # Regression: "methylparaben" contains "ethylparaben" as a substring and
    # used to be penalised twice.
    methyl = algo.calculate_product_rating("a", ["Methylparaben"])
    ethyl = algo.calculate_product_rating("a", ["Ethylparaben"])
    assert methyl["risk_ingredients"] == 1
    assert methyl["risk_details"][0]["reason"]
    assert methyl["final_score"] == ethyl["final_score"]


def test_risk_details_explain_each_flag(algo):
    result = algo.calculate_product_rating("Harsh", HARSH)
    for risk in result["risk_details"]:
        assert risk["ingredient"] in HARSH
        assert risk["reason"]
        assert risk["points_deducted"] > 0


def test_empty_and_non_string_ingredients_are_ignored(algo):
    result = algo.calculate_product_rating("Messy input", ["", None, "Water"])
    assert result["risk_ingredients"] == 0


def test_normalize_ingredient_name_strips_prefix_and_suffix(algo):
    assert algo.normalize_ingredient_name("  Sodium Hyaluronate ") == "hyaluronate"
    assert algo.normalize_ingredient_name("Jojoba Oil") == "jojoba"
    assert algo.normalize_ingredient_name(None) == ""


def test_rating_bands_match_score(algo):
    for ingredients in ([], CLEAN, HARSH, HIGH_RISK):
        r = algo.calculate_product_rating("x", ingredients)
        s = r["final_score"]
        expected = (
            "Excellent" if s >= 80 else
            "Good" if s >= 60 else
            "Moderate" if s >= 40 else
            "Poor" if s >= 20 else
            "Avoid"
        )
        assert r["rating"] == expected


def test_batch_processor_ranks_products():
    products = [
        {"product_name": "Risky", "ingredients": HIGH_RISK},
        {"product_name": "Clean", "ingredients": CLEAN, "product_type": "moisturizer"},
        {"product_name": "Harsh", "ingredients": HARSH},
    ]
    processor = BatchRatingProcessor()
    assert processor.get_top_rated(products, n=1)[0]["product_name"] == "Clean"
    assert processor.get_worst_rated(products, n=1)[0]["product_name"] == "Risky"
