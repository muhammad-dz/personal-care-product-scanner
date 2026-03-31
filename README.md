# Personal Care Product Safety Scanner

A web application that scans personal care product labels, analyzes ingredient safety, and processes user reviews to help you make informed choices about the products you use.

## Features

- Scan product labels with your camera or upload images
- Check ingredient safety using the Open Beauty Facts database
- See what other customers are saying with sentiment analysis
- Get safety scores and easy-to-understand ratings

## Setup

### Backend Setup

## Product Review Scraper

The project includes a tool that collects reviews from **Influenster**, a popular beauty product review platform.

### What it does:

- Gathers reviews for popular beauty products
- Collects ratings, review text, dates, and reviewer information
- Saves everything to CSV files for analysis
- Includes sample data so you can test without scraping

### How to use it:

````bash
# Test if everything is working first
python scraper/test_influenster.py

# Run the interactive review collector
python scraper/influenster_scraper.py

# Analyze the reviews you've collected
python nlp/analyze_influenster.py

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac or Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m app.main
````
