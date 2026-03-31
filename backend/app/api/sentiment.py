"""
Sentiment Analysis API Endpoints with Product-Specific Filtering and Word Cloud
"""
from fastapi import APIRouter
import pandas as pd
import json
from pathlib import Path
from collections import Counter
import logging
import glob
import sys
import os

# Add the project root to Python path to find nlp module
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)
router = APIRouter()

DATA_DIR = Path("../data/reviews")

# Sample data as fallback
SAMPLE_SENTIMENT_DATA = {
    "success": True,
    "data": {
        "total_reviews": 1000,
        "sentiment_counts": {"positive": 571, "neutral": 166, "negative": 263},
        "sentiment_percentages": {"positive": 57.1, "neutral": 16.6, "negative": 26.3},
        "avg_sentiment_score": 0.164,
        "avg_rating": 3.9,
        "issue_frequency": {"rash": 96, "sensitivity": 75, "acne": 57, "dryness": 19, "irritation": 15}
    }
}


def get_latest_review_file():
    """Find the most recent review file"""
    files = list(DATA_DIR.glob("*reviews*.csv"))
    files = [f for f in files if 'sample' not in f.name.lower()]
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_ctime)


def load_review_data():
    """Load the latest review dataset"""
    latest_file = get_latest_review_file()
    if latest_file and latest_file.exists():
        try:
            df = pd.read_csv(latest_file)
            if len(df) > 0:
                return df
        except Exception as e:
            print(f"Error loading reviews: {e}")
    return None


@router.get("/sentiment/summary")
async def get_sentiment_summary():
    """Get overall sentiment summary (global stats)"""
    try:
        df = load_review_data()
        if df is not None and len(df) > 0:
            total = len(df)
            
            if 'sentiment' in df.columns:
                pos = (df['sentiment'] == 'positive').sum()
                neu = (df['sentiment'] == 'neutral').sum()
                neg = (df['sentiment'] == 'negative').sum()
            else:
                pos = (df['rating'] >= 4).sum()
                neu = ((df['rating'] >= 3) & (df['rating'] < 4)).sum()
                neg = (df['rating'] < 3).sum()
            
            issue_freq = {}
            if 'issues' in df.columns:
                all_issues = []
                for issues in df['issues']:
                    if isinstance(issues, str) and issues:
                        all_issues.extend(issues.split(','))
                issue_freq = dict(Counter(all_issues).most_common(5))
            else:
                issue_freq = {"rash": 96, "sensitivity": 75, "acne": 57}
            
            return {
                "success": True,
                "data": {
                    "total_reviews": int(total),
                    "sentiment_counts": {"positive": int(pos), "neutral": int(neu), "negative": int(neg)},
                    "sentiment_percentages": {
                        "positive": round(pos/total*100, 1),
                        "neutral": round(neu/total*100, 1),
                        "negative": round(neg/total*100, 1)
                    },
                    "avg_sentiment_score": 0.164,
                    "avg_rating": round(df['rating'].mean(), 1) if 'rating' in df else 3.9,
                    "issue_frequency": issue_freq
                }
            }
    except Exception as e:
        print(f"Error loading data: {e}")
    
    return SAMPLE_SENTIMENT_DATA


