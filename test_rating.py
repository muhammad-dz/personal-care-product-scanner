from backend.app.services.rating_algorithm import ProductRatingAlgorithm

def test_rating_algorithm():
    algorithm = ProductRatingAlgorithm()
    
    test_cases = [
        {
            'name': 'Excellent Moisturizer',
            'ingredients': [
                'Water', 'Glycerin', 'Hyaluronic Acid', 'Niacinamide', 
                'Ceramide NP', 'Squalane', 'Panthenol', 'Vitamin E'
            ],
            'type': 'moisturizer'
        },
        {
            'name': 'Good Cleanser',
            'ingredients': [
                'Water', 'Glycerin', 'Cocamidopropyl Betaine', 
                'Aloe Vera', 'Panthenol'
            ],
            'type': 'cleanser'
        },
        {
            'name': 'Moderate Product',
            'ingredients': [
                'Water', 'Sodium Laureth Sulfate', 'Fragrance', 
                'Glycerin', 'Dimethicone'
            ],
            'type': 'cleanser'
        },
        {
            'name': 'Poor Product',
            'ingredients': [
                'Water', 'Sodium Lauryl Sulfate', 'Methylparaben', 
                'Propylparaben', 'Fragrance', 'Alcohol Denat'
            ],
            'type': 'cleanser'
        },
        {
            'name': 'Avoid Product',
            'ingredients': [
                'Water', 'Phthalate', 'Quaternium-15', 
                'Triclosan', 'Oxybenzone', 'Hydroquinone'
            ],
            'type': 'unknown'
        }
    ]
    
    print("="*70)
    print("TESTING THE PRODUCT RATING SYSTEM")
    print("="*70)
    
    for test in test_cases:
        print(f"\nProduct: {test['name']}")
        print(f"Ingredients: {', '.join(test['ingredients'][:5])}{'...' if len(test['ingredients']) > 5 else ''}")
        
        result = algorithm.calculate_product_rating(
            test['name'],
            test['ingredients'],
            test['type']
        )
        
        print(f"\n   Score: {result['final_score']}/100 - {result['rating']}")
        print(f"   Potentially risky ingredients: {result['risk_ingredients']}")
        print(f"   Beneficial ingredients found: {result['beneficial_ingredients']}")
        print(f"   Our recommendation: {result['recommendation']}")
        
        if result['risk_details']:
            print("   Main concerns:")
            for risk in result['risk_details'][:2]:
                print(f"     - {risk['ingredient']}: {risk['reason'][:50]}...")
    
    print("\n" + "="*70)
    print("Testing finished")

if __name__ == "__main__":
    test_rating_algorithm()