from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ocr, sentiment  # Combined import
from app.services.openbeautyfacts import OpenBeautyFactsClient
import uvicorn

app = FastAPI(
    title="Personal Care Product Safety Scanner API",
    description="API for scanning personal care products and analyzing safety & reviews",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(sentiment.router, prefix="/api", tags=["Sentiment"])

# Direct beauty lookup endpoint
@app.get("/api/beauty/lookup/{barcode}")
async def lookup_beauty_product(barcode: str):
    """Fetch cosmetic product by barcode"""
    client = OpenBeautyFactsClient()
    result = await client.get_product_by_barcode(barcode)
    return result

# Universal scan endpoint
@app.get("/api/beauty/universal/{barcode}")
async def universal_product_scan(barcode: str):
    """Universal product scanner"""
    client = OpenBeautyFactsClient()
    result = await client.universal_scan(barcode)
    return result

# Test endpoint
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