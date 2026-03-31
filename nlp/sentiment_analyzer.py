"""
Sentiment Analysis for Cosmetic Reviews with Word Cloud Support
"""
import nltk
import pandas as pd
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
import glob
import json
import os
from collections import Counter
from datetime import datetime
import re

# Download required NLTK data
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Try to import wordcloud
try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    import io
    import base64
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    print("WordCloud not available. Install with: pip install wordcloud matplotlib")


class CosmeticSentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        
        self.issue_keywords = {
            'rash': ['rash', 'redness', 'itchy', 'irritation', 'burning'],
            'acne': ['acne', 'breakout', 'pimple'],
            'dryness': ['dry', 'flaky', 'peeling', 'tight'],
            'sensitivity': ['sensitive', 'allergic', 'reaction', 'sting']
        }
    
    def analyze_sentiment(self, text):
        scores = self.sia.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return sentiment, compound, scores
    
    def extract_issues(self, text):
        text_lower = text.lower()
        detected = []
        
        for issue, keywords in self.issue_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(issue)
                    break
        return detected
    
    def generate_wordcloud(self, reviews_df, sentiment_filter=None):
        """Generate word cloud from reviews"""
        if not WORDCLOUD_AVAILABLE:
            return None
        
        if 'text' not in reviews_df.columns:
            print("No text column found in data")
            return None
        
        if sentiment_filter:
            filtered_df = reviews_df[reviews_df['sentiment'] == sentiment_filter]
            if len(filtered_df) == 0:
                return None
            text = ' '.join(filtered_df['text'].fillna(''))
        else:
            text = ' '.join(reviews_df['text'].fillna(''))
        
        if not text or len(text) < 50:
            print(f"Not enough text. Length: {len(text)}")
            return None
        
        # Clean text
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            max_words=100,
            colormap='gray'
        ).generate(text)
        
        # Convert to image
        img_buffer = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        
        img_buffer.seek(0)
        return base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    def get_wordcloud_data(self, reviews_df, sentiment_filter=None):
        """Get word frequencies for word cloud"""
        if 'text' not in reviews_df.columns:
            return {}
        
        if sentiment_filter:
            filtered_df = reviews_df[reviews_df['sentiment'] == sentiment_filter]
            if len(filtered_df) == 0:
                return {}
            text = ' '.join(filtered_df['text'].fillna(''))
        else:
            text = ' '.join(reviews_df['text'].fillna(''))
        
        if not text:
            return {}
        
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        word_counts = Counter(words)
        
        stopwords = {'the', 'and', 'for', 'this', 'product', 'skin', 'have', 'with', 'was', 'but', 'not', 'you', 'are', 'has', 'from', 'your', 'like', 'very', 'just', 'can'}
        
        for stop in stopwords:
            if stop in word_counts:
                del word_counts[stop]
        
        return dict(word_counts.most_common(30))