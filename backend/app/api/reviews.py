from fastapi import APIRouter, HTTPException

from app.config import REVIEWS_FILE
from app.services.sentiment import summarise_file

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

_cache = {}


@router.get("/summary")
def summary():
    if not REVIEWS_FILE.exists():
        raise HTTPException(404, "No review data found. Run scripts/generate_reviews.py first.")

    # re-analyse only when the file changes
    modified = REVIEWS_FILE.stat().st_mtime
    if _cache.get("modified") != modified:
        _cache["data"] = summarise_file(REVIEWS_FILE)
        _cache["modified"] = modified
    return _cache["data"]
