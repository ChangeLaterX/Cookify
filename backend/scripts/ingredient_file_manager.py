"""
Simple Ingredient Names File Manager.

This script creates and maintains a simple text file with all ingredient names
from the Supabase database. The file is updated once per week automatically.
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from shared.database.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class IngredientNamesManager:
    """Manages a simple file containing all ingredient names."""
    
    def __init__(self, file_path: str = "data/ingredient_names.txt"):
        """
        Initialize the manager.
        
        Args:
            file_path: Path to the ingredient names file
        """
        self.file_path = Path(file_path)
        self.metadata_path = Path(str(file_path).replace('.txt', '_metadata.json'))
        self.update_interval_days = 7  # Update once per week
        
        # Ensure the data directory exists
        self.file_path.parent.mkdir(exist_ok=True)
    
    def _get_metadata(self) -> Dict:
        """Get metadata about the last update."""
        try:
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not read metadata: {e}")
        
        return {
            "last_updated": None,
            "ingredient_count": 0,
            "version": 1
        }
    
    def _save_metadata(self, ingredient_count: int) -> None:
        """Save metadata about the update."""
        metadata = {
            "last_updated": datetime.now().isoformat(),
            "ingredient_count": ingredient_count,
            "version": 1
        }
        
        try:
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metadata: {e}")
    
    def needs_update(self) -> bool:
        """Check if the ingredient file needs to be updated."""
        # If file doesn't exist, we need to create it
        if not self.file_path.exists():
            return True
        
        metadata = self._get_metadata()
        last_updated = metadata.get("last_updated")
        
        if not last_updated:
            return True
        
        try:
            last_update_date = datetime.fromisoformat(last_updated)
            days_since_update = (datetime.now() - last_update_date).days
            
            return days_since_update >= self.update_interval_days
        except Exception as e:
            logger.warning(f"Could not parse last update date: {e}")
            return True
    
    async def load_ingredients_from_database(self) -> List[str]:
        """
        Load all ingredient names from the Supabase database.
        
        Returns:
            List[str]: List of ingredient names
        """
        try:
            logger.info("Loading ingredient names from Supabase database...")
            
            supabase = get_supabase_client()
            
            # Query only the names, sorted alphabetically
            response = (
                supabase.table("ingredient_master")
                .select("name")
                .order("name")
                .execute()
            )
            
            if not response.data:
                logger.warning("No ingredients found in database")
                return []
            
            ingredient_names = [item["name"] for item in response.data]
            
            logger.info(f"Successfully loaded {len(ingredient_names)} ingredient names")
            return ingredient_names
            
        except Exception as e:
            logger.error(f"Failed to load ingredients from database: {str(e)}")
            return []
    
    def save_ingredients_to_file(self, ingredient_names: List[str]) -> bool:
        """
        Save ingredient names to a text file.
        
        Args:
            ingredient_names: List of ingredient names to save
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Create a header with timestamp and count
            header = [
                f"# Cookify Ingredient Names",
                f"# Generated: {datetime.now().isoformat()}",
                f"# Total ingredients: {len(ingredient_names)}",
                f"# Auto-updated weekly",
                f"",
            ]
            
            # Write to file
            with open(self.file_path, 'w', encoding='utf-8') as f:
                # Write header
                for line in header:
                    f.write(line + '\n')
                
                # Write ingredient names (one per line)
                for name in ingredient_names:
                    f.write(name + '\n')
            
            # Save metadata
            self._save_metadata(len(ingredient_names))
            
            logger.info(f"Successfully saved {len(ingredient_names)} ingredients to {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save ingredients to file: {str(e)}")
            return False
    
    def load_ingredients_from_file(self) -> List[str]:
        """
        Load ingredient names from the text file.
        
        Returns:
            List[str]: List of ingredient names
        """
        try:
            if not self.file_path.exists():
                return []
            
            ingredient_names = []
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        ingredient_names.append(line)
            
            logger.info(f"Loaded {len(ingredient_names)} ingredients from file")
            return ingredient_names
            
        except Exception as e:
            logger.error(f"Failed to load ingredients from file: {str(e)}")
            return []
    
    async def update_if_needed(self) -> bool:
        """
        Update the ingredient file if needed (once per week).
        
        Returns:
            bool: True if update was performed, False if not needed or failed
        """
        if not self.needs_update():
            logger.info("Ingredient file is up to date, no update needed")
            return False
        
        logger.info("Ingredient file needs update, fetching from database...")
        
        # Load from database
        ingredient_names = await self.load_ingredients_from_database()
        
        if not ingredient_names:
            logger.error("No ingredients loaded from database")
            return False
        
        # Save to file
        success = self.save_ingredients_to_file(ingredient_names)
        
        if success:
            logger.info("✅ Ingredient file updated successfully")
        else:
            logger.error("❌ Failed to update ingredient file")
        
        return success
    
    def get_status(self) -> Dict:
        """Get status information about the ingredient file."""
        metadata = self._get_metadata()
        
        return {
            "file_exists": self.file_path.exists(),
            "file_path": str(self.file_path),
            "last_updated": metadata.get("last_updated"),
            "ingredient_count": metadata.get("ingredient_count", 0),
            "needs_update": self.needs_update(),
            "update_interval_days": self.update_interval_days
        }


# Global instance
ingredient_manager = IngredientNamesManager()


async def initialize_ingredient_file() -> bool:
    """
    Initialize the ingredient file at application startup.
    
    This function checks if the file needs updating and updates it if necessary.
    Should be called once when FastAPI starts.
    
    Returns:
        bool: True if successful, False if failed
    """
    logger.info("Initializing ingredient names file...")
    
    try:
        # Check if update is needed and perform it
        updated = await ingredient_manager.update_if_needed()
        
        # Get current status
        status = ingredient_manager.get_status()
        
        if status["file_exists"]:
            logger.info(f"✅ Ingredient file ready: {status['ingredient_count']} ingredients")
            logger.info(f"   File path: {status['file_path']}")
            logger.info(f"   Last updated: {status['last_updated']}")
            logger.info(f"   Next update in: {7 - (datetime.now() - datetime.fromisoformat(status['last_updated']) if status['last_updated'] else datetime.now()).days} days")
            return True
        else:
            logger.error("❌ Ingredient file could not be created")
            return False
            
    except Exception as e:
        logger.error(f"Error during ingredient file initialization: {str(e)}")
        return False


def get_ingredient_names() -> List[str]:
    """
    Get all ingredient names from the file.
    
    This is the main function that OCR services should use.
    
    Returns:
        List[str]: List of all ingredient names
    """
    return ingredient_manager.load_ingredients_from_file()


def get_ingredient_file_status() -> Dict:
    """
    Get status information about the ingredient file for monitoring.
    
    Returns:
        Dict: Status information
    """
    return ingredient_manager.get_status()


# Export public functions
__all__ = [
    "initialize_ingredient_file",
    "get_ingredient_names",
    "get_ingredient_file_status"
]
