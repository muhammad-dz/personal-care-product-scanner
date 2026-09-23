import re
from collections import Counter
from pathlib import Path

import nltk
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer

# VADER's usual cut-offs for calling a text positive or negative
POSITIVE = 0.05
NEGATIVE = -0.05

ISSUE_KEYWORDS = {
    "rash": ["rash", "redness", "itchy", "itching", "irritation", "irritated", "burning", "burned"],
    "acne": ["acne", "breakout", "breakouts", "broke out", "pimple", "pimples"],
    "dryness": ["dry", "dryness", "flaky", "peeling", "tight"],
    "oiliness": ["oily", "greasy"],
    "sensitivity": ["sensitive", "allergic", "reaction", "sting", "stinging"],
}

_ISSUE_PATTERNS = {
    issue: re.compile(r"\b(" + "|".join(map(re.escape, words)) + r")\b", re.IGNORECASE)
    for issue, words in ISSUE_KEYWORDS.items()
}


def _load_vader() -> SentimentIntensityAnalyzer:
    try:
        return SentimentIntensityAnalyzer()
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)
        return SentimentIntensityAnalyzer()


class ReviewAnalyzer:
    def __init__(self):
        self.vader = _load_vader()

    def sentiment(self, text: str):
        compound = self.vader.polarity_scores(text)["compound"]
        if compound >= POSITIVE:
            label = "positive"
        elif compound <= NEGATIVE:
            label = "negative"
        else:
            label = "neutral"
        return label, compound

    @staticmethod
    def issues(text: str) -> list:
        return [issue for issue, pattern in _ISSUE_PATTERNS.items() if pattern.search(text)]

    def analyse(self, reviews: pd.DataFrame, min_length: int = 10) -> pd.DataFrame:
        rows = []
        for review in reviews.itertuples(index=False):
            text = str(getattr(review, "text", "") or "")
            if len(text) < min_length:
                continue
            label, compound = self.sentiment(text)
            rating = getattr(review, "rating", None)
            # "no irritation at all" shouldn't count as an irritation report, so
            # skip happy reviews (VADER alone gets fooled by the word "irritation")
            happy = label == "positive" or (pd.notna(rating) and rating >= 4)
            issues = [] if happy else self.issues(text)
            rows.append({
                "product_name": getattr(review, "product_name", None),
                "rating": rating,
                "sentiment": label,
                "score": compound,
                "issues": issues,
            })
        return pd.DataFrame(rows, columns=["product_name", "rating", "sentiment", "score", "issues"])

    @staticmethod
    def summarise(analysed: pd.DataFrame) -> dict:
        total = len(analysed)
        counts = analysed["sentiment"].value_counts().to_dict()
        issues = Counter(issue for row in analysed["issues"] for issue in row)

        def pct(n):
            return round(100 * n / total, 1) if total else 0.0

        return {
            "total_reviews": total,
            "sentiment": {
                label: {"count": int(counts.get(label, 0)), "percent": pct(counts.get(label, 0))}
                for label in ("positive", "neutral", "negative")
            },
            "average_score": round(float(analysed["score"].mean()), 3) if total else None,
            "average_rating": round(float(analysed["rating"].mean()), 2) if total else None,
            "top_issues": [{"issue": k, "count": v} for k, v in issues.most_common()],
        }


def summarise_file(path: Path) -> dict:
    reviews = pd.read_csv(path)
    analyser = ReviewAnalyzer()
    summary = analyser.summarise(analyser.analyse(reviews))
    sources = reviews["source"].dropna().unique().tolist() if "source" in reviews else []
    summary["data_source"] = ", ".join(sources) or "unknown"
    return summary
