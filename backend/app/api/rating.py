"""
API endpoint for product rating algorithm
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.services.rating_algorithm import ProductRatingAlgorithm, BatchRatingProcessor

router = APIRouter()
algorithm = ProductRatingAlgorithm()
batch_processor = BatchRatingProcessor()

class RatingRequest(BaseModel):
    product_name: str
    ingredients: List[str]
    product_type: str = "unknown"

class BatchRatingRequest(BaseModel):
    products: List[Dict[str, Any]]

@router.post("/rate-product")
async def rate_product(request: RatingRequest):
    """
    Rate a single product based on its ingredients
    """
    try:
        result = algorithm.calculate_product_rating(
            request.product_name,
            request.ingredients,
            request.product_type
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rate-batch")
async def rate_products(request: BatchRatingRequest):
    """
    Rate multiple products in batch
    """
    try:
        results = batch_processor.rate_products(request.products)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ingredient-info/{ingredient_name}")
async def get_ingredient_info(ingredient_name: str):
    """
    Get detailed information about a specific ingredient
    """
    try:
        # Check if it's a risk ingredient
        normalized = ingredient_name.lower()
        
        for risk_name, risk_info in algorithm.high_risk_ingredients.items():
            if risk_name in normalized:
                return {
                    "success": True,
                    "ingredient": ingredient_name,
                    "category": "risk",
                    "risk_level": risk_info['risk'],
                    "reason": risk_info['reason'],
                    "points_deducted": 10 if risk_info['risk'] == 'high' else 5
                }
        
        # Check if it's a beneficial ingredient
        for benefit_name, benefit_info in algorithm.beneficial_ingredients.items():
            if benefit_name in normalized:
                return {
                    "success": True,
                    "ingredient": ingredient_name,
                    "category": "beneficial",
                    "benefit": benefit_info['benefit'],
                    "points_added": benefit_info['points']
                }
        
        return {
            "success": True,
            "ingredient": ingredient_name,
            "category": "neutral",
            "message": "No significant concerns or benefits identified"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rating-categories")
async def get_rating_categories():
    """
    Get the rating categories and their score ranges
    """
    return {
        "success": True,
        "categories": [
            {"rating": "Excellent", "range": "80-100", "description": "Safe, beneficial ingredients"},
            {"rating": "Good", "range": "60-79", "description": "Generally safe, minor concerns"},
            {"rating": "Moderate", "range": "40-59", "description": "Mixed, proceed with caution"},
            {"rating": "Poor", "range": "20-39", "description": "Multiple concerning ingredients"},
            {"rating": "Avoid", "range": "0-19", "description": "High-risk, avoid this product"}
        ]
    }