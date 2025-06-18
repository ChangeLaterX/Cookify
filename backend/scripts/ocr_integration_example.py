"""
Example integration: How to use the ingredient cache with OCR services.

This file demonstrates how the cached ingredient data can be integrated
with the OCR receipt processing to improve ingredient recognition.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher

from scripts.ingredient_loader import (
    get_ingredient_names_for_ocr,
    search_ingredient_matches,
    get_ingredient_cache_stats
)

logger = logging.getLogger(__name__)


class IngredientMatcher:
    """
    Advanced ingredient matching for OCR text processing.
    
    This class provides fuzzy matching capabilities to match OCR-extracted
    text against the cached ingredient database.
    """
    
    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize the ingredient matcher.
        
        Args:
            similarity_threshold: Minimum similarity score for fuzzy matching (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.ingredient_names = []
        self._load_ingredients()
    
    def _load_ingredients(self) -> None:
        """Load ingredients from the cache."""
        try:
            self.ingredient_names = get_ingredient_names_for_ocr()
            logger.info(f"Loaded {len(self.ingredient_names)} ingredients for matching")
        except Exception as e:
            logger.error(f"Failed to load ingredients: {str(e)}")
            self.ingredient_names = []
    
    def refresh_ingredients(self) -> bool:
        """
        Refresh the ingredient list from the cache.
        
        Returns:
            bool: True if successful, False if failed
        """
        try:
            self._load_ingredients()
            return len(self.ingredient_names) > 0
        except Exception as e:
            logger.error(f"Failed to refresh ingredients: {str(e)}")
            return False
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher.
        
        Args:
            text1: First string
            text2: Second string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def clean_ocr_text(self, text: str) -> str:
        """
        Clean OCR text for better matching.
        
        Args:
            text: Raw OCR text
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\s\-\']', ' ', text)
        
        # Fix common OCR errors
        replacements = {
            'l': 'i',  # Common OCR error
            '0': 'o',  # Zero to O
            '1': 'l',  # One to L
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.lower()
    
    def find_exact_matches(self, ocr_text: str) -> List[str]:
        """
        Find exact ingredient matches in OCR text.
        
        Args:
            ocr_text: OCR extracted text
            
        Returns:
            List[str]: List of exactly matching ingredient names
        """
        matches = []
        ocr_lower = ocr_text.lower()
        
        for ingredient in self.ingredient_names:
            if ingredient.lower() in ocr_lower:
                matches.append(ingredient)
        
        return matches
    
    def find_fuzzy_matches(self, ocr_text: str, max_matches: int = 10) -> List[Tuple[str, float]]:
        """
        Find fuzzy ingredient matches in OCR text.
        
        Args:
            ocr_text: OCR extracted text
            max_matches: Maximum number of matches to return
            
        Returns:
            List[Tuple[str, float]]: List of (ingredient_name, similarity_score) tuples
        """
        matches = []
        cleaned_text = self.clean_ocr_text(ocr_text)
        words = cleaned_text.split()
        
        for ingredient in self.ingredient_names:
            best_similarity = 0.0
            ingredient_lower = ingredient.lower()
            ingredient_words = ingredient_lower.split()
            
            # Check similarity with full text
            similarity = self.calculate_similarity(cleaned_text, ingredient_lower)
            best_similarity = max(best_similarity, similarity)
            
            # Check similarity with individual words
            for word in words:
                for ing_word in ingredient_words:
                    similarity = self.calculate_similarity(word, ing_word)
                    best_similarity = max(best_similarity, similarity)
            
            # Check if any ingredient word appears in OCR text
            for ing_word in ingredient_words:
                if ing_word in cleaned_text:
                    best_similarity = max(best_similarity, 0.8)  # High score for word matches
            
            if best_similarity >= self.similarity_threshold:
                matches.append((ingredient, best_similarity))
        
        # Sort by similarity score (descending) and return top matches
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:max_matches]
    
    def match_ingredients_in_text(self, ocr_text: str) -> Dict[str, any]:
        """
        Comprehensive ingredient matching in OCR text.
        
        Args:
            ocr_text: OCR extracted text
            
        Returns:
            Dict containing exact matches, fuzzy matches, and metadata
        """
        # Find exact matches first
        exact_matches = self.find_exact_matches(ocr_text)
        
        # Find fuzzy matches
        fuzzy_matches = self.find_fuzzy_matches(ocr_text)
        
        # Remove fuzzy matches that are already exact matches
        fuzzy_only = [
            (name, score) for name, score in fuzzy_matches 
            if name not in exact_matches
        ]
        
        return {
            "ocr_text": ocr_text,
            "exact_matches": exact_matches,
            "fuzzy_matches": fuzzy_only,
            "total_matches": len(exact_matches) + len(fuzzy_only),
            "cache_stats": get_ingredient_cache_stats(),
            "similarity_threshold": self.similarity_threshold
        }


