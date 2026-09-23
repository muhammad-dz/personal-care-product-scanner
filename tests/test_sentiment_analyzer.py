"""Unit tests for the NLP review analyser (VADER sentiment + issue keywords)."""
import nltk
import pandas as pd
import pytest

nltk.download("vader_lexicon", quiet=True)

from nlp.sentiment_analyzer import CosmeticSentimentAnalyzer  # noqa: E402


@pytest.fixture(scope="module")
def analyzer():
    return CosmeticSentimentAnalyzer()


def test_positive_review(analyzer):
    sentiment, score = analyzer.analyze_sentiment("I love this moisturiser, my skin feels amazing and soft.")
    assert sentiment == "positive"
    assert score > 0.05


def test_negative_review(analyzer):
    sentiment, score = analyzer.analyze_sentiment("Terrible product. It burned my face and I hate it.")
    assert sentiment == "negative"
    assert score < -0.05


def test_neutral_review(analyzer):
    sentiment, _ = analyzer.analyze_sentiment("The bottle is 50ml.")
    assert sentiment == "neutral"


def test_extracts_multiple_issues_once_each(analyzer):
    issues = analyzer.extract_issues("Gave me a rash and redness, plus a breakout and dry flaky patches.")
    assert sorted(issues) == ["acne", "dryness", "rash"]


def test_issue_matching_is_case_insensitive(analyzer):
    assert analyzer.extract_issues("SEVERE IRRITATION") == ["rash"]


def test_no_issues_in_happy_review(analyzer):
    assert analyzer.extract_issues("Lovely texture and smells nice.") == []


def test_analyze_reviews_skips_short_or_empty_text(analyzer):
    df = pd.DataFrame([
        {"product_name": "A", "rating": 5, "text": "Absolutely wonderful, best cleanser I have used."},
        {"product_name": "B", "rating": 1, "text": "bad"},
        {"product_name": "C", "rating": 3, "text": ""},
    ])
    results = analyzer.analyze_reviews(df)
    assert list(results["product_name"]) == ["A"]


def test_generate_report_counts_sentiment_and_issues(analyzer):
    df = pd.DataFrame([
        {"product_name": "A", "rating": 5, "text": "Absolutely wonderful, best cleanser I have ever used."},
        {"product_name": "B", "rating": 1, "text": "Awful. It gave me a horrible rash and made my skin dry."},
        {"product_name": "C", "rating": 2, "text": "Caused a breakout and more irritation than I expected, disappointing."},
    ])
    report = analyzer.generate_report(analyzer.analyze_reviews(df))

    assert report["total_reviews"] == 3
    assert report["sentiment_counts"].get("positive") == 1
    assert report["sentiment_counts"].get("negative") == 2
    assert report["issue_frequency"]["rash"] == 2
    assert report["avg_rating"] == pytest.approx(2.7)
