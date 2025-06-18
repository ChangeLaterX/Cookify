"""
Simple OCR Integration Example.

This shows how to use the ingredient names file with OCR processing.
"""

from typing import List
from pathlib import Path


def load_ingredient_names() -> List[str]:
    """
    Load ingredient names from the text file.
    
    Returns:
        List[str]: List of ingredient names
    """
    ingredient_file = Path("data/ingredient_names.txt")
    
    if not ingredient_file.exists():
        return []
    
    ingredient_names = []
    
    with open(ingredient_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                ingredient_names.append(line)
    
    return ingredient_names


def find_ingredients_in_text(text: str, ingredient_names: List[str]) -> List[str]:
    """
    Simple function to find ingredients mentioned in OCR text.
    
    Args:
        text: OCR extracted text
        ingredient_names: List of known ingredient names
        
    Returns:
        List[str]: Found ingredient names
    """
    text_lower = text.lower()
    found_ingredients = []
    
    for ingredient in ingredient_names:
        if ingredient.lower() in text_lower:
            found_ingredients.append(ingredient)
    
    return found_ingredients


# Example usage for OCR service
def enhance_receipt_processing():
    """
    Example of how to enhance receipt processing with ingredient matching.
    """
    # Load ingredient names once
    ingredient_names = load_ingredient_names()
    print(f"Loaded {len(ingredient_names)} ingredient names")
    
    # Example OCR text from a receipt
    sample_receipt_text = """
    GROCERY STORE
    chicken breast 2.5 lbs $12.99
    organic tomatoes 1 lb $3.49
    brown rice 2 lb bag $4.99
    cheddar cheese 8oz $4.99
    olive oil 500ml $8.99
    total $34.45
    """
    
    # Find ingredients in the text
    found_ingredients = find_ingredients_in_text(sample_receipt_text, ingredient_names)
    
    print("\nFound ingredients in receipt:")
    for ingredient in found_ingredients:
        print(f"  ✅ {ingredient}")
    
    if not found_ingredients:
        print("  ⚠️ No ingredients found")


if __name__ == "__main__":
    enhance_receipt_processing()
