"""
Rating API Endpoints with Skin Type Personalization
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

from app.services.rating_algorithm import ProductRatingAlgorithm, BatchRatingProcessor

algorithm = ProductRatingAlgorithm()
batch_processor = BatchRatingProcessor()

class PersonalizedRatingRequest(BaseModel):
    product_name: str
    ingredients: List[str]
    product_type: str = "unknown"
    skin_type: str = "normal"
    concerns: List[str] = []

class BatchPersonalizedRequest(BaseModel):
    products: List[Dict[str, Any]]
    skin_type: str = "normal"
    concerns: List[str] = []

@router.post("/rate-product-personalized")
async def rate_product_personalized(request: PersonalizedRatingRequest):
    """Rate a product with skin type personalization"""
    try:
        result = algorithm.calculate_product_rating(
            product_name=request.product_name,
            ingredients=request.ingredients,
            product_type=request.product_type,
            skin_type=request.skin_type,
            concerns=request.concerns
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Rating error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rate-batch-personalized")
async def rate_batch_personalized(request: BatchPersonalizedRequest):
    """Rate multiple products with personalization"""
    try:
        results = batch_processor.rate_products(
            request.products, 
            request.skin_type, 
            request.concerns
        )
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"Batch rating error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skin-types")
async def get_skin_types():
    """Get available skin types and their descriptions"""
    algorithm = ProductRatingAlgorithm()
    return {
        "success": True,
        "skin_types": {
            "normal": algorithm.skin_type_adjustments["normal"]["description"],
            "dry": algorithm.skin_type_adjustments["dry"]["description"],
            "oily": algorithm.skin_type_adjustments["oily"]["description"],
            "combination": algorithm.skin_type_adjustments["combination"]["description"],
            "sensitive": algorithm.skin_type_adjustments["sensitive"]["description"]
        }
    }

@router.get("/concerns")
async def get_concerns():
    """Get available skin concerns"""
    algorithm = ProductRatingAlgorithm()
    return {
        "success": True,
        "concerns": list(algorithm.concern_adjustments.keys())
    }

@router.get("/rating-categories")
async def get_rating_categories():
    """Get the rating categories and their score ranges"""
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