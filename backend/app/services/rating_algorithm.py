"""
Product Rating Algorithm for Personal Care Products
Rates products based on ingredient safety, scientific consensus, and user reports
"""
import math
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path

class ProductRatingAlgorithm:
    """
    Rates personal care products based on ingredient composition
    Score range: 0-100 (higher is safer/better)
    Rating categories: Excellent (80-100), Good (60-79), Moderate (40-59), Poor (20-39), Avoid (0-19)
    """
    
    def __init__(self):
        # Load ingredient safety database
        self.ingredient_db = self._load_ingredient_database()
        
        # High-risk ingredients to flag (common harmful substances)
        self.high_risk_ingredients = {
            # Add to high_risk_ingredients in rating_algorithm.py
'benzophenone': {'risk': 'medium', 'category': 'sunscreen', 'reason': 'Potential endocrine disruptor'},
'homosalate': {'risk': 'medium', 'category': 'sunscreen', 'reason': 'Endocrine disruptor concerns'},
'octocrylene': {'risk': 'medium', 'category': 'sunscreen', 'reason': 'Skin allergen concerns'},
            # Parabens - endocrine disruptors
            'methylparaben': {'risk': 'high', 'category': 'paraben', 'reason': 'Endocrine disruptor, potential reproductive toxicity'},
            'ethylparaben': {'risk': 'high', 'category': 'paraben', 'reason': 'Endocrine disruptor, potential reproductive toxicity'},
            'propylparaben': {'risk': 'high', 'category': 'paraben', 'reason': 'Endocrine disruptor, potential reproductive toxicity'},
            'butylparaben': {'risk': 'high', 'category': 'paraben', 'reason': 'Endocrine disruptor, potential reproductive toxicity'},
            'isobutylparaben': {'risk': 'high', 'category': 'paraben', 'reason': 'Endocrine disruptor, potential reproductive toxicity'},
            
            # Sulfates - skin irritants
            'sodium lauryl sulfate': {'risk': 'medium', 'category': 'sulfate', 'reason': 'Skin and eye irritation, can strip natural oils'},
            'sodium laureth sulfate': {'risk': 'medium', 'category': 'sulfate', 'reason': 'Skin irritation, potentially contaminated with 1,4-dioxane'},
            'ammonium lauryl sulfate': {'risk': 'medium', 'category': 'sulfate', 'reason': 'Skin and eye irritation'},
            
            # Phthalates - endocrine disruptors
            'phthalate': {'risk': 'high', 'category': 'phthalate', 'reason': 'Endocrine disruptor, reproductive toxicity'},
            'diethyl phthalate': {'risk': 'high', 'category': 'phthalate', 'reason': 'Endocrine disruptor, reproductive toxicity'},
            'dibutyl phthalate': {'risk': 'high', 'category': 'phthalate', 'reason': 'Endocrine disruptor, reproductive toxicity'},
            
            # Fragrance - allergen
            'fragrance': {'risk': 'medium', 'category': 'fragrance', 'reason': 'Can contain phthalates, common allergen'},
            'parfum': {'risk': 'medium', 'category': 'fragrance', 'reason': 'Can contain phthalates, common allergen'},
            
            # Formaldehyde releasers
            'quaternium-15': {'risk': 'high', 'category': 'formaldehyde', 'reason': 'Formaldehyde releaser, carcinogen'},
            'dmdm hydantoin': {'risk': 'high', 'category': 'formaldehyde', 'reason': 'Formaldehyde releaser, carcinogen'},
            'diazolidinyl urea': {'risk': 'high', 'category': 'formaldehyde', 'reason': 'Formaldehyde releaser, carcinogen'},
            'imidazolidinyl urea': {'risk': 'high', 'category': 'formaldehyde', 'reason': 'Formaldehyde releaser, carcinogen'},
            
            # Alcohols - drying
            'alcohol denat': {'risk': 'medium', 'category': 'alcohol', 'reason': 'Can be drying and irritating'},
            'denatured alcohol': {'risk': 'medium', 'category': 'alcohol', 'reason': 'Can be drying and irritating'},
            'isopropyl alcohol': {'risk': 'medium', 'category': 'alcohol', 'reason': 'Can be drying and irritating'},
            
            # Silicones - occlusive
            'dimethicone': {'risk': 'low', 'category': 'silicone', 'reason': 'Can be occlusive, may clog pores for some'},
            'cyclomethicone': {'risk': 'low', 'category': 'silicone', 'reason': 'Can be occlusive, may clog pores for some'},
            
            # PEG compounds
            'peg-40': {'risk': 'medium', 'category': 'peg', 'reason': 'May contain ethylene oxide, a carcinogen'},
            'peg-100': {'risk': 'medium', 'category': 'peg', 'reason': 'May contain ethylene oxide, a carcinogen'},
            
            # Other concerning ingredients
            'triclosan': {'risk': 'high', 'category': 'antimicrobial', 'reason': 'Endocrine disruptor, antibiotic resistance'},
            'oxybenzone': {'risk': 'high', 'category': 'sunscreen', 'reason': 'Endocrine disruptor, skin allergen'},
            'octinoxate': {'risk': 'medium', 'category': 'sunscreen', 'reason': 'Endocrine disruptor concerns'},
            'retinyl palmitate': {'risk': 'medium', 'category': 'vitamin_a', 'reason': 'May be phototoxic'},
            'hydroquinone': {'risk': 'high', 'category': 'bleaching', 'reason': 'Carcinogen concerns'},
        }
        
        # Beneficial ingredients that add points
        self.beneficial_ingredients = {
            # Add to beneficial_ingredients
'peptide': {'benefit': 'Collagen support', 'points': 8},
'copper peptide': {'benefit': 'Skin repair', 'points': 9},
'adenosine': {'benefit': 'Anti-aging', 'points': 6},
            # Moisturizers
            'glycerin': {'benefit': 'Moisturizing', 'points': 5},
            'hyaluronic acid': {'benefit': 'Deep hydration', 'points': 8},
            'sodium hyaluronate': {'benefit': 'Deep hydration', 'points': 8},
            'ceramide': {'benefit': 'Barrier repair', 'points': 8},
            'ceramide np': {'benefit': 'Barrier repair', 'points': 8},
            'squalane': {'benefit': 'Moisturizing', 'points': 6},
            'shea butter': {'benefit': 'Nourishing', 'points': 5},
            'cocoa butter': {'benefit': 'Moisturizing', 'points': 4},
            
            # Actives
            'niacinamide': {'benefit': 'Brightening, barrier repair', 'points': 10},
            'vitamin c': {'benefit': 'Antioxidant, brightening', 'points': 10},
            'ascorbic acid': {'benefit': 'Antioxidant, brightening', 'points': 10},
            'retinol': {'benefit': 'Anti-aging', 'points': 8},
            'salicylic acid': {'benefit': 'Exfoliating, acne-fighting', 'points': 7},
            'glycolic acid': {'benefit': 'Exfoliating', 'points': 7},
            'lactic acid': {'benefit': 'Gentle exfoliating', 'points': 6},
            'azelaic acid': {'benefit': 'Acne-fighting, brightening', 'points': 8},
            'bakuchiol': {'benefit': 'Gentle retinol alternative', 'points': 7},
            
            # Soothing
            'aloe vera': {'benefit': 'Soothing, hydrating', 'points': 5},
            'allantoin': {'benefit': 'Soothing, healing', 'points': 5},
            'panthenol': {'benefit': 'Soothing, moisturizing', 'points': 5},
            'centella asiatica': {'benefit': 'Soothing, healing', 'points': 7},
            'madecassoside': {'benefit': 'Soothing, healing', 'points': 7},
            'beta-glucan': {'benefit': 'Soothing, moisturizing', 'points': 6},
            
            # Antioxidants
            'vitamin e': {'benefit': 'Antioxidant', 'points': 5},
            'tocopherol': {'benefit': 'Antioxidant', 'points': 5},
            'green tea extract': {'benefit': 'Antioxidant', 'points': 6},
            'resveratrol': {'benefit': 'Antioxidant', 'points': 6},
            'ferulic acid': {'benefit': 'Antioxidant', 'points': 6},
            
            # Minerals
            'zinc oxide': {'benefit': 'Mineral sunscreen, soothing', 'points': 7},
            'titanium dioxide': {'benefit': 'Mineral sunscreen', 'points': 6},
        }
        
        # Ingredient categories that affect overall score
        self.category_weights = {
            'paraben': -15,
            'phthalate': -20,
            'formaldehyde': -25,
            'sulfate': -8,
            'fragrance': -5,
            'alcohol': -3,
            'silicone': -2,
            'peg': -5,
            'antimicrobial': -10,
            'sunscreen': -3,
            'vitamin_a': -3,
            'bleaching': -15,
        }
    
    def _load_ingredient_database(self) -> Dict:
        """Load or create ingredient safety database"""
        db_file = Path("data/ingredient_database.json")
        
        if db_file.exists():
            with open(db_file, 'r') as f:
                return json.load(f)
        else:
            # Return empty dict - will use hardcoded data
            return {}
    
    def normalize_ingredient_name(self, ingredient: str) -> str:
        """
        Normalize ingredient name for matching
        """
        if not isinstance(ingredient, str):
            return ""
        
        # Convert to lowercase and strip
        normalized = ingredient.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes = ['sodium ', 'potassium ', 'calcium ', 'magnesium ', 'zinc ']
        suffixes = [' extract', ' oil', ' acid', ' ester', ' polymer', ' derivative']
        
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        return normalized
    
    def detect_risk_ingredients(self, ingredients: List[str]) -> Tuple[List[Dict], int]:
        """
        Detect high-risk ingredients and calculate risk score
        Returns: (list of detected risks, total risk points)
        """
        detected_risks = []
        total_risk = 0
        
        for ingredient in ingredients:
            if not ingredient:
                continue
            
            ingredient_lower = ingredient.lower()
            normalized = self.normalize_ingredient_name(ingredient)
            
            # Check direct matches
            for risk_name, risk_info in self.high_risk_ingredients.items():
                if risk_name in ingredient_lower or risk_name in normalized:
                    # Calculate risk points based on severity
                    if risk_info['risk'] == 'high':
                        points = 10
                    elif risk_info['risk'] == 'medium':
                        points = 5
                    else:
                        points = 2
                    
                    detected_risks.append({
                        'ingredient': ingredient,
                        'risk_category': risk_info['category'],
                        'risk_level': risk_info['risk'],
                        'reason': risk_info['reason'],
                        'points_deducted': points
                    })
                    
                    total_risk += points
                    
                    # Apply category weight
                    category = risk_info['category']
                    if category in self.category_weights:
                        total_risk += abs(self.category_weights[category])  # Add as positive risk
            
            # Check for partial matches (e.g., "paraben" in "methylparaben")
            for category, weight in self.category_weights.items():
                if category in ingredient_lower:
                    # Already counted via direct match? This catches variants
                    if not any(r['risk_category'] == category for r in detected_risks):
                        detected_risks.append({
                            'ingredient': ingredient,
                            'risk_category': category,
                            'risk_level': 'medium',
                            'reason': f'Contains {category} (potential concern)',
                            'points_deducted': abs(weight)
                        })
                        total_risk += abs(weight)
        
        return detected_risks, total_risk
    
    def detect_beneficial_ingredients(self, ingredients: List[str]) -> Tuple[List[Dict], int]:
        """
        Detect beneficial ingredients and calculate benefit points
        Returns: (list of detected benefits, total benefit points)
        """
        detected_benefits = []
        total_benefit = 0
        
        for ingredient in ingredients:
            if not ingredient:
                continue
            
            ingredient_lower = ingredient.lower()
            normalized = self.normalize_ingredient_name(ingredient)
            
            for benefit_name, benefit_info in self.beneficial_ingredients.items():
                if benefit_name in ingredient_lower or benefit_name in normalized:
                    detected_benefits.append({
                        'ingredient': ingredient,
                        'benefit': benefit_info['benefit'],
                        'points_added': benefit_info['points']
                    })
                    
                    total_benefit += benefit_info['points']
                    break  # Only count each ingredient once
        
        return detected_benefits, total_benefit
    
    def calculate_product_rating(self, 
                                product_name: str,
                                ingredients: List[str],
                                product_type: str = "unknown") -> Dict[str, Any]:
        """
        Calculate overall product rating based on ingredients
        """
        # Base score starts at 70 (average product)
        base_score = 70
        
        # Detect risks and benefits
        risks, risk_points = self.detect_risk_ingredients(ingredients)
        benefits, benefit_points = self.detect_beneficial_ingredients(ingredients)
        
        # Calculate total score
        # Each risk point deducts 2 from score (to make impact significant)
        # Each benefit point adds 1 to score
        total_score = base_score - (risk_points * 2) + benefit_points
        
        # Apply product type modifiers
        type_modifiers = {
            'cleanser': {'max_score': 85, 'min_beneficial_threshold': 2},
            'moisturizer': {'max_score': 95, 'min_beneficial_threshold': 3},
            'serum': {'max_score': 98, 'min_beneficial_threshold': 4},
            'sunscreen': {'max_score': 90, 'min_beneficial_threshold': 2},
            'toner': {'max_score': 80, 'min_beneficial_threshold': 1},
            'mask': {'max_score': 85, 'min_beneficial_threshold': 2},
            'unknown': {'max_score': 90, 'min_beneficial_threshold': 2}
        }
        
        modifier = type_modifiers.get(product_type.lower(), type_modifiers['unknown'])
        total_score = min(total_score, modifier['max_score'])
        total_score = max(total_score, 0)  # Don't go below 0
        
        # Round to nearest integer
        final_score = round(total_score)
        
        # Determine rating category
        if final_score >= 80:
            rating = "Excellent"
        elif final_score >= 60:
            rating = "Good"
        elif final_score >= 40:
            rating = "Moderate"
        elif final_score >= 20:
            rating = "Poor"
        else:
            rating = "Avoid"
        
        # Count risk categories
        risk_categories = {}
        for risk in risks:
            cat = risk['risk_category']
            risk_categories[cat] = risk_categories.get(cat, 0) + 1
        
        # Count benefit categories
        benefit_categories = {}
        for benefit in benefits:
            cat = benefit['benefit']
            benefit_categories[cat] = benefit_categories.get(cat, 0) + 1
        
        return {
            'product_name': product_name,
            'total_ingredients': len(ingredients),
            'risk_ingredients': len(risks),
            'beneficial_ingredients': len(benefits),
            'risk_details': risks,
            'benefit_details': benefits,
            'risk_points': risk_points,
            'benefit_points': benefit_points,
            'raw_score': total_score,
            'final_score': final_score,
            'rating': rating,
            'risk_categories': risk_categories,
            'benefit_categories': benefit_categories,
            'recommendation': self._generate_recommendation(risks, benefits, final_score)
        }
    
    def _generate_recommendation(self, risks: List[Dict], benefits: List[Dict], score: int) -> str:
        """Generate user-friendly recommendation"""
        if score >= 80:
            if len(risks) == 0:
                return "Excellent choice! This product contains beneficial ingredients with no concerning additives."
            else:
                return "Good overall formula with minor concerns. Consider patch testing."
        
        elif score >= 60:
            if len(risks) <= 2:
                return "Solid product with some beneficial ingredients. May work well for most skin types."
            else:
                return "Decent formula but contains some ingredients that may be irritating for sensitive skin."
        
        elif score >= 40:
            if len(risks) <= 3:
                return "Mixed formula. Has some benefits but also contains concerning ingredients. Proceed with caution."
            else:
                return "Contains multiple concerning ingredients. Consider alternatives with cleaner formulations."
        
        else:
            return "NOT RECOMMENDED. Contains high-risk ingredients linked to health concerns. Avoid this product."


