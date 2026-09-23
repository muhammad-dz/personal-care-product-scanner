"""
Simple test for sentiment analysis on sample data
"""
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter

print("Loading sample reviews...")
df = pd.read_csv('data/reviews/sample_reviews.csv')
print(f"Loaded {len(df)} reviews")

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Analyze each review
results = []
for _, row in df.iterrows():
    text = row['text']
    scores = sia.polarity_scores(text)
    
    if scores['compound'] >= 0.05:
        sentiment = 'positive'
    elif scores['compound'] <= -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    results.append({
        'product': row['product_name'],
        'rating': row['rating'],
        'sentiment': sentiment,
        'score': scores['compound'],
        'text': text[:50] + '...'
    })

# Create DataFrame
results_df = pd.DataFrame(results)

# Print summary
print("\n" + "="*60)
print("SENTIMENT ANALYSIS RESULTS")
print("="*60)
print(f"Total Reviews: {len(results_df)}")
print(f"\nSentiment Distribution:")
print(f"  Positive: {(results_df['sentiment'] == 'positive').sum()} ({(results_df['sentiment'] == 'positive').mean()*100:.1f}%)")
print(f"  Neutral:  {(results_df['sentiment'] == 'neutral').sum()} ({(results_df['sentiment'] == 'neutral').mean()*100:.1f}%)")
print(f"  Negative: {(results_df['sentiment'] == 'negative').sum()} ({(results_df['sentiment'] == 'negative').mean()*100:.1f}%)")

print(f"\nAverage Sentiment Score: {results_df['score'].mean():.3f}")
print(f"Average Rating: {results_df['rating'].mean():.1f}/5.0")

# Extract issues
issues = []
issue_keywords = {
    'rash': ['rash', 'redness', 'itchy', 'irritation'],
    'acne': ['acne', 'breakout', 'pimple'],
    'dryness': ['dry', 'flaky', 'peeling']
}

for _, row in df.iterrows():
    text = row['text'].lower()
    for issue, keywords in issue_keywords.items():
        for keyword in keywords:
            if keyword in text:
                issues.append(issue)
                break

print(f"\nIssues Detected:")
issue_counts = Counter(issues)
for issue, count in issue_counts.most_common():
    print(f"  - {issue}: {count}")

# Save results
results_df.to_csv('data/reviews/sentiment_results.csv', index=False)
print("\n✅ Results saved to data/reviews/sentiment_results.csv")
