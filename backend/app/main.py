"""
Personal Care Product Safety Scanner - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ocr, sentiment, rating
from app.services.openbeautyfacts import OpenBeautyFactsClient
from app.services.rating_algorithm import ProductRatingAlgorithm
import uvicorn

# Initialize rating algorithm
rating_algorithm = ProductRatingAlgorithm()

app = FastAPI(
    title="Personal Care Product Safety Scanner API",
    description="API for scanning personal care products and analyzing safety & reviews",
    version="1.0.0"
)

# CORS middleware - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(sentiment.router, prefix="/api", tags=["Sentiment"])
app.include_router(rating.router, prefix="/api/rating", tags=["Rating"])


@app.get("/api/beauty/lookup/{barcode}")
async def lookup_beauty_product(barcode: str):
    """Fetch cosmetic product by barcode and calculate safety rating"""
    client = OpenBeautyFactsClient()
    result = await client.get_product_by_barcode(barcode)
    
    # If product found, calculate rating
    if result.get('success'):
        ingredients = result.get('ingredients_list', [])
        product_name = result.get('product_name', 'Unknown')
        
        # Calculate rating using our algorithm
        rating_result = rating_algorithm.calculate_product_rating(
            product_name=product_name,
            ingredients=ingredients,
            product_type="unknown"
        )
        
        # Add rating data to the result
        result['rating_data'] = rating_result
    
    return result


@app.get("/api/beauty/universal/{barcode}")
async def universal_product_scan(barcode: str):
    """Universal product scanner"""
    client = OpenBeautyFactsClient()
    result = await client.universal_scan(barcode)
    return result


@app.get("/api/test/{barcode}")
async def test_barcode(barcode: str):
    """Test endpoint to verify API is working"""
    return {"message": f"API is working! Barcode: {barcode}"}


@app.get("/")
async def root():
    return {"message": "Personal Care Product Safety Scanner API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)