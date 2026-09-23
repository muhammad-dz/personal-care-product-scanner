# Ethics & data notes

## Review data

Many retail and review sites forbid automated scraping in their Terms of
Service. So this project:

- uses a **synthetic review dataset** (`scraper/download_beauty_dataset.py`)
  during development
- keeps the scraper scripts in `scraper/` as experiments only; they are not
  part of the running app and shouldn't be pointed at sites whose terms
  prohibit it
- would move to a properly licensed public dataset for any real use

The review data has no reviewer names or personal information.

## Product data

Product and ingredient data comes from
[Open Beauty Facts](https://world.openbeautyfacts.org/), an open database
licensed under the Open Database License (ODbL). Requests identify the app
with a custom `User-Agent`, as the project asks.

## Safety ratings are not medical advice

The ingredient scores are a rule-based heuristic built for learning. Whether
an ingredient is a concern often depends on its concentration, the product
type and the person using it. The app says an ingredient is "flagged", not
that it's "unsafe". Anyone with skin conditions or allergies should rely on
a dermatologist or pharmacist, not this tool.
