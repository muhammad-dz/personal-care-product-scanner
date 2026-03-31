import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter

print("Loading sample customer reviews...")
df = pd.read_csv('data/reviews/sample_reviews.csv')
print(f"Found {len(df)} reviews")

sia = SentimentIntensityAnalyzer()

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

results_df = pd.DataFrame(results)

print("\n" + "="*60)
print("CUSTOMER REVIEW ANALYSIS")
print("="*60)
print(f"Total reviews analyzed: {len(results_df)}")
print(f"\nHow people feel:")
print(f"  Happy customers: {(results_df['sentiment'] == 'positive').sum()} ({(results_df['sentiment'] == 'positive').mean()*100:.1f}%)")
print(f"  Mixed feelings:  {(results_df['sentiment'] == 'neutral').sum()} ({(results_df['sentiment'] == 'neutral').mean()*100:.1f}%)")
print(f"  Unhappy customers: {(results_df['sentiment'] == 'negative').sum()} ({(results_df['sentiment'] == 'negative').mean()*100:.1f}%)")

print(f"\nAverage sentiment score: {results_df['score'].mean():.3f}")
print(f"Average rating: {results_df['rating'].mean():.1f} out of 5")

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

print(f"\nWhat people complained about:")
issue_counts = Counter(issues)
for issue, count in issue_counts.most_common():
    print(f"  - {issue}: {count} people mentioned this")

results_df.to_csv('data/reviews/sentiment_results.csv', index=False)
print("\nAnalysis complete! Results saved to data/reviews/sentiment_results.csv")