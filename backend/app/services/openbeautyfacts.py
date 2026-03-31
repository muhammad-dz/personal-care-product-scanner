"""
Open Beauty Facts API Integration Service
"""
import requests
import logging

logger = logging.getLogger(__name__)

class OpenBeautyFactsClient:
    """Client for Open Beauty Facts API"""
    
    def __init__(self):
        self.BASE_URL = "https://world.openbeautyfacts.org/api/v2"
        self.UNIVERSAL_URL = "https://world.openfoodfacts.org/api/v2/product"
        self.USER_AGENT = "PersonalCareProductScanner/1.0"
    
    async def get_product_by_barcode(self, barcode: str):
        """Fetch product by barcode"""
        url = f"{self.BASE_URL}/product/{barcode}.json"
        print(f"Fetching: {url}")
        
        try:
            response = requests.get(
                url,
                headers={"User-Agent": self.USER_AGENT},
                timeout=10
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
    
    async def universal_scan(self, barcode: str):
        """Universal scanner fallback"""
        return await self.get_product_by_barcode(barcode)