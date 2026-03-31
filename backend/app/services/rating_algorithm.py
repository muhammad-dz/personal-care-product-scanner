"""
Product Rating Algorithm for Personal Care Products
With Skin Type Personalization
"""
import math
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ProductRatingAlgorithm:
    """
    Rates personal care products based on ingredient composition
    With personalized adjustments for different skin types
    """
    
    def __init__(self):
        # Load ingredient safety database
        self.ingredient_db = self._load_ingredient_database()
        
        # High-risk ingredients
        self.high_risk_ingredients = {
            'methylparaben': {'risk': 'high', 'category': 'paraben', 'reason': 'Endocrine disruptor, potential reproductive toxicity'},
            'propylparaben': {'risk': 'high', 'category': 'paraben', 'reason': 'Endocrine disruptor, potential reproductive toxicity'},
            'butylparaben': {'risk': 'high', 'category': 'paraben', 'reason': 'Endocrine disruptor, potential reproductive toxicity'},
            'sodium lauryl sulfate': {'risk': 'medium', 'category': 'sulfate', 'reason': 'Skin and eye irritation, can strip natural oils'},
            'sodium laureth sulfate': {'risk': 'medium', 'category': 'sulfate', 'reason': 'Skin irritation, potentially contaminated'},
            'fragrance': {'risk': 'medium', 'category': 'fragrance', 'reason': 'Common allergen, may contain phthalates'},
            'parfum': {'risk': 'medium', 'category': 'fragrance', 'reason': 'Common allergen, may contain phthalates'},
            'alcohol denat': {'risk': 'medium', 'category': 'alcohol', 'reason': 'Can be drying and irritating'},
            'denatured alcohol': {'risk': 'medium', 'category': 'alcohol', 'reason': 'Can be drying and irritating'},
            'phthalate': {'risk': 'high', 'category': 'phthalate', 'reason': 'Endocrine disruptor, reproductive toxicity'},
            'triclosan': {'risk': 'high', 'category': 'antimicrobial', 'reason': 'Endocrine disruptor, antibiotic resistance'},
            'oxybenzone': {'risk': 'high', 'category': 'sunscreen', 'reason': 'Endocrine disruptor, skin allergen'},
            'dimethicone': {'risk': 'low', 'category': 'silicone', 'reason': 'Can be occlusive, may clog pores for some'},
        }
        
        # Beneficial ingredients
        self.beneficial_ingredients = {
            'glycerin': {'benefit': 'Moisturizing', 'points': 5},
            'hyaluronic acid': {'benefit': 'Deep hydration', 'points': 8},
            'sodium hyaluronate': {'benefit': 'Deep hydration', 'points': 8},
            'niacinamide': {'benefit': 'Brightening, barrier repair', 'points': 10},
            'ceramide': {'benefit': 'Barrier repair', 'points': 8},
            'ceramide np': {'benefit': 'Barrier repair', 'points': 8},
            'squalane': {'benefit': 'Moisturizing', 'points': 6},
            'shea butter': {'benefit': 'Nourishing', 'points': 5},
            'panthenol': {'benefit': 'Soothing, moisturizing', 'points': 5},
            'aloe vera': {'benefit': 'Soothing, hydrating', 'points': 5},
            'vitamin e': {'benefit': 'Antioxidant', 'points': 5},
            'tocopherol': {'benefit': 'Antioxidant', 'points': 5},
            'salicylic acid': {'benefit': 'Exfoliating, acne-fighting', 'points': 7},
            'glycolic acid': {'benefit': 'Exfoliating', 'points': 7},
            'lactic acid': {'benefit': 'Gentle exfoliating', 'points': 6},
            'retinol': {'benefit': 'Anti-aging', 'points': 8},
            'water': {'benefit': 'Hydrating base', 'points': 2},
        }
        
        # Skin type specific adjustments
        self.skin_type_adjustments = {
            'sensitive': {
                'penalties': {
                    'alcohol': -25, 'fragrance': -20, 'parfum': -20,
                    'essential oil': -15, 'denatured alcohol': -25,
                    'sodium lauryl sulfate': -15, 'sodium laureth sulfate': -12,
                    'methylparaben': -10, 'propylparaben': -10,
                    'dimethicone': -5, 'phthalate': -15
                },
                'bonuses': {
                    'panthenol': 8, 'aloe vera': 8, 'ceramide': 10,
                    'niacinamide': 8, 'glycerin': 5, 'hyaluronic acid': 8,
                    'squalane': 6, 'shea butter': 5
                },
                'description': 'Sensitive skin needs gentle, fragrance-free products'
            },
            'dry': {
                'penalties': {
                    'alcohol': -20, 'denatured alcohol': -20, 'sodium lauryl sulfate': -12,
                    'salicylic acid': -5, 'glycolic acid': -5, 'benzoyl peroxide': -10,
                    'fragrance': -5
                },
                'bonuses': {
                    'glycerin': 10, 'hyaluronic acid': 12, 'squalane': 10,
                    'shea butter': 10, 'ceramide': 10, 'panthenol': 8,
                    'aloe vera': 5, 'lanolin': 5
                },
                'description': 'Dry skin needs intense hydration and barrier repair'
            },
            'oily': {
                'penalties': {
                    'shea butter': -8, 'coconut oil': -8, 'mineral oil': -10,
                    'lanolin': -8, 'dimethicone': -5, 'paraffin': -10,
                    'petrolatum': -10
                },
                'bonuses': {
                    'salicylic acid': 12, 'niacinamide': 10, 'glycolic acid': 8,
                    'lactic acid': 8, 'zinc': 10, 'tea tree oil': 8,
                    'benzoyl peroxide': 10, 'retinol': 8, 'clay': 5
                },
                'description': 'Oily skin benefits from exfoliants and lightweight formulas'
            },
            'combination': {
                'penalties': {
                    'alcohol': -10, 'shea butter': -5, 'mineral oil': -5,
                    'sodium lauryl sulfate': -8
                },
                'bonuses': {
                    'niacinamide': 10, 'glycerin': 5, 'hyaluronic acid': 6,
                    'salicylic acid': 8, 'ceramide': 6
                },
                'description': 'Combination skin needs balance of hydration and oil control'
            },
            'normal': {
                'penalties': {
                    'alcohol': -5, 'fragrance': -3
                },
                'bonuses': {
                    'glycerin': 5, 'hyaluronic acid': 6, 'niacinamide': 6
                },
                'description': 'Normal skin works well with most formulas'
            }
        }
        
        # Concern-specific adjustments
        self.concern_adjustments = {
            'acne': {
                'penalties': {
                    'coconut oil': -12, 'shea butter': -8, 'mineral oil': -10,
                    'lanolin': -8, 'isopropyl myristate': -10
                },
                'bonuses': {
                    'salicylic acid': 15, 'benzoyl peroxide': 15, 'niacinamide': 12,
                    'zinc': 10, 'tea tree oil': 10, 'retinol': 10, 'sulfur': 8
                }
            },
            'aging': {
                'penalties': {
                    'alcohol': -10, 'fragrance': -5
                },
                'bonuses': {
                    'retinol': 15, 'vitamin c': 15, 'ascorbic acid': 15,
                    'niacinamide': 12, 'peptide': 12, 'hyaluronic acid': 10,
                    'ceramide': 10, 'squalane': 8, 'ferulic acid': 10
                }
            },
            'redness': {
                'penalties': {
                    'alcohol': -20, 'fragrance': -15, 'essential oil': -15,
                    'sodium lauryl sulfate': -12, 'peppermint': -15
                },
                'bonuses': {
                    'niacinamide': 15, 'panthenol': 12, 'aloe vera': 12,
                    'ceramide': 10, 'centella asiatica': 12, 'azelaic acid': 10,
                    'green tea extract': 8
                }
            },
            'hyperpigmentation': {
                'penalties': {
                    'alcohol': -8, 'fragrance': -5
                },
                'bonuses': {
                    'niacinamide': 15, 'vitamin c': 15, 'kojic acid': 12,
                    'arbutin': 12, 'azelaic acid': 10, 'tranexamic acid': 10,
                    'lactic acid': 8, 'glycolic acid': 8
                }
            }
        }
    
    def _load_ingredient_database(self) -> Dict:
        """Load ingredient safety database"""
        db_file = Path("data/ingredient_database.json")
        if db_file.exists():
            with open(db_file, 'r') as f:
                return json.load(f)
        return {}
    
    def detect_risk_ingredients(self, ingredients: List[str]) -> Tuple[List[Dict], int]:
        """Detect high-risk ingredients"""
        detected_risks = []
        total_risk = 0
        
        for ingredient in ingredients:
            if not ingredient:
                continue
            ingredient_lower = ingredient.lower()
            
            for risk_name, risk_info in self.high_risk_ingredients.items():
                if risk_name in ingredient_lower:
                    points = 10 if risk_info['risk'] == 'high' else 5 if risk_info['risk'] == 'medium' else 2
                    detected_risks.append({
                        'ingredient': ingredient,
                        'risk_category': risk_info['category'],
                        'risk_level': risk_info['risk'],
                        'reason': risk_info['reason'],
                        'points_deducted': points
                    })
                    total_risk += points
                    break
        
        return detected_risks, total_risk
    
    def detect_beneficial_ingredients(self, ingredients: List[str]) -> Tuple[List[Dict], int]:
        """Detect beneficial ingredients"""
        detected_benefits = []
        total_benefit = 0
        
        for ingredient in ingredients:
            if not ingredient:
                continue
            ingredient_lower = ingredient.lower()
            
            for benefit_name, benefit_info in self.beneficial_ingredients.items():
                if benefit_name in ingredient_lower:
                    detected_benefits.append({
                        'ingredient': ingredient,
                        'benefit': benefit_info['benefit'],
                        'points_added': benefit_info['points']
                    })
                    total_benefit += benefit_info['points']
                    break
        
        return detected_benefits, total_benefit
    
    def calculate_product_rating(self, 
                                product_name: str,
                                ingredients: List[str],
                                product_type: str = "unknown",
                                skin_type: str = "normal",
                                concerns: List[str] = None) -> Dict[str, Any]:
        """Calculate product rating with skin type personalization"""
        if concerns is None:
            concerns = []
        
        # Base score starts at 70
        base_score = 70
        
        # Detect risks and benefits
        risks, risk_points = self.detect_risk_ingredients(ingredients)
        benefits, benefit_points = self.detect_beneficial_ingredients(ingredients)
        
        # Calculate base score
        total_score = base_score - (risk_points * 2) + benefit_points
        
        # Apply skin type adjustments
        skin_adjustments = self.skin_type_adjustments.get(skin_type, self.skin_type_adjustments['normal'])
        skin_penalty = 0
        skin_bonus = 0
        applied_penalties = []
        applied_bonuses = []
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Apply skin type penalties
            for bad_ing, penalty in skin_adjustments['penalties'].items():
                if bad_ing in ingredient_lower:
                    skin_penalty += penalty
                    applied_penalties.append({
                        'ingredient': ingredient,
                        'reason': f'May be problematic for {skin_type} skin',
                        'adjustment': penalty
                    })
                    break
            
            # Apply skin type bonuses
            for good_ing, bonus in skin_adjustments['bonuses'].items():
                if good_ing in ingredient_lower:
                    skin_bonus += bonus
                    applied_bonuses.append({
                        'ingredient': ingredient,
                        'reason': f'Beneficial for {skin_type} skin',
                        'adjustment': bonus
                    })
                    break
        
        # Apply concern-specific adjustments
        concern_penalty = 0
        concern_bonus = 0
        applied_concern_penalties = []
        applied_concern_bonuses = []
        
        for concern in concerns:
            if concern in self.concern_adjustments:
                adj = self.concern_adjustments[concern]
                for ingredient in ingredients:
                    ingredient_lower = ingredient.lower()
                    
                    for bad_ing, penalty in adj['penalties'].items():
                        if bad_ing in ingredient_lower:
                            concern_penalty += penalty
                            applied_concern_penalties.append({
                                'ingredient': ingredient,
                                'concern': concern,
                                'reason': f'May worsen {concern}',
                                'adjustment': penalty
                            })
                            break
                    
                    for good_ing, bonus in adj['bonuses'].items():
                        if good_ing in ingredient_lower:
                            concern_bonus += bonus
                            applied_concern_bonuses.append({
                                'ingredient': ingredient,
                                'concern': concern,
                                'reason': f'Helps with {concern}',
                                'adjustment': bonus
                            })
                            break
        
        # Calculate final personalized score
        personalized_score = total_score + skin_penalty + skin_bonus + concern_penalty + concern_bonus
        personalized_score = max(0, min(100, round(personalized_score)))
        
        # Standard score (without personalization)
        standard_score = max(0, min(100, round(total_score)))
        
        # Determine ratings
        standard_rating = self._get_rating(standard_score)
        personalized_rating = self._get_rating(personalized_score)
        
        # Generate personalized recommendation
        recommendation = self._generate_personalized_recommendation(
            standard_score, personalized_score, skin_type, concerns,
            applied_penalties, applied_bonuses,
            applied_concern_penalties, applied_concern_bonuses
        )
        
        return {
            'product_name': product_name,
            'total_ingredients': len(ingredients),
            'risk_ingredients': len(risks),
            'beneficial_ingredients': len(benefits),
            'risk_details': risks,
            'benefit_details': benefits,
            'risk_points': risk_points,
            'benefit_points': benefit_points,
            'standard_score': standard_score,
            'standard_rating': standard_rating,
            'personalized_score': personalized_score,
            'personalized_rating': personalized_rating,
            'skin_type': skin_type,
            'concerns': concerns,
            'skin_adjustments': {
                'penalty_total': skin_penalty,
                'bonus_total': skin_bonus,
                'applied_penalties': applied_penalties,
                'applied_bonuses': applied_bonuses
            },
            'concern_adjustments': {
                'penalty_total': concern_penalty,
                'bonus_total': concern_bonus,
                'applied_penalties': applied_concern_penalties,
                'applied_bonuses': applied_concern_bonuses
            },
            'recommendation': recommendation,
            'score_difference': personalized_score - standard_score
        }
    
    def _get_rating(self, score: int) -> str:
        """Get rating category from score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Poor"
        else:
            return "Avoid"
    
    def _generate_personalized_recommendation(self, standard_score, personalized_score,
                                              skin_type, concerns, penalties, bonuses,
                                              concern_penalties, concern_bonuses) -> str:
        """Generate personalized recommendation"""
        diff = personalized_score - standard_score
        
        if diff > 15:
            return f"Excellent for {skin_type} skin! This product is especially well-suited for your skin type."
        elif diff > 5:
            return f"Good choice for {skin_type} skin. This product scores {personalized_score}/100 for your skin type, which is {diff} points higher than the general rating."
        elif diff < -15:
            return f"Caution: This product may not be ideal for {skin_type} skin. It scores {abs(diff)} points lower for your skin type."
        elif diff < -5:
            return f"This product may cause some issues for {skin_type} skin. The standard rating is {standard_score}, but it's {abs(diff)} points lower for your skin type."
        else:
            return f"This product is reasonably suitable for {skin_type} skin. The personalized score ({personalized_score}) is close to the general rating ({standard_score})."


class BatchRatingProcessor:
    """Process multiple products"""
    
    def __init__(self):
        self.algorithm = ProductRatingAlgorithm()
    
    def rate_products(self, products: List[Dict], skin_type: str = "normal", concerns: List[str] = None) -> List[Dict]:
        """Rate multiple products with personalization"""
        results = []
        for product in products:
            ingredients = product.get('ingredients', [])
            name = product.get('product_name', 'Unknown')
            rating = self.algorithm.calculate_product_rating(
                name, ingredients, "unknown", skin_type, concerns
            )
            results.append(rating)
        return results