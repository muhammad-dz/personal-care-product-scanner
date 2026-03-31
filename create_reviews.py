import pandas as pd
import random

reviews = []
products = ['CeraVe Cleanser', 'La Roche-Posay', 'Neutrogena', 'Cetaphil']
positive_texts = ['love this product works great amazing', 'my skin feels so soft', 'very hydrating and gentle']
negative_texts = ['caused rash on my face', 'broke me out badly', 'made my skin dry and flaky', 'irritation and burning']
neutral_texts = ['it is okay nothing special', 'decent product works fine']

for i in range(200):
    if i < 100:
        text = random.choice(positive_texts)
        rating = 5
        sentiment = 'positive'
    elif i < 150:
        text = random.choice(neutral_texts)
        rating = 3
        sentiment = 'neutral'
    else:
        text = random.choice(negative_texts)
        rating = 1
        sentiment = 'negative'
    
    reviews.append({
        'product_name': random.choice(products),
        'rating': rating,
        'text': text,
        'sentiment': sentiment,
        'sentiment_score': 0.5 if sentiment == 'positive' else (-0.5 if sentiment == 'negative' else 0),
        'issues': 'rash' if 'rash' in text else ('acne' if 'broke' in text else '')
    })

df = pd.DataFrame(reviews)
df.to_csv('data/reviews/wordcloud_data.csv', index=False)
print(f'Created {len(reviews)} sample reviews with text')
print(f'Positive: {(df["sentiment"] == "positive").sum()}')
print(f'Neutral: {(df["sentiment"] == "neutral").sum()}')
print(f'Negative: {(df["sentiment"] == "negative").sum()}')
