import re
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import List, Optional

from app.rules import BENEFITS, CONCERNS, Rule

BASE_SCORE = 75
MAX_BENEFIT_BONUS = 25
PENALTY = {"high": 15, "medium": 7, "low": 3}

BANDS = [
    (80, "Excellent"),
    (60, "Good"),
    (40, "Moderate"),
    (20, "Poor"),
    (0, "Avoid"),
]


@dataclass
class IngredientResult:
    ingredient: str
    effect: str  # "concern", "benefit" or "neutral"
    rule: Optional[str] = None
    level: Optional[str] = None
    reason: Optional[str] = None
    points: int = 0


@lru_cache(maxsize=None)
def _compile(rule: Rule):
    # letters/digits either side of a match mean we are inside another word
    compiled = []
    for pattern in rule.patterns:
        if rule.whole:
            compiled.append(re.compile(rf"^{pattern}$"))
        else:
            compiled.append(re.compile(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])"))
    return compiled


def _matches(rule: Rule, name: str) -> bool:
    return any(p.search(name) for p in _compile(rule))


def normalise(ingredient: str) -> str:
    return " ".join(ingredient.lower().replace("*", "").split())


def classify(ingredient: str) -> IngredientResult:
    name = normalise(ingredient)

    for rule in CONCERNS:
        if _matches(rule, name):
            return IngredientResult(ingredient, "concern", rule.name, rule.level, rule.reason,
                                    -PENALTY[rule.level])

    for rule in BENEFITS:
        if _matches(rule, name):
            return IngredientResult(ingredient, "benefit", rule.name, None, rule.reason, rule.points)

    return IngredientResult(ingredient, "neutral")


def band_for(score: int) -> str:
    for threshold, label in BANDS:
        if score >= threshold:
            return label
    return BANDS[-1][1]


def score_ingredients(ingredients: List[str]) -> dict:
    seen = set()
    results = []
    for ingredient in ingredients:
        if not isinstance(ingredient, str) or not ingredient.strip():
            continue
        key = normalise(ingredient)
        if key in seen:
            continue
        seen.add(key)
        results.append(classify(ingredient.strip()))

    penalty = sum(r.points for r in results if r.effect == "concern")
    bonus = sum(r.points for r in results if r.effect == "benefit")
    capped_bonus = min(bonus, MAX_BENEFIT_BONUS)

    score = max(0, min(100, BASE_SCORE + penalty + capped_bonus))

    return {
        "score": score,
        "band": band_for(score),
        "base_score": BASE_SCORE,
        "penalty": penalty,
        "bonus": capped_bonus,
        "bonus_capped": bonus > MAX_BENEFIT_BONUS,
        "concerns": sum(1 for r in results if r.effect == "concern"),
        "benefits": sum(1 for r in results if r.effect == "benefit"),
        "ingredients": [asdict(r) for r in results],
    }
