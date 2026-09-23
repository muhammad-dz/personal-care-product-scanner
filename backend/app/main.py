import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import products, rating, reviews, scan
from app.config import CORS_ORIGINS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title="Personal Care Product Scanner",
    description="Look up cosmetics by barcode or label photo and rate their ingredients.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(scan.router)
app.include_router(rating.router)
app.include_router(reviews.router)


@app.get("/health")
def health():
    return {"status": "ok"}
