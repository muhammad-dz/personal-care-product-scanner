import pandas as pd
import glob
import os
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from nlp.sentiment_analyzer import CosmeticSentimentAnalyzer
except ImportError:
    print("Note: Couldn't import the main sentiment analyzer. Using a simpler version instead...")
    
    from nltk.sentiment import SentimentIntensityAnalyzer
    from collections import Counter
    
    class CosmeticSentimentAnalyzer:
        def __init__(self):
            try:
                import nltk
                nltk.download('vader_lexicon', quiet=True)
                self.sia = SentimentIntensityAnalyzer()
            except:
                self.sia = None
                print("Note: NLTK not available, using basic rule-based sentiment detection")
        
        def analyze_sentiment(self, text):
            if self.sia:
                scores = self.sia.polarity_scores(text)
                compound = scores['compound']
                if compound >= 0.05:
                    sentiment = 'positive'
                elif compound <= -0.05:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                return sentiment, compound
            else:
                positive_words = ['love', 'great', 'amazing', 'perfect', 'best', 'excellent']
                negative_words = ['rash', 'acne', 'breakout', 'irritation', 'burning', 'terrible']
                
                text_lower = text.lower()
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count > neg_count:
                    return 'positive', 0.5
                elif neg_count > pos_count:
                    return 'negative', -0.5
                else:
                    return 'neutral', 0.0
        
        def extract_issues(self, text):
            issues = []
            issue_keywords = {
                'rash': ['rash', 'redness', 'itchy', 'irritation', 'burning'],
                'acne': ['acne', 'breakout', 'pimple', 'cyst'],
                'dryness': ['dry', 'flaky', 'peeling', 'tight'],
                'sensitivity': ['sensitive', 'allergic', 'reaction', 'sting']
            }
            text_lower = text.lower()
            for issue, keywords in issue_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        issues.append(issue)
                        break
            return issues
        
        def analyze_reviews(self, df):
            results = []
            for _, row in df.iterrows():
                text = row.get('text', '')
                if not text or len(text) < 10:
                    continue
                
                sentiment, score = self.analyze_sentiment(text)
                issues = self.extract_issues(text)
                
                results.append({
                    'product_name': row.get('product_name', 'Unknown'),
                    'rating': row.get('rating', 3),
                    'sentiment': sentiment,
                    'sentiment_score': score,
                    'issues': issues
                })
            return pd.DataFrame(results)
        
        def generate_report(self, df):
            report = {
                'total_reviews': len(df),
                'sentiment_counts': df['sentiment'].value_counts().to_dict(),
                'avg_sentiment_score': round(df['sentiment_score'].mean(), 3) if len(df) > 0 else 0,
                'avg_rating': round(df['rating'].mean(), 1) if len(df) > 0 else 0,
                'issue_frequency': {}
            }
            
            total = report['total_reviews']
            if total > 0:
                report['sentiment_percentages'] = {
                    'positive': round((report['sentiment_counts'].get('positive', 0) / total) * 100, 1),
                    'neutral': round((report['sentiment_counts'].get('neutral', 0) / total) * 100, 1),
                    'negative': round((report['sentiment_counts'].get('negative', 0) / total) * 100, 1)
                }
            else:
                report['sentiment_percentages'] = {'positive': 0, 'neutral': 0, 'negative': 0}
            
            all_issues = []
            for issues in df['issues']:
                if isinstance(issues, list):
                    all_issues.extend(issues)
                elif isinstance(issues, str) and issues:
                    all_issues.extend(issues.split(','))
            
            report['issue_frequency'] = dict(Counter(all_issues).most_common())
            
            return report


