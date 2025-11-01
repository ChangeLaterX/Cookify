"""
OCR Test Fixtures Package.

This package contains test fixtures, sample data, and mock responses for OCR testing.
"""

from pathlib import Path

# Fixture directory
FIXTURES_DIR = Path(__file__).parent

# Sample OCR responses for testing
SAMPLE_OCR_RESPONSES = {
    "simple_receipt": {
        "text": """
        FRESH MARKET GROCERY
        123 Main Street
        
        Tomatoes (2 lbs)      $3.98
        Onions (1 lb)         $1.49
        Garlic (3 bulbs)      $2.25
        
        Total:               $7.72
        """,
        "confidence": 85.5,
        "items": ["Tomatoes", "Onions", "Garlic"],
    },
    "complex_receipt": {
        "text": """
        SUPER GROCERY STORE
        456 Oak Avenue
        Phone: (555) 123-4567
        
        Receipt #: 789012
        Date: 2024-12-15 14:30:25
        Cashier: Jane D.
        
        ================================
        
        Organic Tomatoes (2 lbs)    $4.98
        Yellow Onions (3 lbs)       $2.47
        Fresh Garlic (1 bulb)       $0.89
        Bell Peppers (4 count)      $3.76
        Ground Beef (1 lb)          $5.99
        Chicken Breast (2 lbs)      $8.98
        Whole Milk (1 gallon)       $3.29
        Large Eggs (12 count)       $2.89
        Cheddar Cheese (8 oz)       $3.99
        Whole Wheat Bread           $2.99
        
        ================================
        
        Subtotal:                  $40.23
        Tax (8.5%):                $3.42
        Total:                     $43.65
        
        Payment Method: CARD
        Card ending in: 1234
        
        Thank you for shopping!
        """,
        "confidence": 92.3,
        "items": [
            "Organic Tomatoes",
            "Yellow Onions",
            "Fresh Garlic",
            "Bell Peppers",
            "Ground Beef",
            "Chicken Breast",
            "Whole Milk",
            "Large Eggs",
            "Cheddar Cheese",
            "Whole Wheat Bread",
        ],
    },
    "ocr_errors_receipt": {
        "text": """
        FRFSH MARKFT GROCFRY
        
        Tomatnes (2 its)      $398
        Onins (1 ib)          $149
        Garlie (3 bults)      $225
        Mitk (1 galon)        $329
        
        Tot:                 $1101
        """,
        "confidence": 58.7,
        "items": ["Tomatnes", "Onins", "Garlie", "Mitk"],  # OCR errors
    },
}

# Sample ingredient data for mocking
SAMPLE_INGREDIENTS = [
    {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Tomatoes",
        "description": "Fresh red tomatoes",
    },
    {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Onions",
        "description": "Yellow cooking onions",
    },
    {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Garlic",
        "description": "Fresh garlic bulbs",
    },
    {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440004",
        "name": "Bell Peppers",
        "description": "Mixed color bell peppers",
    },
    {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440005",
        "name": "Ground Beef",
        "description": "Lean ground beef",
    },
    {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440006",
        "name": "Chicken Breast",
        "description": "Boneless chicken breast",
    },
    {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440007",
        "name": "Milk",
        "description": "Whole milk",
    },
    {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440008",
        "name": "Eggs",
        "description": "Large fresh eggs",
    },
]
