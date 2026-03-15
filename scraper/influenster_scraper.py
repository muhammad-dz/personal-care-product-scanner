"""
Influenster Product Review Scraper
Specifically designed for beauty and personal care product reviews
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
from datetime import datetime
import re

class InfluensterScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
        }
        
        # Popular beauty products with known Influenster URLs
        self.beauty_products = [
            {
                'name': 'CeraVe Hydrating Facial Cleanser',
                'url': 'https://www.influenster.com/reviews/cerave-hydrating-facial-cleanser'
            },
            {
                'name': 'The Ordinary Niacinamide 10% + Zinc 1%',
                'url': 'https://www.influenster.com/reviews/the-ordinary-niacinamide-10-zinc-1'
            },
            {
                'name': 'La Roche-Posay Toleriane Double Repair Face Moisturizer',
                'url': 'https://www.influenster.com/reviews/la-roche-posay-toleriane-double-repair-face-moisturizer'
            },
            {
                'name': 'Neutrogena Hydro Boost Water Gel',
                'url': 'https://www.influenster.com/reviews/neutrogena-hydro-boost-water-gel'
            },
            {
                'name': 'Cetaphil Gentle Skin Cleanser',
                'url': 'https://www.influenster.com/reviews/cetaphil-gentle-skin-cleanser'
            }
        ]
    
    def scrape_product_reviews(self, product_url, max_pages=3):
        """
        Scrape reviews for a specific product from Influenster
        """
        all_reviews = []
        product_name = self._extract_product_name(product_url)
        
        print(f"🔍 Scraping reviews for: {product_name}")
        
        for page in range(1, max_pages + 1):
            try:
                # Construct paginated URL
                if '?' in product_url:
                    paginated_url = f"{product_url}&page={page}"
                else:
                    paginated_url = f"{product_url}?page={page}"
                
                print(f"  Fetching page {page}...")
                response = requests.get(paginated_url, headers=self.headers, timeout=15)
                
                if response.status_code != 200:
                    print(f"  Failed to load page {page}: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all review cards - adjust selectors based on actual HTML
                review_cards = soup.find_all('div', class_=re.compile(r'review-card|review-item|review__card'))
                
                # Fallback selectors if the above doesn't work
                if not review_cards:
                    review_cards = soup.find_all('div', {'data-testid': 'review-card'})
                if not review_cards:
                    review_cards = soup.find_all('article', class_=re.compile(r'review'))
                
                if not review_cards:
                    print(f"  No reviews found on page {page}")
                    break
                
                for card in review_cards:
                    try:
                        review = self._parse_review_card(card, product_name)
                        if review:
                            all_reviews.append(review)
                    except Exception as e:
                        print(f"    Error parsing review: {e}")
                        continue
                
                print(f"  Page {page}: Found {len(review_cards)} reviews, saved {len([r for r in all_reviews if r.get('product_name') == product_name])} total")
                
                # Random delay to avoid blocking
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"  Error on page {page}: {e}")
                break
        
        print(f"  Total for {product_name}: {len([r for r in all_reviews if r.get('product_name') == product_name])} reviews")
        return all_reviews
    
    def _parse_review_card(self, card, product_name):
        """
        Extract review details from a review card element
        """
        # Rating (usually 1-5 stars)
        rating = 0
        rating_elem = card.find('span', class_=re.compile(r'rating|stars', re.I))
        if rating_elem:
            rating_text = rating_elem.get_text().strip()
            rating_match = re.search(r'(\d+(\.\d+)?)', rating_text)
            if rating_match:
                rating = float(rating_match.group(1))
        else:
            # Try to find by aria-label
            rating_elem = card.find('div', {'aria-label': re.compile(r'rating', re.I)})
            if rating_elem:
                rating_match = re.search(r'(\d+(\.\d+)?)', rating_elem.get('aria-label', ''))
                if rating_match:
                    rating = float(rating_match.group(1))
        
        # Review title
        title = ""
        title_elem = card.find('h3', class_=re.compile(r'title|heading', re.I))
        if title_elem:
            title = title_elem.get_text().strip()
        
        # Review text
        text = ""
        text_elem = card.find('p', class_=re.compile(r'review-text|description|content', re.I))
        if text_elem:
            text = text_elem.get_text().strip()
        
        # Skip if no review text
        if not text or len(text) < 20:
            return None
        
        # Review date
        date = ""
        date_elem = card.find('time')
        if date_elem:
            date = date_elem.get('datetime', date_elem.get_text().strip())
        else:
            date_elem = card.find('span', class_=re.compile(r'date', re.I))
            if date_elem:
                date = date_elem.get_text().strip()
        
        # Reviewer name
        reviewer = ""
        name_elem = card.find('span', class_=re.compile(r'username|author|name', re.I))
        if name_elem:
            reviewer = name_elem.get_text().strip()
        
        # Verified purchase? (Influenster reviews are from community members)
        verified = "Influenster"
        
        return {
            'product_name': product_name,
            'rating': rating,
            'title': title,
            'text': text,
            'date': date,
            'reviewer': reviewer,
            'verified': verified,
            'source': 'Influenster',
            'scraped_date': datetime.now().isoformat()
        }
    
    def _extract_product_name(self, url):
        """Extract product name from URL"""
        # Try to extract from URL pattern
        match = re.search(r'/reviews/(.+?)(?:\?|$)', url)
        if match:
            name_parts = match.group(1).split('-')
            return ' '.join([p.capitalize() for p in name_parts])
        return "Unknown Product"
    
    def scrape_multiple_products(self, product_list=None, max_pages=3):
        """
        Scrape reviews for multiple products
        """
        if product_list is None:
            product_list = self.beauty_products
        
        all_reviews = []
        
        for product in product_list:
            try:
                if isinstance(product, dict):
                    url = product.get('url')
                else:
                    url = product
                
                reviews = self.scrape_product_reviews(url, max_pages)
                all_reviews.extend(reviews)
                
                # Longer delay between products
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                print(f"❌ Failed to scrape {product}: {e}")
                continue
        
        # Save to CSV
        if all_reviews:
            df = pd.DataFrame(all_reviews)
            filename = f"data/reviews/influenster_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"\n✅ Saved {len(all_reviews)} reviews to {filename}")
            
            # Also save a sample for quick viewing
            sample_file = f"data/reviews/influenster_reviews_sample.csv"
            df.head(20).to_csv(sample_file, index=False)
            print(f"   Sample (20 reviews) saved to {sample_file}")
        else:
            print("\n❌ No reviews were collected!")
        
        return all_reviews
    
    def search_products_by_category(self, category, max_results=10):
        """
        Search for products by category (e.g., 'moisturizer', 'cleanser')
        Note: This is a helper to find product URLs, not a full implementation
        """
        print(f"🔍 Searching for {category} products...")
        print("   To find product URLs manually:")
        print(f"   1. Go to https://www.influenster.com/search?q={category}")
        print(f"   2. Click on individual products")
        print(f"   3. Copy the URL from the reviews page")
        return []


def main():
    """Main function to run the scraper"""
    print("=" * 60)
    print("INFLUENSTER BEAUTY PRODUCT REVIEW SCRAPER")
    print("=" * 60)
    
    scraper = InfluensterScraper()
    
    print("\n📋 Available products:")
    for i, product in enumerate(scraper.beauty_products, 1):
        print(f"  {i}. {product['name']}")
    
    print("\nOptions:")
    print("  1. Scrape all pre-defined products")
    print("  2. Scrape a custom URL")
    print("  3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        print("\n🚀 Scraping all pre-defined products...")
        scraper.scrape_multiple_products(max_pages=3)
        
    elif choice == '2':
        url = input("\nEnter Influenster review URL: ").strip()
        if url:
            pages = input("Number of pages to scrape (default 3): ").strip()
            pages = int(pages) if pages.isdigit() else 3
            scraper.scrape_product_reviews(url, pages)
        else:
            print("❌ No URL provided")
    
    elif choice == '3':
        print("Exiting...")
    
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()