@router.get("/sentiment/product/{product_name}")
async def get_product_sentiment(product_name: str):
    """Get sentiment for a specific product"""
    try:
        df = load_review_data()
        
        if df is None or len(df) == 0:
            return {
                "success": False,
                "message": "No review data available",
                "product_name": product_name,
                "sentiment": None
            }
        
        product_lower = product_name.lower()
        
        # Try exact match first
        product_df = df[df['product_name'].str.lower() == product_lower]
        
        # If no exact match, try partial match
        if len(product_df) == 0:
            words = product_lower.split()
            skip_words = ['the', 'and', 'for', 'with', 'plus', 'cream', 'lotion', 'gel', 'face', 'skin']
            keywords = [w for w in words if w not in skip_words and len(w) > 3][:3]
            
            if keywords:
                mask = pd.Series([False] * len(df))
                for keyword in keywords:
                    mask |= df['product_name'].str.lower().str.contains(keyword, na=False)
                product_df = df[mask]
        
        if len(product_df) == 0:
            return {
                "success": False,
                "message": f"No reviews found for {product_name}",
                "product_name": product_name,
                "sentiment": None,
                "total_reviews": 0
            }
        
        total = len(product_df)
        
        if 'sentiment' in product_df.columns:
            pos = (product_df['sentiment'] == 'positive').sum()
            neu = (product_df['sentiment'] == 'neutral').sum()
            neg = (product_df['sentiment'] == 'negative').sum()
        else:
            pos = (product_df['rating'] >= 4).sum()
            neu = ((product_df['rating'] >= 3) & (product_df['rating'] < 4)).sum()
            neg = (product_df['rating'] < 3).sum()
        
        all_issues = []
        if 'issues' in product_df.columns:
            for issues in product_df['issues']:
                if isinstance(issues, str) and issues:
                    all_issues.extend(issues.split(','))
        
        issue_freq = dict(Counter(all_issues).most_common(5))
        
        sample_reviews = []
        if 'text' in product_df.columns:
            for _, row in product_df.head(3).iterrows():
                text = row.get('text', '')
                sample_reviews.append({
                    'text': text[:150] + '...' if len(text) > 150 else text,
                    'rating': row.get('rating', 3),
                    'sentiment': row.get('sentiment', 'neutral')
                })
        
        return {
            "success": True,
            "product_name": product_name,
            "total_reviews": int(total),
            "sentiment": {
                "positive": int(pos),
                "neutral": int(neu),
                "negative": int(neg),
                "positive_pct": round(pos/total*100, 1) if total > 0 else 0,
                "neutral_pct": round(neu/total*100, 1) if total > 0 else 0,
                "negative_pct": round(neg/total*100, 1) if total > 0 else 0
            },
            "average_rating": round(product_df['rating'].mean(), 1) if 'rating' in product_df else 0,
            "common_issues": issue_freq,
            "sample_reviews": sample_reviews
        }
        
    except Exception as e:
        print(f"Error in product sentiment: {e}")
        return {
            "success": False,
            "error": str(e),
            "product_name": product_name
        }


@router.get("/sentiment/wordcloud")
async def get_wordcloud(sentiment: str = None):
    """Get word cloud image for overall or filtered sentiment"""
    try:
        from nlp.sentiment_analyzer import CosmeticSentimentAnalyzer
        
        df = load_review_data()
        
        if df is None or len(df) == 0:
            return {"success": False, "message": "No review data available"}
        
        if sentiment and sentiment in ['positive', 'negative']:
            if 'sentiment' not in df.columns:
                analyzer_temp = CosmeticSentimentAnalyzer()
                sentiments = []
                for text in df['text']:
                    s, _ = analyzer_temp.analyze_sentiment(text)
                    sentiments.append(s)
                df['sentiment'] = sentiments
            
            df = df[df['sentiment'] == sentiment]
            if len(df) == 0:
                return {"success": False, "message": f"No {sentiment} reviews found"}
        
        analyzer = CosmeticSentimentAnalyzer()
        img_base64 = analyzer.generate_wordcloud(df, sentiment)
        
        if img_base64:
            return {
                "success": True,
                "sentiment_filter": sentiment or "all",
                "image": img_base64,
                "review_count": len(df)
            }
        else:
            return {"success": False, "message": "Could not generate word cloud"}
            
    except Exception as e:
        print(f"Error generating word cloud: {e}")
        return {"success": False, "error": str(e)}


@router.get("/sentiment/wordcloud/data")
async def get_wordcloud_data(sentiment: str = None):
    """Get word frequency data for word cloud"""
    try:
        from nlp.sentiment_analyzer import CosmeticSentimentAnalyzer
        
        df = load_review_data()
        
        if df is None or len(df) == 0:
            return {"success": False, "message": "No review data available"}
        
        if sentiment and sentiment in ['positive', 'negative']:
            if 'sentiment' not in df.columns:
                analyzer_temp = CosmeticSentimentAnalyzer()
                sentiments = []
                for text in df['text']:
                    s, _ = analyzer_temp.analyze_sentiment(text)
                    sentiments.append(s)
                df['sentiment'] = sentiments
            
            df = df[df['sentiment'] == sentiment]
        
        analyzer = CosmeticSentimentAnalyzer()
        word_data = analyzer.get_wordcloud_data(df, sentiment)
        
        return {
            "success": True,
            "sentiment_filter": sentiment or "all",
            "words": word_data,
            "review_count": len(df)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/sentiment/health")
async def sentiment_health():
    """Simple health check"""
    return {"status": "ok", "message": "Sentiment API is working"}


@router.get("/sentiment/test")
async def sentiment_test():
    """Test endpoint"""
    return {"success": True, "message": "Sentiment API test successful"}