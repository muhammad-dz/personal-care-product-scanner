import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from datetime import datetime

class AmazonReviewScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
        }
        
        self.cosmetic_products = {
            'B01M4MIU8P': 'CeraVe Hydrating Facial Cleanser',
            'B00NRQZ0J2': 'Neutrogena Hydro Boost Water Gel',
            'B0788DVRM1': 'The Ordinary Niacinamide 10% + Zinc 1%',
            'B07RKVXTTN': 'La Roche-Posay Toleriane Double Repair',
            'B01LYN1QH6': 'Cetaphil Gentle Skin Cleanser',
            'B07WC7K4PK': 'Olay Regenerist Retinol 24',
            'B07H2CXDVV': 'Paula\'s Choice 2% BHA Exfoliant',
            'B08HJ4B5B2': 'CeraVe Moisturizing Cream'
        }
    
    def scrape_reviews(self, asin, max_pages=2):
        all_reviews = []
        product_name = self.cosmetic_products.get(asin, "Unknown")
        
        print(f"Looking up: {product_name}")
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_paging_btm_next_{page}?pageNumber={page}"
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                reviews = soup.find_all('div', {'data-hook': 'review'})
                
                for review in reviews:
                    try:
                        rating_elem = review.find('i', {'data-hook': 'review-star-rating'})
                        rating = 0
                        if rating_elem:
                            rating_text = rating_elem.text.strip()
                            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                            if rating_match:
                                rating = float(rating_match.group(1))
                        
                        text_elem = review.find('span', {'data-hook': 'review-body'})
                        text = text_elem.text.strip() if text_elem else ""
                        
                        title_elem = review.find('a', {'data-hook': 'review-title'})
                        title = title_elem.text.strip() if title_elem else ""
                        
                        if text and len(text) > 20:
                            all_reviews.append({
                                'product_asin': asin,
                                'product_name': product_name,
                                'rating': rating,
                                'title': title,
                                'text': text,
                                'date': datetime.now().isoformat()
                            })
                    except:
                        continue
                
                print(f"  Page {page}: found {len(reviews)} reviews")
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"  Something went wrong: {e}")
                break
        
        return all_reviews
    
    def scrape_multiple_products(self, max_pages=2):
        all_reviews = []
        
        for asin in self.cosmetic_products.keys():
            reviews = self.scrape_reviews(asin, max_pages)
            all_reviews.extend(reviews)
            time.sleep(2)
        
        if all_reviews:
            df = pd.DataFrame(all_reviews)
            filename = f"data/reviews/amazon_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"\nSuccess! Saved {len(all_reviews)} reviews to {filename}")
        else:
            print("\nNo reviews were collected. Please try again later.")

if __name__ == "__main__":
    scraper = AmazonReviewScraper()
    scraper.scrape_multiple_products(max_pages=2)