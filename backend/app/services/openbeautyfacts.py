"""
Open Beauty Facts API Integration Service
Simplified version with better error handling
"""
import httpx
from typing import Dict, Any

class OpenBeautyFactsClient:
    """Client for Open Beauty Facts API"""
    
    def __init__(self):
        self.BASE_URL = "https://world.openbeautyfacts.org/api/v2"
        self.UNIVERSAL_URL = "https://world.openfoodfacts.org/api/v2/product"
        self.USER_AGENT = "PersonalCareProductScanner/1.0"
    
    async def get_product_by_barcode(self, barcode: str) -> Dict[str, Any]:
        """Fetch product by barcode"""
        url = f"{self.BASE_URL}/product/{barcode}.json"
        print(f"Fetching: {url}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.USER_AGENT},
                    timeout=10.0,
                    follow_redirects=True
                )
                
                if response.status_code != 200:
                    return {
                        "success": False, 
                        "error": f"HTTP {response.status_code}",
                        "barcode": barcode
                    }
                
                data = response.json()
                
                if data.get("status") == 1:
                    product = data.get("product", {})
                    
                    # Extract ingredients
                    ingredients_text = product.get("ingredients_text", "")
                    ingredients_list = []
                    
                    if "ingredients" in product:
                        for ing in product.get("ingredients", []):
                            name = ing.get("text", ing.get("id", ""))
                            if name:
                                ingredients_list.append(name)
                    
                    if not ingredients_list and ingredients_text:
                        ingredients_list = [i.strip() for i in ingredients_text.split(",") if i.strip()]
                    
                    return {
                        "success": True,
                        "source": "Open Beauty Facts",
                        "barcode": product.get("code", barcode),
                        "product_name": product.get("product_name", "Unknown"),
                        "brands": product.get("brands", "Unknown"),
                        "ingredients_text": ingredients_text,
                        "ingredients_list": ingredients_list or product.get("ingredients_tags", []),
                        "image_url": product.get("image_url", "")
                    }
                else:
                    return {
                        "success": False, 
                        "error": "Product not found",
                        "barcode": barcode
                    }
                    
            except Exception as e:
                print(f"Error: {e}")
                return {
                    "success": False, 
                    "error": str(e),
                    "barcode": barcode
                }
    
    async def universal_scan(self, barcode: str) -> Dict[str, Any]:
        """Try universal scanner as fallback"""
        url = f"{self.UNIVERSAL_URL}/{barcode}.json"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    params={"product_type": "all"},
                    headers={"User-Agent": self.USER_AGENT},
                    timeout=10.0
                )
                
                data = response.json()
                
                if data.get("status") == 1:
                    product = data.get("product", {})
                    return {
                        "success": True,
                        "source": "Open Food Facts",
                        "barcode": barcode,
                        "product_name": product.get("product_name", "Unknown"),
                        "brands": product.get("brands", "Unknown"),
                        "ingredients_text": product.get("ingredients_text", ""),
                        "ingredients_list": []
                    }
                else:
                    return {"success": False, "error": "Not found in any database"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}