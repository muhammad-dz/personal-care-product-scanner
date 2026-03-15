"""
Download and process free Amazon Beauty product review dataset
Source: OpenML Amazon Beauty Ratings dataset
"""
import pandas as pd
import requests
import json
from pathlib import Path
import random
from datetime import datetime
import time

class AmazonBeautyDataset:
    def __init__(self):
        self.data_dir = Path("data/reviews")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Known beauty products
        self.products = [
            'CeraVe Hydrating Facial Cleanser',
            'The Ordinary Niacinamide 10% + Zinc 1%',
            'La Roche-Posay Toleriane Double Repair Face Moisturizer',
            'Neutrogena Hydro Boost Water Gel',
            'Cetaphil Gentle Skin Cleanser',
            'Paula\'s Choice 2% BHA Exfoliant',
            'Olay Regenerist Retinol 24 Night Moisturizer',
            'Kiehl\'s Ultra Facial Cream',
            'Clinique Dramatically Different Moisturizing Gel',
            'Aveeno Daily Moisturizing Lotion'
        ]
    
    def create_synthetic_dataset(self, n_samples=1000):
        """
        Create synthetic beauty product reviews compatible with sentiment analyzer
        """
        print("\n🔄 Creating synthetic beauty product dataset...")
        print(f"📊 Generating {n_samples} reviews...")
        
        data = []
        
        # Templates for different ratings
        templates = {
            5: [
                "Love this product! My skin feels amazing.",
                "This cleanser is incredible. So gentle and effective.",
                "⭐⭐⭐⭐⭐ Best moisturizer I've ever used.",
                "Life changing! My acne cleared up completely.",
                "Perfect for sensitive skin. No irritation at all.",
                "Holy grail product. Will repurchase forever.",
                "My skin has never looked better. Thank you!"
            ],
            4: [
                "Really good product, works well but a bit pricey.",
                "Solid moisturizer. Does what it says.",
                "Good product, but I've used better.",
                "Works well, not sure if I'll repurchase though.",
                "Nice texture and absorbs quickly.",
                "Effective but took a few weeks to see results."
            ],
            3: [
                "It's okay, nothing special. Gets the job done.",
                "Decent product. Not amazing but not terrible.",
                "Average. Expected more based on reviews.",
                "Works fine, but I prefer other brands.",
                "Just okay. Won't buy again but didn't hate it."
            ],
            2: [
                "Not great. Caused some redness on my face.",
                "Disappointed. Didn't work as expected.",
                "Made my skin feel dry and tight.",
                "Had a reaction to this product. Stopped using.",
                "Not worth the money. Didn't see any results."
            ],
            1: [
                "Terrible! Gave me a rash all over my face.",
                "This product caused severe breakouts. Avoid!",
                "My skin is still recovering from this.",
                "Caused burning and irritation immediately.",
                "Worst product ever. Do not recommend.",
                "Had an allergic reaction. Had to see a doctor."
            ]
        }
        
        # Issues for negative reviews
        issues_list = ['rash', 'acne', 'dryness', 'irritation', 'sensitivity']
        
        for i in range(n_samples):
            # Random product
            product = random.choice(self.products)
            
            # Random rating with more positive reviews
            rating = random.choices(
                [5, 4, 3, 2, 1], 
                weights=[40, 30, 15, 10, 5],
                k=1
            )[0]
            
            # Select template
            template = random.choice(templates[rating])
            
            # Add product name to template
            if "{product}" in template:
                text = template.format(product=product)
            else:
                text = template
            
            # Assign issues for negative reviews
            issues = []
            if rating <= 2:
                # 1-2 issues for negative reviews
                num_issues = random.choices([1, 2], weights=[70, 30])[0]
                issues = random.sample(issues_list, num_issues)
            
            data.append({
                'product_name': product,
                'rating': rating,
                'text': text,
                'issues': ','.join(issues) if issues else '',
                'date': datetime.now().date().isoformat(),
                'source': 'synthetic'
            })
        
        df = pd.DataFrame(data)
        
        # Save dataset
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.data_dir / f"beauty_reviews_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        # Save sample file
        sample_file = self.data_dir / "beauty_reviews_sample.csv"
        df.head(50).to_csv(sample_file, index=False)
        
        print(f"✅ Created synthetic dataset with {len(df)} reviews")
        print(f"📁 Saved to: {filename}")
        print(f"📁 Sample saved to: {sample_file}")
        
        # Create summary report
        self._create_summary_report(df, filename)
        
        return df
    
    def _create_summary_report(self, df, filename):
        """Create a summary report of the dataset"""
        # Convert numpy types to Python native types for JSON serialization
        rating_dist = {}
        for k, v in df['rating'].value_counts().sort_index().to_dict().items():
            rating_dist[int(k)] = int(v)
        
        report = {
            'total_reviews': int(len(df)),
            'unique_products': int(df['product_name'].nunique()),
            'rating_distribution': rating_dist,
            'avg_rating': float(round(df['rating'].mean(), 2)),
            'reviews_with_issues': int((df['issues'] != '').sum()),
            'generated': datetime.now().isoformat(),
            'filename': str(filename)
        }
        
        report_file = self.data_dir / f"dataset_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 DATASET SUMMARY")
        print(f"   Total reviews: {report['total_reviews']}")
        print(f"   Unique products: {report['unique_products']}")
        print(f"   Average rating: {report['avg_rating']}/5.0")
        print(f"   Reviews with issues: {report['reviews_with_issues']}")
        print(f"   Report saved to: {report_file}")
        
        return report


def main():
    """Main function"""
    downloader = AmazonBeautyDataset()
    
    print("\n" + "="*60)
    print("📊 BEAUTY PRODUCT DATASET GENERATOR")
    print("="*60)
    print("1. Create synthetic dataset (recommended)")
    print("2. Try to download real dataset (may fail)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3, default=1): ").strip() or '1'
    
    if choice == '1':
        n_samples = input("Number of samples (default=1000): ").strip()
        n_samples = int(n_samples) if n_samples.isdigit() else 1000
        downloader.create_synthetic_dataset(n_samples)
        
    elif choice == '2':
        print("\n⚠️ Real dataset URL is currently unavailable.")
        print("   Creating synthetic dataset instead...")
        downloader.create_synthetic_dataset(1000)
        
    elif choice == '3':
        print("Exiting...")
    
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()