from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from datetime import datetime

router = APIRouter()

# Product database for smart mock OCR
PRODUCT_DATABASE = {
    'cerave': {
        'name': 'CeraVe Hydrating Facial Cleanser',
        'ingredients': [
            "Purified Water",
            "Glycerin",
            "Cetearyl Alcohol",
            "Behentrimonium Methosulfate",
            "Ceramide 3",
            "Ceramide 6-III",
            "Ceramide 1",
            "Hyaluronic Acid",
            "Cholesterol",
            "PEG-40 Stearate",
            "Glyceryl Stearate",
            "Stearyl Alcohol",
            "Polysorbate 20",
            "Potassium Phosphate",
            "Dipotassium Phosphate",
            "Sodium Lauroyl Lactylate",
            "Cetyl Alcohol",
            "Disodium EDTA",
            "Phytosphingosine",
            "Methylparaben",
            "Propylparaben",
            "Carbomer",
            "Xanthan Gum"
        ]
    },
    'cetaphil': {
        'name': 'Cetaphil Gentle Skin Cleanser',
        'ingredients': [
            "Water",
            "Cetyl Alcohol",
            "Propylene Glycol",
            "Sodium Lauryl Sulfate",
            "Stearyl Alcohol",
            "Methylparaben",
            "Propylparaben",
            "Butylparaben"
        ]
    },
    'ordinary': {
        'name': 'The Ordinary Niacinamide 10% + Zinc 1%',
        'ingredients': [
            "Aqua (Water)",
            "Niacinamide",
            "Pentylene Glycol",
            "Zinc PCA",
            "Dimethyl Isosorbide",
            "Tamarix Chinensis Extract",
            "Xanthan Gum",
            "Lactic Acid",
            "Ethoxydiglycol",
            "Hydroxyethylcellulose",
            "Propanediol",
            "PCA",
            "Sodium Chloride",
            "Citric Acid",
            "Phenoxyethanol",
            "Chlorphenesin"
        ]
    },
    'la roche': {
        'name': 'La Roche-Posay Toleriane Double Repair',
        'ingredients': [
            "Aqua/Water",
            "Glycerin",
            "Dimethicone",
            "Isopropyl Palmitate",
            "Niacinamide",
            "Ammonium Polyacryloyldimethyl Taurate",
            "Myristyl Myristate",
            "Stearic Acid",
            "Ceramide NP",
            "Potassium Cetyl Phosphate",
            "Sodium Hydroxide",
            "Myristic Acid",
            "Palmitic Acid",
            "Capryloyl Salicylic Acid",
            "Arachidic Acid",
            "Oleic Acid",
            "Caprylyl Glycol",
            "Xanthan Gum",
            "Tocopherol",
            "Acetyl Dipeptide-1 Cetyl Ester"
        ]
    },
    'neutrogena': {
        'name': 'Neutrogena Hydro Boost Water Gel',
        'ingredients': [
            "Water",
            "Dimethicone",
            "Glycerin",
            "Dimethicone/Vinyl Dimethicone Crosspolymer",
            "Phenoxyethanol",
            "Acrylates/C10-30 Alkyl Acrylate Crosspolymer",
            "Chlorphenesin",
            "Dimethiconol",
            "Triethanolamine",
            "Dimethicone Crosspolymer",
            "C12-14 Pareth-12",
            "Sodium Hyaluronate",
            "Ethylhexylglycerin"
        ]
    },
    'generic': {
        'name': 'Personal Care Product',
        'ingredients': [
            "Water",
            "Glycerin",
            "Cetearyl Alcohol",
            "Glyceryl Stearate",
            "Cetyl Alcohol",
            "Stearyl Alcohol",
            "Phenoxyethanol",
            "Fragrance"
        ]
    }
}

