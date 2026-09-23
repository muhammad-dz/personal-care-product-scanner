import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# comma separated, e.g. "http://localhost:3000,https://scanner.example.com"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

REVIEWS_FILE = Path(os.getenv("REVIEWS_FILE", ROOT / "data" / "reviews" / "reviews.csv"))

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024
