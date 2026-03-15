"""
Analyze Influenster reviews for sentiment and issues
"""
import pandas as pd
import glob
import os
from sentiment_analyzer import CosmeticSentimentAnalyzer
import json
from datetime import datetime

def analyze_influenster_reviews():
    """Find latest Influenster review file and analyze it"""
    
    # Find latest Influenster review file
    review_files = glob.glob("data/reviews/influenster_reviews_*.csv")
    
    if not review_files:
        print("❌ No Influenster review files found.")
        print("   Run the scraper first: python scraper/influenster_scraper.py")
        return
    
    latest = max(review_files, key=os.path.getctime)
    print(f"📁 Loading: {latest}")
    
    # Load the data
    df = pd.read_csv(latest)
    print(f"📊 Loaded {len(df)} reviews")
    
    if len(df) == 0:
        print("❌ No reviews in the file")
        return
    
    # Initialize analyzer
    analyzer = CosmeticSentimentAnalyzer()
    
    # Analyze reviews
    print("🔍 Analyzing sentiments...")
    results = analyzer.analyze_reviews(df)
    
    # Generate report
    report = analyzer.generate_report(results)
    
    # Add source information
    report['source'] = 'Influenster'
    report['analyzed_date'] = datetime.now().isoformat()
    
    # Save report
    report_file = f"data/reviews/influenster_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 INFLUENSTER SENTIMENT ANALYSIS REPORT")
    print("="*60)
    print(f"Total Reviews: {report['total_reviews']}")
    print(f"\nSentiment Distribution:")
    print(f"  Positive: {report['sentiment_counts'].get('positive', 0)} ({report['sentiment_percentages']['positive']}%)")
    print(f"  Neutral:  {report['sentiment_counts'].get('neutral', 0)} ({report['sentiment_percentages']['neutral']}%)")
    print(f"  Negative: {report['sentiment_counts'].get('negative', 0)} ({report['sentiment_percentages']['negative']}%)")
    print(f"\nAverage Sentiment Score: {report['avg_sentiment_score']}")
    print(f"Average Rating: {report['avg_rating']}/5.0")
    
    print(f"\n🔴 Top Reported Issues:")
    for i, (issue, count) in enumerate(list(report['issue_frequency'].items())[:5], 1):
        print(f"  {i}. {issue}: {count}")
    
    print(f"\n✅ Report saved to {report_file}")
    print("="*60)
    
    # Save a summary CSV for easy viewing
    summary_df = results[['product_name', 'sentiment', 'rating', 'issues', 'text_preview']]
    summary_file = f"data/reviews/influenster_analyzed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"📄 Analyzed data saved to {summary_file}")

if __name__ == "__main__":
    analyze_influenster_reviews()