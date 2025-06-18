"""
Ingredient Data Loader Script.

This script loads all ingredient names from the Supabase ingredient_master table
and prepares them for OCR matching. It runs when the FastAPI application starts
to cache ingredient data for better performance.
"""

import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from shared.database.supabase import get_supabase_client
from core.config import settings

logger = logging.getLogger(__name__)


class IngredientCache:
    """Cache for ingredient master data to improve OCR matching performance."""
    
    def __init__(self):
        self.ingredients: List[Dict[str, str]] = []
        self.ingredient_names: List[str] = []
        self.ingredient_map: Dict[str, Dict] = {}  # name -> full ingredient data
        self.last_updated: Optional[datetime] = None
        self.cache_duration_hours = 1  # Cache for 1 hour
        
    def is_cache_valid(self) -> bool:
        """Check if the cache is still valid based on timestamp."""
        if not self.last_updated:
            return False
        
        cache_expiry = self.last_updated + timedelta(hours=self.cache_duration_hours)
        return datetime.now() < cache_expiry
    
    async def load_ingredients_from_database(self) -> bool:
        """
        Load all ingredients from the Supabase database.
        
        Returns:
            bool: True if successful, False if failed
        """
        try:
            logger.info("Loading ingredients from Supabase database...")
            
            supabase = get_supabase_client()
            
            # Query all ingredients from ingredient_master table
            response = (
                supabase.table("ingredient_master")
                .select("ingredient_id, name, calories_per_100g, proteins_per_100g, fat_per_100g, carbs_per_100g, price_per_100g_cents")
                .order("name")
                .execute()
            )
            
            if not response.data:
                logger.warning("No ingredients found in database")
                return False
            
            # Process the data
            self.ingredients = response.data
            self.ingredient_names = [ingredient["name"] for ingredient in response.data]
            
            # Create a lookup map for faster access
            self.ingredient_map = {
                ingredient["name"].lower(): ingredient 
                for ingredient in response.data
            }
            
            self.last_updated = datetime.now()
            
            logger.info(f"Successfully loaded {len(self.ingredients)} ingredients from database")
            logger.info(f"Sample ingredients: {', '.join(self.ingredient_names[:5])}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ingredients from database: {str(e)}")
            return False
    
    async def refresh_if_needed(self) -> bool:
        """
        Refresh the cache if it's expired or empty.
        
        Returns:
            bool: True if cache is valid/refreshed, False if failed
        """
        if not self.is_cache_valid() or not self.ingredients:
            logger.info("Cache expired or empty, refreshing ingredient data...")
            return await self.load_ingredients_from_database()
        
        return True
    
    def get_all_ingredient_names(self) -> List[str]:
        """
        Get all ingredient names for OCR matching.
        
        Returns:
            List[str]: List of all ingredient names
        """
        return self.ingredient_names.copy()
    
    def get_ingredient_by_name(self, name: str) -> Optional[Dict]:
        """
        Get ingredient data by name (case-insensitive).
        
        Args:
            name: The ingredient name to search for
            
        Returns:
            Optional[Dict]: Ingredient data if found, None otherwise
        """
        return self.ingredient_map.get(name.lower())
    
    def search_ingredients_fuzzy(self, query: str, limit: int = 10) -> List[str]:
        """
        Search for ingredients that contain the query string.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[str]: List of matching ingredient names
        """
        query_lower = query.lower()
        matches = [
            name for name in self.ingredient_names 
            if query_lower in name.lower()
        ]
        return matches[:limit]
    
    def get_cache_stats(self) -> Dict[str, any]:
        """
        Get cache statistics for monitoring.
        
        Returns:
            Dict: Cache statistics
        """
        return {
            "total_ingredients": len(self.ingredients),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "cache_valid": self.is_cache_valid(),
            "cache_duration_hours": self.cache_duration_hours
        }


# Global cache instance
ingredient_cache = IngredientCache()


async def initialize_ingredient_cache() -> bool:
    """
    Initialize the ingredient cache at application startup.
    
    This function should be called when FastAPI starts up to pre-load
    ingredient data for OCR matching.
    
    Returns:
        bool: True if successful, False if failed
    """
    logger.info("Initializing ingredient cache...")
    
    try:
        success = await ingredient_cache.load_ingredients_from_database()
        
        if success:
            stats = ingredient_cache.get_cache_stats()
            logger.info(f"Ingredient cache initialized successfully: {stats}")
        else:
            logger.error("Failed to initialize ingredient cache")
            
        return success
        
    except Exception as e:
        logger.error(f"Error during ingredient cache initialization: {str(e)}")
        return False


async def refresh_ingredient_cache() -> bool:
    """
    Manually refresh the ingredient cache.
    
    This can be called periodically or when database changes are detected.
    
    Returns:
        bool: True if successful, False if failed
    """
    logger.info("Manually refreshing ingredient cache...")
    return await ingredient_cache.load_ingredients_from_database()


def get_ingredient_names_for_ocr() -> List[str]:
    """
    Get all ingredient names for OCR matching.
    
    This is the main function that OCR services should use to get
    the list of known ingredients for matching against detected text.
    
    Returns:
        List[str]: List of all ingredient names
    """
    if not ingredient_cache.is_cache_valid():
        logger.warning("Ingredient cache is invalid - consider refreshing")
    
    return ingredient_cache.get_all_ingredient_names()


def search_ingredient_matches(ocr_text: str, max_matches: int = 5) -> List[str]:
    """
    Search for ingredient matches in OCR text.
    
    This function can be used by OCR services to find potential
    ingredient matches in extracted text.
    
    Args:
        ocr_text: The OCR extracted text to search in
        max_matches: Maximum number of matches to return
        
    Returns:
        List[str]: List of matching ingredient names
    """
    matches = []
    
    # Split OCR text into words for better matching
    words = ocr_text.lower().split()
    
    for ingredient_name in ingredient_cache.get_all_ingredient_names():
        ingredient_lower = ingredient_name.lower()
        
        # Check if ingredient name appears in OCR text
        if ingredient_lower in ocr_text.lower():
            matches.append(ingredient_name)
            continue
        
        # Check if any words match ingredient words
        ingredient_words = ingredient_lower.split()
        for word in words:
            if any(word in ingredient_word for ingredient_word in ingredient_words):
                matches.append(ingredient_name)
                break
    
    # Remove duplicates and limit results
    unique_matches = list(dict.fromkeys(matches))
    return unique_matches[:max_matches]


def get_ingredient_cache_stats() -> Dict[str, any]:
    """
    Get ingredient cache statistics for monitoring and debugging.
    
    Returns:
        Dict: Cache statistics including count, last update time, etc.
    """
    return ingredient_cache.get_cache_stats()


# Export public functions
__all__ = [
    "initialize_ingredient_cache",
    "refresh_ingredient_cache", 
    "get_ingredient_names_for_ocr",
    "search_ingredient_matches",
    "get_ingredient_cache_stats",
    "ingredient_cache"
]