def demonstrate_ocr_integration():
    """
    Demonstration of how to integrate ingredient matching with OCR.
    
    This function shows example usage that could be integrated into
    the OCR service for receipt processing.
    """
    # Initialize the matcher
    matcher = IngredientMatcher(similarity_threshold=0.6)
    
    # Example OCR text from a receipt
    sample_ocr_texts = [
        "chicken breast 2.5 lbs $12.99",
        "organic tomatoes 1 lb $3.49", 
        "brown rice 2 lb bag $4.99",
        "greek yogurt 32oz $5.99",
        "olive oil extra virgin 500ml $8.99",
        "bell peppers red 3 count $2.99"
    ]
    
    logger.info("=== OCR Ingredient Matching Demonstration ===")
    
    for i, ocr_text in enumerate(sample_ocr_texts, 1):
        logger.info(f"\n--- Sample {i} ---")
        logger.info(f"OCR Text: '{ocr_text}'")
        
        # Match ingredients
        results = matcher.match_ingredients_in_text(ocr_text)
        
        logger.info(f"Exact matches: {results['exact_matches']}")
        logger.info(f"Fuzzy matches: {[(name, f'{score:.2f}') for name, score in results['fuzzy_matches'][:3]]}")
        logger.info(f"Total matches: {results['total_matches']}")
    
    # Show cache statistics
    cache_stats = get_ingredient_cache_stats()
    logger.info(f"\n=== Cache Statistics ===")
    logger.info(f"Total cached ingredients: {cache_stats['total_ingredients']}")
    logger.info(f"Cache valid: {cache_stats['cache_valid']}")
    logger.info(f"Last updated: {cache_stats['last_updated']}")


# Example usage for OCR service integration
def enhance_ocr_service_example():
    """
    Example of how to enhance the existing OCR service with ingredient matching.
    
    This shows how the ReceiptItem extraction could be improved with
    the cached ingredient data.
    """
    from scripts.ingredient_loader import search_ingredient_matches
    
    def enhanced_extract_receipt_items(ocr_text: str) -> List[Dict[str, any]]:
        """
        Enhanced version of receipt item extraction with ingredient matching.
        
        Args:
            ocr_text: Raw OCR text from receipt
            
        Returns:
            List of enhanced receipt items with ingredient suggestions
        """
        # This would replace/enhance the existing _extract_receipt_items method
        items = []
        lines = ocr_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Basic item detection logic (simplified)
            if any(indicator in line.lower() for indicator in ['$', 'lb', 'oz', 'kg', 'count']):
                # Extract basic item info
                item_text = re.sub(r'\$\d+\.\d{2}', '', line).strip()
                
                # Use ingredient matching to find suggestions
                ingredient_matches = search_ingredient_matches(item_text, max_matches=3)
                
                item = {
                    "detected_text": item_text,
                    "original_line": line,
                    "ingredient_suggestions": ingredient_matches,
                    "confidence_score": len(ingredient_matches) / 3.0  # Simple confidence
                }
                
                items.append(item)
        
        return items
    
    # Example usage
    sample_receipt = """
    GROCERY STORE RECEIPT
    chicken breast 2.5 lbs $12.99
    organic tomatoes 1 lb $3.49
    brown rice 2 lb $4.99
    total $21.47
    """
    
    enhanced_items = enhanced_extract_receipt_items(sample_receipt)
    
    logger.info("=== Enhanced OCR Receipt Processing ===")
    for item in enhanced_items:
        logger.info(f"Detected: '{item['detected_text']}'")
        logger.info(f"Suggestions: {item['ingredient_suggestions']}")
        logger.info(f"Confidence: {item['confidence_score']:.2f}")
        logger.info("---")


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_ocr_integration()
    enhance_ocr_service_example()
