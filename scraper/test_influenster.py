"""
Simple test script to verify Influenster scraping works
"""
import requests
from bs4 import BeautifulSoup
import sys

def test_connection(url):
    """Test if we can connect to Influenster"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ Connected successfully: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"📄 Page title: {title.text[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_url = "https://www.influenster.com/reviews/cerave-hydrating-facial-cleanser"
    print(f"Testing connection to: {test_url}")
    test_connection(test_url)