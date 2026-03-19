from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import cv2
import numpy as np
from PIL import Image
import io
from pyzbar.pyzbar import decode
import requests

router = APIRouter()

@router.post("/extract-text")
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    Extract barcode from product label image and lookup product
    """
    try:
        # Read the uploaded image
        contents = await file.read()
        
        # Convert to image for barcode reading
        image = Image.open(io.BytesIO(contents))
        
        # Convert PIL Image to numpy array for OpenCV
        open_cv_image = np.array(image)
        
        # Convert RGB to BGR (OpenCV format)
        if len(open_cv_image.shape) == 3:
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        
        # Try to decode barcodes
        barcodes = decode(open_cv_image)
        
        if not barcodes:
            return {
                "success": False,
                "filename": file.filename,
                "message": "No barcode found in image. Please ensure the barcode is clearly visible.",
                "ingredients": []
            }
        
        # Get the first barcode
        barcode = barcodes[0]
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        
        print(f"✅ Found barcode: {barcode_data} (Type: {barcode_type})")
        
        # Now lookup this product using Open Beauty Facts
        lookup_url = f"https://world.openbeautyfacts.org/api/v2/product/{barcode_data}.json"
        response = requests.get(lookup_url, timeout=10)
        
        if response.status_code != 200:
            return {
                "success": False,
                "filename": file.filename,
                "barcode": barcode_data,
                "message": "Product not found in database",
                "ingredients": []
            }
        
        data = response.json()
        
        if data.get("status") == 1:
            product = data.get("product", {})
            
            # Extract ingredients
            ingredients_text = product.get("ingredients_text", "")
            ingredients_list = []
            
            # Try to get structured ingredients
            if "ingredients" in product:
                for ing in product.get("ingredients", []):
                    name = ing.get("text", ing.get("id", ""))
                    if name:
                        ingredients_list.append(name)
            
            # Fallback to text parsing
            if not ingredients_list and ingredients_text:
                ingredients_list = [i.strip() for i in ingredients_text.split(",") if i.strip()]
            
            return {
                "success": True,
                "filename": file.filename,
                "barcode": barcode_data,
                "product_name": product.get("product_name", "Unknown Product"),
                "brands": product.get("brands", "Unknown Brand"),
                "extracted_text": ingredients_text,
                "ingredients": ingredients_list,
                "message": "Product found via barcode scan"
            }
        else:
            return {
                "success": False,
                "filename": file.filename,
                "barcode": barcode_data,
                "message": "Product not found in database",
                "ingredients": []
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/batch-check")
async def batch_check_ingredients(ingredients: List[str]):
    """
    Check safety for multiple ingredients
    """
    # Mock safety database (keep your existing one)
    safety_database = {
        "water": {"score": 10, "rating": "Excellent", "hazards": []},
        "glycerin": {"score": 9, "rating": "Excellent", "hazards": []},
        "hyaluronic acid": {"score": 10, "rating": "Excellent", "hazards": []},
        "niacinamide": {"score": 9, "rating": "Excellent", "hazards": []},
        "ceramide": {"score": 9, "rating": "Excellent", "hazards": []},
        "methylparaben": {"score": 3, "rating": "Poor", "hazards": ["Endocrine disruptor", "Potential reproductive toxicity"]},
        "propylparaben": {"score": 3, "rating": "Poor", "hazards": ["Endocrine disruptor", "Potential reproductive toxicity"]},
        "sodium lauryl sulfate": {"score": 4, "rating": "Moderate", "hazards": ["Skin irritation", "Eye irritation"]},
        "sodium laureth sulfate": {"score": 4, "rating": "Moderate", "hazards": ["Skin irritation", "May contain 1,4-dioxane"]},
        "fragrance": {"score": 3, "rating": "Poor", "hazards": ["Common allergen", "May contain phthalates"]},
        "parfum": {"score": 3, "rating": "Poor", "hazards": ["Common allergen", "May contain phthalates"]},
    }
    
    results = []
    total_score = 0
    
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        found = False
        
        for key, data in safety_database.items():
            if key in ingredient_lower:
                results.append({
                    "ingredient": ingredient,
                    "safety_score": data["score"],
                    "rating": data["rating"],
                    "hazards": data["hazards"]
                })
                total_score += data["score"]
                found = True
                break
        
        if not found:
            # Default for unknown ingredients
            results.append({
                "ingredient": ingredient,
                "safety_score": 6,
                "rating": "Good",
                "hazards": ["Limited data available"]
            })
            total_score += 6
    
    avg_score = total_score / len(results) if results else 0
    
    if avg_score >= 8:
        overall = "Excellent"
    elif avg_score >= 6.5:
        overall = "Good"
    elif avg_score >= 5:
        overall = "Moderate"
    else:
        overall = "Poor"
    
    return {
        "success": True,
        "results": results,
        "average_score": round(avg_score, 1),
        "overall_rating": overall
    }