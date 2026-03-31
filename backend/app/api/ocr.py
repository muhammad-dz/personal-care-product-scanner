"""
OCR API Endpoint
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Product database for smart mock OCR
PRODUCT_DATABASE = {
    'cerave': {
        'name': 'CeraVe Hydrating Facial Cleanser',
        'ingredients': [
            "Purified Water", "Glycerin", "Cetearyl Alcohol", "Behentrimonium Methosulfate",
            "Ceramide 3", "Ceramide 6-III", "Ceramide 1", "Hyaluronic Acid", "Cholesterol",
            "PEG-40 Stearate", "Glyceryl Stearate", "Stearyl Alcohol", "Polysorbate 20",
            "Potassium Phosphate", "Dipotassium Phosphate", "Sodium Lauroyl Lactylate",
            "Cetyl Alcohol", "Disodium EDTA", "Phytosphingosine", "Methylparaben",
            "Propylparaben", "Carbomer", "Xanthan Gum"
        ]
    },
    'cetaphil': {
        'name': 'Cetaphil Gentle Skin Cleanser',
        'ingredients': [
            "Water", "Cetyl Alcohol", "Propylene Glycol", "Sodium Lauryl Sulfate",
            "Stearyl Alcohol", "Methylparaben", "Propylparaben", "Butylparaben"
        ]
    },
    'ordinary': {
        'name': 'The Ordinary Niacinamide 10% + Zinc 1%',
        'ingredients': [
            "Aqua (Water)", "Niacinamide", "Pentylene Glycol", "Zinc PCA",
            "Dimethyl Isosorbide", "Tamarix Chinensis Extract", "Xanthan Gum",
            "Lactic Acid", "Ethoxydiglycol", "Hydroxyethylcellulose", "Propanediol",
            "PCA", "Sodium Chloride", "Citric Acid", "Phenoxyethanol", "Chlorphenesin"
        ]
    },
    'generic': {
        'name': 'Personal Care Product',
        'ingredients': [
            "Water", "Glycerin", "Cetearyl Alcohol", "Glyceryl Stearate",
            "Cetyl Alcohol", "Stearyl Alcohol", "Phenoxyethanol", "Fragrance"
        ]
    }
}

@router.post("/extract-text")
async def extract_text_from_image(file: UploadFile = File(...)):
    """Extract ingredients from product label image"""
    try:
        contents = await file.read()
        file_size = len(contents)
        filename = file.filename.lower()
        
        print(f"Image uploaded: {file.filename} ({file_size} bytes)")
        
        # Detect product from filename
        detected = 'generic'
        for key in PRODUCT_DATABASE.keys():
            if key in filename:
                detected = key
                break
        
        product = PRODUCT_DATABASE[detected]
        
        print(f"Detected product: {product['name']}")
        print(f"Ingredients found: {len(product['ingredients'])}")
        
        return {
            "success": True,
            "filename": file.filename,
            "product_name": product['name'],
            "ingredients": product['ingredients'],
            "extracted_text": "Ingredients: " + ", ".join(product['ingredients'][:8]) + "...",
            "ingredient_count": len(product['ingredients']),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"OCR failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

@router.post("/batch-check")
async def batch_check_ingredients(ingredients: List[str]):
    """Check safety for ingredients"""
    safety_database = {
        "water": {"score": 10, "rating": "Excellent", "hazards": []},
        "glycerin": {"score": 9, "rating": "Excellent", "hazards": []},
        "hyaluronic acid": {"score": 10, "rating": "Excellent", "hazards": []},
        "niacinamide": {"score": 9, "rating": "Excellent", "hazards": []},
        "ceramide": {"score": 9, "rating": "Excellent", "hazards": []},
        "methylparaben": {"score": 3, "rating": "Poor", "hazards": ["Endocrine disruptor"]},
        "propylparaben": {"score": 3, "rating": "Poor", "hazards": ["Endocrine disruptor"]},
        "sodium lauryl sulfate": {"score": 4, "rating": "Moderate", "hazards": ["Skin irritation"]},
        "sodium laureth sulfate": {"score": 4, "rating": "Moderate", "hazards": ["Skin irritation"]},
        "fragrance": {"score": 3, "rating": "Poor", "hazards": ["Common allergen"]},
        "alcohol": {"score": 5, "rating": "Moderate", "hazards": ["Can be drying"]},
    }
    
    results = []
    total = 0
    
    for ing in ingredients:
        ing_lower = ing.lower()
        found = False
        for key, data in safety_database.items():
            if key in ing_lower:
                results.append({"ingredient": ing, **data})
                total += data["score"]
                found = True
                break
        if not found:
            results.append({
                "ingredient": ing,
                "score": 5,
                "rating": "Moderate",
                "hazards": ["Limited data available"]
            })
            total += 5
    
    avg = total / len(results) if results else 0
    
    return {
        "success": True,
        "results": results,
        "average_score": round(avg, 1),
        "overall_rating": "Good" if avg >= 6 else "Moderate" if avg >= 4 else "Poor",
        "total_ingredients": len(results)
    }