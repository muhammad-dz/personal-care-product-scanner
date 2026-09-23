import pandas as pd
import pytest

from app.services.sentiment import ReviewAnalyzer, summarise_file


@pytest.fixture(scope="module")
def analyser():
    return ReviewAnalyzer()


def test_labels(analyser):
    assert analyser.sentiment("I love this, my skin feels amazing")[0] == "positive"
    assert analyser.sentiment("Terrible, it burned my face and I hate it")[0] == "negative"
    assert analyser.sentiment("The bottle is 50ml.")[0] == "neutral"


def test_issue_keywords_match_whole_words(analyser):
    assert sorted(analyser.issues("Gave me a rash and a breakout, skin felt dry")) == ["acne", "dryness", "rash"]
    assert analyser.issues("Hydrating and lovely") == []  # "dry" inside "hydrating" doesn't count


def test_positive_reviews_do_not_report_issues(analyser):
    reviews = pd.DataFrame([{"product_name": "A", "rating": 5,
                             "text": "Amazing for sensitive skin, no irritation at all."}])
    assert analyser.analyse(reviews)["issues"].iloc[0] == []


def test_short_reviews_skipped(analyser):
    reviews = pd.DataFrame([{"product_name": "A", "rating": 1, "text": "bad"},
                            {"product_name": "B", "rating": 5, "text": "Really lovely cleanser, would buy again"}])
    assert list(analyser.analyse(reviews)["product_name"]) == ["B"]


def test_summary_from_file(tmp_path):
    path = tmp_path / "reviews.csv"
    pd.DataFrame([
        {"product_name": "A", "rating": 5, "text": "Absolutely wonderful, best cleanser I have used.", "source": "test"},
        {"product_name": "B", "rating": 1, "text": "Awful, it gave me a horrible rash.", "source": "test"},
        {"product_name": "C", "rating": 2, "text": "Horrible breakout and a rash, very disappointing.", "source": "test"},
    ]).to_csv(path, index=False)

    summary = summarise_file(path)
    assert summary["total_reviews"] == 3
    assert summary["sentiment"]["negative"]["count"] == 2
    assert summary["top_issues"][0] == {"issue": "rash", "count": 2}
    assert summary["average_rating"] == pytest.approx(2.67)
    assert summary["data_source"] == "test"
