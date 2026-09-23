from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.scoring import classify, score_ingredients

router = APIRouter(prefix="/api/rating", tags=["rating"])


class RatingRequest(BaseModel):
    ingredients: List[str] = Field(min_length=1, max_length=200)


@router.post("")
def rate(request: RatingRequest):
    return score_ingredients(request.ingredients)


@router.get("/ingredient/{name}")
def ingredient(name: str):
    return classify(name)