class BatchRatingProcessor:
    """Process multiple products for rating"""
    
    def __init__(self):
        self.algorithm = ProductRatingAlgorithm()
    
    def rate_products(self, products: List[Dict]) -> List[Dict]:
        """Rate multiple products"""
        results = []
        
        for product in products:
            ingredients = product.get('ingredients', [])
            name = product.get('product_name', 'Unknown')
            p_type = product.get('product_type', 'unknown')
            
            rating = self.algorithm.calculate_product_rating(name, ingredients, p_type)
            results.append(rating)
        
        return results
    
    def get_top_rated(self, products: List[Dict], n: int = 5) -> List[Dict]:
        """Get top N rated products"""
        rated = self.rate_products(products)
        return sorted(rated, key=lambda x: x['final_score'], reverse=True)[:n]
    
    def get_worst_rated(self, products: List[Dict], n: int = 5) -> List[Dict]:
        """Get worst N rated products"""
        rated = self.rate_products(products)
        return sorted(rated, key=lambda x: x['final_score'])[:n]


# Example usage
if __name__ == "__main__":
    # Test the algorithm
    algorithm = ProductRatingAlgorithm()
    
    # Test with some example products
    test_products = [
        {
            'name': 'Clean Beauty Moisturizer',
            'ingredients': ['Water', 'Glycerin', 'Hyaluronic Acid', 'Niacinamide', 'Ceramide NP', 'Shea Butter'],
            'type': 'moisturizer'
        },
        {
            'name': 'Generic Drugstore Cleanser',
            'ingredients': ['Water', 'Sodium Lauryl Sulfate', 'Fragrance', 'Paraben', 'Alcohol Denat'],
            'type': 'cleanser'
        },
        {
            'name': 'Natural Face Cream',
            'ingredients': ['Aloe Vera', 'Jojoba Oil', 'Vitamin E', 'Green Tea Extract', 'Panthenol'],
            'type': 'moisturizer'
        }
    ]
    
    for product in test_products:
        print(f"\n{'='*60}")
        print(f"Product: {product['name']}")
        print(f"Ingredients: {', '.join(product['ingredients'])}")
        
        result = algorithm.calculate_product_rating(
            product['name'], 
            product['ingredients'], 
            product['type']
        )
        
        print(f"\nScore: {result['final_score']}/100 - {result['rating']}")
        print(f"Risk ingredients found: {result['risk_ingredients']}")
        print(f"Beneficial ingredients: {result['beneficial_ingredients']}")
        print(f"Recommendation: {result['recommendation']}")
        
        if result['risk_details']:
            print("\nRisks detected:")
            for risk in result['risk_details'][:3]:
                print(f"  • {risk['ingredient']}: {risk['reason']}")