# Personal Care Product Safety Scanner

A web application that scans personal care product labels, analyzes ingredient safety, and processes user reviews using NLP.

## Features

- OCR scanning of product labels
- Ingredient safety analysis using Open Beauty Facts database
- Sentiment analysis of user reviews
- Safety scoring and visualization

## Setup

### Backend Setup

## 🕷️ Web Scraper for Product Reviews

The project includes a scraper for **Influenster**, a dedicated beauty product review platform.

### Features:

- Scrapes reviews for popular beauty products
- Extracts ratings, review text, dates, and reviewer info
- Saves data to CSV for sentiment analysis
- Includes sample data for testing

### Usage:

````bash
# Test connection first
python scraper/test_influenster.py

# Run interactive scraper
python scraper/influenster_scraper.py

# Analyze scraped reviews
python nlp/analyze_influenster.py

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m app.main
````