class BeautyDatasetAnalyzer:
    def __init__(self):
        self.data_dir = Path("data/reviews")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = CosmeticSentimentAnalyzer()
    
    def find_latest_dataset(self):
        patterns = [
            "beauty_reviews_*.csv",
            "synthetic_beauty_*.csv",
            "*.csv"
        ]
        
        all_files = []
        for pattern in patterns:
            all_files.extend(glob.glob(str(self.data_dir / pattern)))
        
        exclude_patterns = ['sample', 'report', 'analyzed']
        filtered_files = []
        for f in all_files:
            if not any(p in f.lower() for p in exclude_patterns):
                filtered_files.append(f)
        
        if not filtered_files:
            return None
        
        return max(filtered_files, key=os.path.getctime)
    
    def analyze_dataset(self, dataset_path=None):
        if dataset_path is None:
            dataset_path = self.find_latest_dataset()
        
        if not dataset_path:
            print("No dataset files found!")
            print("Please run the downloader first: python scraper/download_beauty_dataset.py")
            return None
        
        print(f"Loading dataset: {dataset_path}")
        
        df = pd.read_csv(dataset_path)
        print(f"Loaded {len(df)} reviews")
        
        if len(df) == 0:
            print("No reviews found in this file")
            return None
        
        if 'text' not in df.columns:
            if 'review' in df.columns:
                df.rename(columns={'review': 'text'}, inplace=True)
            elif 'review_text' in df.columns:
                df.rename(columns={'review_text': 'text'}, inplace=True)
            else:
                print("Couldn't find any review text to analyze")
                return None
        
        print("Analyzing customer sentiment...")
        results = self.analyzer.analyze_reviews(df)
        
        if len(results) == 0:
            print("No valid reviews to analyze")
            return None
        
        report = self.analyzer.generate_report(results)
        
        if 'sentiment_percentages' not in report:
            total = report['total_reviews']
            if total > 0:
                report['sentiment_percentages'] = {
                    'positive': round((report['sentiment_counts'].get('positive', 0) / total) * 100, 1),
                    'neutral': round((report['sentiment_counts'].get('neutral', 0) / total) * 100, 1),
                    'negative': round((report['sentiment_counts'].get('negative', 0) / total) * 100, 1)
                }
            else:
                report['sentiment_percentages'] = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        report['dataset_source'] = str(dataset_path)
        report['analyzed_date'] = datetime.now().isoformat()
        report['total_analyzed'] = int(len(results))
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.data_dir / f"analysis_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self._print_report(report)
        
        analyzed_file = self.data_dir / f"analyzed_reviews_{timestamp}.csv"
        results.to_csv(analyzed_file, index=False)
        print(f"\nSaved analyzed data to: {analyzed_file}")
        
        return results, report
    
    def _print_report(self, report):
        print("\n" + "="*60)
        print("BEAUTY PRODUCT REVIEW ANALYSIS")
        print("="*60)
        print(f"Total reviews analyzed: {report['total_reviews']}")
        print(f"\nHow people feel:")
        
        pos = report['sentiment_counts'].get('positive', 0)
        neu = report['sentiment_counts'].get('neutral', 0)
        neg = report['sentiment_counts'].get('negative', 0)
        
        if 'sentiment_percentages' in report:
            pos_pct = report['sentiment_percentages'].get('positive', 0)
            neu_pct = report['sentiment_percentages'].get('neutral', 0)
            neg_pct = report['sentiment_percentages'].get('negative', 0)
        else:
            total = report['total_reviews']
            pos_pct = round((pos / total) * 100, 1) if total > 0 else 0
            neu_pct = round((neu / total) * 100, 1) if total > 0 else 0
            neg_pct = round((neg / total) * 100, 1) if total > 0 else 0
        
        print(f"  Happy customers: {pos} ({pos_pct}%)")
        print(f"  Mixed feelings:  {neu} ({neu_pct}%)")
        print(f"  Unhappy customers: {neg} ({neg_pct}%)")
        print(f"\nAverage sentiment score: {report['avg_sentiment_score']}")
        print(f"Average rating: {report['avg_rating']} out of 5")
        
        print(f"\nMost common complaints:")
        for i, (issue, count) in enumerate(list(report['issue_frequency'].items())[:5], 1):
            print(f"  {i}. {issue}: {count} people mentioned this")
        
        print("="*60)


def main():
    print("="*60)
    print("BEAUTY PRODUCT REVIEW ANALYZER")
    print("="*60)
    
    analyzer = BeautyDatasetAnalyzer()
    
    latest = analyzer.find_latest_dataset()
    
    if latest:
        print(f"\nFound dataset: {latest}")
        choice = input("Would you like to analyze this dataset? (y/n): ").strip().lower()
        
        if choice == 'y':
            analyzer.analyze_dataset(latest)
        else:
            print("Analysis cancelled")
    else:
        print("\nNo datasets found!")
        print("First, create a dataset by running:")
        print("   python scraper/download_beauty_dataset.py")


if __name__ == "__main__":
    main()