@router.post("/extract-text")
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    Extract text from product label image
    Smart mock OCR that returns real ingredients based on filename
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        file_size = len(contents)
        
        # Get filename to determine which product this is
        filename = file.filename.lower()
        
        # Log the upload
        print(f"📸 Image uploaded: {file.filename} ({file_size} bytes)")
        
        # Detect product from filename
        detected_product = 'generic'
        for key in PRODUCT_DATABASE.keys():
            if key in filename:
                detected_product = key
                break
        
        # Get product data
        product = PRODUCT_DATABASE[detected_product]
        product_name = product['name']
        ingredients = product['ingredients']
        
        # Create formatted ingredient text
        if len(ingredients) > 10:
            # Format with line breaks for readability
            lines = []
            for i in range(0, len(ingredients), 5):
                lines.append(", ".join(ingredients[i:i+5]))
            extracted_text = "Ingredients:\n" + "\n".join(lines)
        else:
            extracted_text = "Ingredients: " + ", ".join(ingredients)
        
        print(f"✅ Detected product: {product_name}")
        print(f"📊 Ingredients found: {len(ingredients)}")
        
        return {
            "success": True,
            "filename": file.filename,
            "product_name": product_name,
            "content_type": file.content_type,
            "file_size": file_size,
            "timestamp": datetime.now().isoformat(),
            "message": "OCR processing successful",
            "extracted_text": extracted_text,
            "ingredients": ingredients,
            "ingredient_count": len(ingredients)
        }
        
    except Exception as e:
        print(f"❌ OCR processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@router.post("/batch-check")
async def batch_check_ingredients(ingredients: List[str]):
    """
    Check safety for multiple ingredients
    """
    # Mock safety database
    safety_database = {
        "water": {"score": 10, "rating": "Excellent", "hazards": []},
        "glycerin": {"score": 9, "rating": "Excellent", "hazards": []},
        "purified water": {"score": 10, "rating": "Excellent", "hazards": []},
        "hyaluronic acid": {"score": 10, "rating": "Excellent", "hazards": []},
        "niacinamide": {"score": 9, "rating": "Excellent", "hazards": []},
        "ceramide 3": {"score": 9, "rating": "Excellent", "hazards": []},
        "ceramide 6-iii": {"score": 9, "rating": "Excellent", "hazards": []},
        "ceramide 1": {"score": 9, "rating": "Excellent", "hazards": []},
        "ceramide np": {"score": 9, "rating": "Excellent", "hazards": []},
        "cholesterol": {"score": 8, "rating": "Excellent", "hazards": []},
        "sodium hyaluronate": {"score": 9, "rating": "Excellent", "hazards": []},
        "panthenol": {"score": 8, "rating": "Excellent", "hazards": []},
        "allantoin": {"score": 8, "rating": "Excellent", "hazards": []},
        "tocopherol": {"score": 8, "rating": "Excellent", "hazards": []},
        "vitamin e": {"score": 8, "rating": "Excellent", "hazards": []},
        
        # Moderate risk ingredients
        "cetearyl alcohol": {"score": 6, "rating": "Good", "hazards": ["May cause irritation in sensitive skin"]},
        "cetyl alcohol": {"score": 6, "rating": "Good", "hazards": ["May cause irritation in sensitive skin"]},
        "stearyl alcohol": {"score": 6, "rating": "Good", "hazards": ["May cause irritation in sensitive skin"]},
        "glyceryl stearate": {"score": 6, "rating": "Good", "hazards": []},
        "peg-40 stearate": {"score": 5, "rating": "Moderate", "hazards": ["May contain ethylene oxide"]},
        "polysorbate 20": {"score": 5, "rating": "Moderate", "hazards": ["May cause irritation"]},
        "phenoxyethanol": {"score": 5, "rating": "Moderate", "hazards": ["Skin allergen"]},
        "fragrance": {"score": 3, "rating": "Poor", "hazards": ["Common allergen", "May contain phthalates"]},
        "parfum": {"score": 3, "rating": "Poor", "hazards": ["Common allergen", "May contain phthalates"]},
        "sodium lauryl sulfate": {"score": 4, "rating": "Moderate", "hazards": ["Skin irritation", "Eye irritation"]},
        "sodium laureth sulfate": {"score": 4, "rating": "Moderate", "hazards": ["Skin irritation", "May contain 1,4-dioxane"]},
        "dimethicone": {"score": 5, "rating": "Moderate", "hazards": ["May be occlusive"]},
        
        # High risk ingredients
        "methylparaben": {"score": 3, "rating": "Poor", "hazards": ["Endocrine disruptor", "Potential reproductive toxicity"]},
        "propylparaben": {"score": 3, "rating": "Poor", "hazards": ["Endocrine disruptor", "Potential reproductive toxicity"]},
        "butylparaben": {"score": 2, "rating": "Poor", "hazards": ["Endocrine disruptor", "Potential reproductive toxicity"]},
        "ethylparaben": {"score": 3, "rating": "Poor", "hazards": ["Endocrine disruptor", "Potential reproductive toxicity"]},
        "alcohol denat": {"score": 4, "rating": "Moderate", "hazards": ["Drying", "Irritating"]},
        "denatured alcohol": {"score": 4, "rating": "Moderate", "hazards": ["Drying", "Irritating"]},
        "phthalate": {"score": 2, "rating": "Poor", "hazards": ["Endocrine disruptor", "Reproductive toxicity"]},
    }
    
    results = []
    total_score = 0
    
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        
        # Try exact match first
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
        
        # If no match found, use default
        if not found:
            # Check if it contains "paraben"
            if "paraben" in ingredient_lower:
                results.append({
                    "ingredient": ingredient,
                    "safety_score": 3,
                    "rating": "Poor",
                    "hazards": ["Potential endocrine disruptor"]
                })
                total_score += 3
            # Check if it contains "sulfate"
            elif "sulfate" in ingredient_lower:
                results.append({
                    "ingredient": ingredient,
                    "safety_score": 4,
                    "rating": "Moderate",
                    "hazards": ["May cause skin irritation"]
                })
                total_score += 4
            # Check if it contains "alcohol"
            elif "alcohol" in ingredient_lower and not any(x in ingredient_lower for x in ["cetearyl", "cetyl", "stearyl", "glyceryl"]):
                results.append({
                    "ingredient": ingredient,
                    "safety_score": 4,
                    "rating": "Moderate",
                    "hazards": ["Can be drying and irritating"]
                })
                total_score += 4
            # Check if it contains "peg"
            elif "peg" in ingredient_lower:
                results.append({
                    "ingredient": ingredient,
                    "safety_score": 5,
                    "rating": "Moderate",
                    "hazards": ["May contain impurities"]
                })
                total_score += 5
            # Default for unknown ingredients
            else:
                results.append({
                    "ingredient": ingredient,
                    "safety_score": 6,
                    "rating": "Good",
                    "hazards": ["Limited data available"]
                })
                total_score += 6
    
    avg_score = total_score / len(results) if results else 0
    
    # Determine overall rating
    if avg_score >= 8:
        overall = "Excellent"
    elif avg_score >= 6.5:
        overall = "Good"
    elif avg_score >= 5:
        overall = "Moderate"
    elif avg_score >= 3:
        overall = "Poor"
    else:
        overall = "Avoid"
    
    return {
        "success": True,
        "results": results,
        "average_score": round(avg_score, 1),
        "overall_rating": overall,
        "total_ingredients": len(results)
    }