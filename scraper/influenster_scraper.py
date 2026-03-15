"""
Enhanced Influenster Product Review Scraper
With anti-detection measures and session handling
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
import re
from fake_useragent import UserAgent

class EnhancedInfluensterScraper:
    def __init__(self):
        # Use fake-useragent to generate random realistic user agents
        self.ua = UserAgent()
        self.session = None
        self._create_session()
        
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
                'name': 'La Roche-Posay Toleriane Double Repair',
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
    
    def _create_session(self):
        """Create a new session with realistic browser headers"""
        self.session = requests.Session()
        
        # Generate random but realistic browser headers [citation:4]
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        self.session.headers.update(headers)
        
        # Add cookies to appear more like a real browser
        self.session.cookies.set('visid_incap', '', domain='.influenster.com')
        self.session.cookies.set('nlbi_', '', domain='.influenster.com')
    
    def _random_delay(self, min_seconds=2, max_seconds=5):
        """Add random delay between requests to avoid detection [citation:4]"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"  ⏱️ Waiting {delay:.1f} seconds...")
        time.sleep(delay)
    
    def scrape_product_reviews(self, product_url, max_pages=3):
        """
        Scrape reviews for a specific product with anti-detection measures
        """
        all_reviews = []
        product_name = self._extract_product_name(product_url)
        
        print(f"\n🔍 Scraping reviews for: {product_name}")
        print(f"📡 Using User-Agent: {self.session.headers['User-Agent'][:50]}...")
        
        for page in range(1, max_pages + 1):
            try:
                # Construct paginated URL
                if '?' in product_url:
                    paginated_url = f"{product_url}&page={page}"
                else:
                    paginated_url = f"{product_url}?page={page}"
                
                print(f"\n  📄 Fetching page {page}...")
                
                # Rotate User-Agent for each page to avoid fingerprinting [citation:4]
                self.session.headers.update({'User-Agent': self.ua.random})
                
                # Add a small random delay before request
                time.sleep(random.uniform(1, 2))
                
                # Make the request with timeout
                response = self.session.get(
                    paginated_url, 
                    timeout=15,
                    allow_redirects=True
                )
                
                print(f"  📊 Status code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"  ❌ Failed to load page {page}: {response.status_code}")
                    if response.status_code == 403:
                        print("  🔒 Blocked! This site has strong anti-bot protection.")
                        print("  💡 Try using a proxy service or consider alternative data sources.")
                    break
                
                # Check if we got a challenge page
                if "just a moment" in response.text.lower() or "captcha" in response.text.lower():
                    print("  ⚠️ Detected challenge page (Cloudflare/DDOS protection)")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors for review cards
                selectors = [
                    'div[class*="review-card"]',
                    'div[class*="review-item"]',
                    'div[data-testid="review-card"]',
                    'article[class*="review"]',
                    'div[class*="ReviewCard"]',
                    'div[class*="review__card"]'
                ]
                
                review_cards = []
                for selector in selectors:
                    review_cards = soup.select(selector)
                    if review_cards:
                        print(f"  ✅ Found {len(review_cards)} reviews using selector: {selector}")
                        break
                
                if not review_cards:
                    print(f"  ⚠️ No reviews found on page {page}")
                    # Save HTML for debugging
                    with open(f"debug_page_{page}.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print(f"  💾 Saved page HTML to debug_page_{page}.html for inspection")
                    break
                
                for card in review_cards:
                    try:
                        review = self._parse_review_card(card, product_name)
                        if review:
                            all_reviews.append(review)
                    except Exception as e:
                        print(f"    ⚠️ Error parsing review: {e}")
                        continue
                
                print(f"  ✅ Page {page}: Found {len(review_cards)} reviews")
                
                # Random delay between pages [citation:7]
                self._random_delay(3, 6)
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Network error on page {page}: {e}")
                break
            except Exception as e:
                print(f"  ❌ Unexpected error on page {page}: {e}")
                break
        
        print(f"\n📊 Total for {product_name}: {len(all_reviews)} reviews")
        return all_reviews
    
    def _parse_review_card(self, card, product_name):
        """Extract review details from a review card element"""
        
        # Extract review text
        text = ""
        text_selectors = [
            'p[class*="review-text"]',
            'p[class*="description"]',
            'div[class*="content"]',
            'span[class*="review"]',
            'div[data-testid*="review"]'
        ]
        
        for selector in text_selectors:
            elem = card.select_one(selector)
            if elem:
                text = elem.get_text().strip()
                break
        
        if not text or len(text) < 20:
            return None
        
        # Extract rating
        rating = 0
        rating_selectors = [
            'span[class*="rating"]',
            'div[class*="stars"]',
            'div[aria-label*="rating"]',
            'meta[itemprop="ratingValue"]'
        ]
        
        for selector in rating_selectors:
            elem = card.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    rating = float(elem.get('content', 0))
                else:
                    rating_text = elem.get_text().strip()
                    rating_match = re.search(r'(\d+(\.\d+)?)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                break
        
        # Extract reviewer name
        reviewer = ""
        name_selectors = [
            'span[class*="author"]',
            'span[class*="username"]',
            'div[class*="user"]',
            'meta[itemprop="author"]'
        ]
        
        for selector in name_selectors:
            elem = card.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    reviewer = elem.get('content', '')
                else:
                    reviewer = elem.get_text().strip()
                break
        
        # Extract date
        date = ""
        date_selectors = [
            'time',
            'span[class*="date"]',
            'meta[itemprop="datePublished"]'
        ]
        
        for selector in date_selectors:
            elem = card.select_one(selector)
            if elem:
                if elem.name == 'time':
                    date = elem.get('datetime', elem.get_text().strip())
                elif elem.name == 'meta':
                    date = elem.get('content', '')
                else:
                    date = elem.get_text().strip()
                break
        
        return {
            'product_name': product_name,
            'rating': rating,
            'text': text,
            'date': date,
            'reviewer': reviewer,
            'source': 'Influenster',
            'scraped_date': datetime.now().isoformat()
        }
    
    def _extract_product_name(self, url):
        """Extract product name from URL"""
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
        success_count = 0
        
        for product in product_list:
            try:
                if isinstance(product, dict):
                    url = product.get('url')
                else:
                    url = product
                
                reviews = self.scrape_product_reviews(url, max_pages)
                all_reviews.extend(reviews)
                
                if reviews:
                    success_count += 1
                
                # Longer delay between products [citation:7]
                self._random_delay(5, 8)
                
            except Exception as e:
                print(f"❌ Failed to scrape {product}: {e}")
                continue
        
        # Save to CSV
        if all_reviews:
            df = pd.DataFrame(all_reviews)
            filename = f"data/reviews/influenster_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"\n✅ Saved {len(all_reviews)} reviews to {filename}")
            
            # Save a sample for quick viewing
            sample_file = f"data/reviews/influenster_reviews_sample.csv"
            df.head(20).to_csv(sample_file, index=False)
            print(f"✅ Sample (20 reviews) saved to {sample_file}")
        else:
            print("\n❌ No reviews were collected!")
        
        return all_reviews


def main():
    """Main function to run the scraper"""
    print("=" * 70)
    print("🔍 ENHANCED INFLUENSTER BEAUTY PRODUCT REVIEW SCRAPER")
    print("=" * 70)
    
    # Install required packages if missing
    try:
        from fake_useragent import UserAgent
    except ImportError:
        print("\n📦 Installing required package: fake-useragent")
        import subprocess
        subprocess.check_call(['pip', 'install', 'fake-useragent'])
        print("✅ Installation complete. Please run the script again.")
        return
    
    scraper = EnhancedInfluensterScraper()
    
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
        print("⚠️  This may take several minutes due to anti-detection delays.")
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