# Personal Care Product Safety Scanner

[![CI](https://github.com/muhammad-dz/personal-care-product-scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/muhammad-dz/personal-care-product-scanner/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)
![NLTK](https://img.shields.io/badge/NLP-NLTK%20VADER-154F5B)

A full-stack app that looks up a cosmetic or skincare product, rates its
ingredient list for safety, and runs sentiment analysis over product reviews
to surface common complaints (rashes, breakouts, dryness and so on).

![Scanner screenshot — ingredient list with an overall safety rating and a per-ingredient breakdown](docs/screenshot-scan.png)

## Why I built this

Ingredient lists on skincare products are long and hard to read, and reviews
are scattered across sites. I wanted one place to answer two questions:
*what's actually in this product?* and *what do people who used it say?*

## How it works

```
 barcode / label image
          │
          ▼
 ┌──────────────────┐     ┌──────────────────────────┐     ┌────────────────────┐
 │ 1. Ingest         │ ──▶ │ 2. Enrich                 │ ──▶ │ 3. Rate             │
 │ barcode or label  │     │ Open Beauty Facts REST API│     │ rule-based scoring  │
 │ upload            │     │ → product + ingredients   │     │ 0–100 + explanation │
 └──────────────────┘     └──────────────────────────┘     └────────────────────┘

 review dataset (CSV) ──▶ 4. NLP: VADER sentiment + keyword issue extraction ──▶ dashboard
```

1. **Ingest:** look up a product by barcode, or upload a label image.
2. **Enrich:** `backend/app/services/openbeautyfacts.py` calls the
   [Open Beauty Facts](https://world.openbeautyfacts.org/) API and normalises
   the ingredient list (structured list first, falling back to parsing the
   free-text field).
3. **Rate:** `backend/app/services/rating_algorithm.py` starts every product at
   a baseline of 70. It deducts points for flagged ingredients (parabens,
   formaldehyde releasers, sulfates, fragrance and others), weighted by
   severity and category, and adds points for beneficial ones (ceramides,
   niacinamide, hyaluronic acid and others). The score is capped per product
   type and mapped to a band: Excellent, Good, Moderate, Poor or Avoid.
   Every deduction is returned with a reason, so the score can be explained.
4. **NLP:** `nlp/sentiment_analyzer.py` classifies reviews with NLTK's VADER
   and tags reported issues with keyword matching. The results feed the
   sentiment dashboard.

### Current limitations (being upfront)

- **The OCR step is a stub.** `POST /api/ocr/extract-text` accepts an image,
  but it returns a known ingredient list based on the filename. It doesn't
  read the pixels yet. Adding real OCR (Tesseract or a cloud vision API) is
  first on the roadmap. Barcode lookup uses real live data.
- **The review data is synthetic.** `scraper/download_beauty_dataset.py`
  generates a synthetic review set for development. If no processed results
  file exists, the sentiment endpoint returns sample figures. See
  [`docs/ethics.md`](docs/ethics.md) for why the project doesn't scrape
  review sites.
- The ingredient ratings are a heuristic for learning purposes, **not medical
  or dermatological advice.**

## Tech stack

- **Backend:** Python 3.11, FastAPI, httpx (async), Pydantic
- **NLP / data:** NLTK (VADER), pandas
- **Frontend:** React, React Router, axios
- **Testing:** pytest (41 tests), FastAPI `TestClient`, `httpx.MockTransport`
- **CI:** GitHub Actions runs the Python tests and builds the frontend on
  every push

## Project structure

```
personal-care-product-scanner/
├── backend/app/
│   ├── api/          # FastAPI routers: ocr, rating, sentiment
│   ├── services/     # Open Beauty Facts client, rating algorithm
│   └── main.py       # App entry point, barcode lookup endpoint
├── nlp/              # Sentiment analyser + analysis scripts
├── scraper/          # Dataset generation / review collection scripts
├── frontend/src/     # React UI: scanner page, sentiment dashboard
├── tests/            # pytest suite
└── docs/             # Screenshots, ethics notes
```

## Running locally

**Backend** (http://localhost:8000, interactive API docs at `/docs`):

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate    Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon
uvicorn app.main:app --reload
```

**Frontend** (http://localhost:3000):

```bash
cd frontend
npm install
npm start
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m nltk.downloader vader_lexicon
pytest -v
```

The suite covers each stage of the pipeline independently:

| File | What it checks |
|------|----------------|
| `tests/test_openbeautyfacts.py` | API client parsing, text fallback, not-found, HTTP and network errors (the HTTP layer is mocked, so there are no real network calls) |
| `tests/test_rating_algorithm.py` | Score bounds, rating bands, product-type caps, case-insensitivity, overlapping ingredient names, batch ranking |
| `tests/test_sentiment_analyzer.py` | Positive/negative/neutral classification, issue extraction, report aggregation |
| `tests/test_api.py` | Endpoints end to end through FastAPI's `TestClient`, including request validation |

The tests found two real bugs, both now fixed and covered by regression
tests:

- "Methylparaben" also matched the "ethylparaben" rule as a substring, so it
  was penalised twice.
- The frontend sent `{"ingredients": [...]}` to `/api/ocr/batch-check`, but
  the endpoint expected a bare list, so every safety check from the UI failed
  with a 422 error.

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/beauty/lookup/{barcode}` | Look up a product on Open Beauty Facts and attach a safety rating |
| POST | `/api/rating/rate-product` | Rate an ingredient list |
| GET  | `/api/rating/ingredient-info/{name}` | Explain why one ingredient is flagged or beneficial |
| POST | `/api/ocr/batch-check` | Per-ingredient safety breakdown |
| POST | `/api/ocr/extract-text` | Label image upload (stubbed OCR, see limitations) |
| GET  | `/api/sentiment/summary` | Aggregated review sentiment and top issues |

## Roadmap

- Real OCR for label images (Tesseract / cloud vision)
- Replace the synthetic reviews with a properly licensed public dataset
- Move the hard-coded ingredient rules into a data file with cited sources
- Deploy the backend and frontend with a live demo link
