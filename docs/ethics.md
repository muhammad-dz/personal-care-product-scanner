# Ethics & data notes

## Review data

Most retail and review sites ban automated scraping in their terms of
service, so this project doesn't scrape any of them. The dashboard runs on a
synthetic dataset from `scripts/generate_reviews.py`:

- the reviews come from templates, not real customers
- the product names are made up, so no real brand gets fake reviews attached to it
- every row is marked `source: synthetic`, and the dashboard shows a notice when it's using that data

For real use, this would move to a properly licensed public review dataset.

## Product data

Product and ingredient data comes from
[Open Beauty Facts](https://world.openbeautyfacts.org/) and
[Open Food Facts](https://world.openfoodfacts.org/), both open databases
under the Open Database License (ODbL). Requests identify the app with a
custom `User-Agent`, as those projects ask.

## Ratings are not medical advice

The ingredient scores are a rule-based heuristic I wrote while learning.
Whether an ingredient is a concern depends on its concentration, the
product type and the person using it, and none of that is modelled. The app
says an ingredient is "flagged", not that it's "unsafe". Anyone with skin
conditions or allergies should speak to a dermatologist or pharmacist.

## Label photos

Uploaded photos are processed in memory and never saved.
