import pandas as pd
import glob
import os
from sentiment_analyzer import CosmeticSentimentAnalyzer
import json
from datetime import datetime

def analyze_influenster_reviews():
    review_files = glob.glob("data/reviews/influenster_reviews_*.csv")
    
    if not review_files:
        print("No Influenster review files found.")
        print("Please run the scraper first: python scraper/influenster_scraper.py")
        return
    
    latest = max(review_files, key=os.path.getctime)
    print(f"Loading: {latest}")
    
    df = pd.read_csv(latest)
    print(f"Loaded {len(df)} reviews")
    
    if len(df) == 0:
        print("No reviews found in this file")
        return
    
    analyzer = CosmeticSentimentAnalyzer()
    
    print("Analyzing customer sentiment...")
    results = analyzer.analyze_reviews(df)
    
    report = analyzer.generate_report(results)
    
    report['source'] = 'Influenster'
    report['analyzed_date'] = datetime.now().isoformat()
    
    report_file = f"data/reviews/influenster_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*60)
    print("INFLUENSTER REVIEW ANALYSIS")
    print("="*60)
    print(f"Total reviews: {report['total_reviews']}")
    print(f"\nHow people feel:")
    print(f"  Happy customers: {report['sentiment_counts'].get('positive', 0)} ({report['sentiment_percentages']['positive']}%)")
    print(f"  Mixed feelings:  {report['sentiment_counts'].get('neutral', 0)} ({report['sentiment_percentages']['neutral']}%)")
    print(f"  Unhappy customers: {report['sentiment_counts'].get('negative', 0)} ({report['sentiment_percentages']['negative']}%)")
    print(f"\nAverage sentiment score: {report['avg_sentiment_score']}")
    print(f"Average rating: {report['avg_rating']} out of 5")
    
    print(f"\nMost common complaints:")
    for i, (issue, count) in enumerate(list(report['issue_frequency'].items())[:5], 1):
        print(f"  {i}. {issue}: {count} people mentioned this")
    
    print(f"\nReport saved to {report_file}")
    print("="*60)
    
    summary_df = results[['product_name', 'sentiment', 'rating', 'issues', 'text_preview']]
    summary_file = f"data/reviews/influenster_analyzed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"Analyzed data saved to {summary_file}")

if __name__ == "__main__":
    analyze_influenster_reviews()