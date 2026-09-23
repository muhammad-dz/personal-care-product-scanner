"""Generate a synthetic review dataset for local development.

The reviews are built from templates, so they are only useful for exercising
the pipeline, not for drawing conclusions about real products. Product names
are made up on purpose.

    python scripts/generate_reviews.py --count 1000 --seed 42
"""
import argparse
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

PRODUCTS = [
    "Hydrating Gel Cleanser",
    "Barrier Repair Moisturiser",
    "Niacinamide 10% Serum",
    "Daily Mineral SPF 30",
    "Gentle Foaming Face Wash",
    "Overnight Retinol Cream",
    "Salicylic Acid Toner",
    "Fragrance-Free Body Lotion",
]

TEMPLATES = {
    5: [
        "Love this, my skin feels amazing after a week.",
        "So gentle and it actually works. Will buy again.",
        "Best moisturiser I've used, no irritation at all.",
        "My skin has never looked better, really happy with it.",
        "Perfect for my sensitive skin, no reaction whatsoever.",
    ],
    4: [
        "Really good product but a bit pricey.",
        "Does what it says. Nice texture and absorbs quickly.",
        "Works well, took a few weeks to see results.",
        "Good overall, but I've used better.",
    ],
    3: [
        "It's okay, nothing special.",
        "Average. Expected more based on the hype.",
        "Works fine but I probably won't repurchase.",
    ],
    2: [
        "Not great, it left my skin feeling dry and tight.",
        "Disappointed, gave me a couple of breakouts.",
        "Caused some redness around my nose.",
        "Didn't see any difference and it stings a little.",
    ],
    1: [
        "Terrible, gave me a rash across my cheeks.",
        "Broke me out badly, had to stop using it.",
        "Burning and irritation straight away.",
        "Had an allergic reaction, avoid if you're sensitive.",
    ],
}

RATING_WEIGHTS = {5: 40, 4: 30, 3: 15, 2: 10, 1: 5}


def generate(count: int, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    start = date(2026, 1, 1)
    rows = []
    for _ in range(count):
        rating = rng.choices(list(RATING_WEIGHTS), weights=RATING_WEIGHTS.values())[0]
        rows.append({
            "product_name": rng.choice(PRODUCTS),
            "rating": rating,
            "text": rng.choice(TEMPLATES[rating]),
            "date": (start + timedelta(days=rng.randrange(180))).isoformat(),
            "source": "synthetic",
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("data/reviews/reviews.csv"))
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df = generate(args.count, args.seed)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} reviews to {args.out}")


if __name__ == "__main__":
    main()
