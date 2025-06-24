"""
Sample ingredient data for testing.

This module provides realistic sample ingredient data that can be used
across different test scenarios.
"""

from typing import Any, Dict, List
from uuid import uuid4

# Sample ingredient categories with realistic nutritional profiles
SAMPLE_INGREDIENTS: List[Dict[str, Any]] = [
    # Vegetables
    {
        "name": "Tomato",
        "calories_per_100g": 18.0,
        "proteins_per_100g": 0.9,
        "fat_per_100g": 0.2,
        "carbs_per_100g": 3.9,
        "price_per_100g_cents": 250,
        "category": "vegetables",
    },
    {
        "name": "Spinach",
        "calories_per_100g": 23.0,
        "proteins_per_100g": 2.9,
        "fat_per_100g": 0.4,
        "carbs_per_100g": 3.6,
        "price_per_100g_cents": 400,
        "category": "vegetables",
    },
    {
        "name": "Carrot",
        "calories_per_100g": 41.0,
        "proteins_per_100g": 0.9,
        "fat_per_100g": 0.2,
        "carbs_per_100g": 9.6,
        "price_per_100g_cents": 180,
        "category": "vegetables",
    },
    # Proteins
    {
        "name": "Chicken Breast",
        "calories_per_100g": 165.0,
        "proteins_per_100g": 31.0,
        "fat_per_100g": 3.6,
        "carbs_per_100g": 0.0,
        "price_per_100g_cents": 1200,
        "category": "meat",
    },
    {
        "name": "Salmon Fillet",
        "calories_per_100g": 208.0,
        "proteins_per_100g": 25.4,
        "fat_per_100g": 12.4,
        "carbs_per_100g": 0.0,
        "price_per_100g_cents": 2500,
        "category": "fish",
    },
    {
        "name": "Eggs",
        "calories_per_100g": 155.0,
        "proteins_per_100g": 13.0,
        "fat_per_100g": 11.0,
        "carbs_per_100g": 1.1,
        "price_per_100g_cents": 600,
        "category": "dairy",
    },
    # Grains and Starches
    {
        "name": "Brown Rice",
        "calories_per_100g": 111.0,
        "proteins_per_100g": 2.6,
        "fat_per_100g": 0.9,
        "carbs_per_100g": 23.0,
        "price_per_100g_cents": 300,
        "category": "grains",
    },
    {
        "name": "Whole Wheat Pasta",
        "calories_per_100g": 124.0,
        "proteins_per_100g": 5.0,
        "fat_per_100g": 0.5,
        "carbs_per_100g": 25.0,
        "price_per_100g_cents": 350,
        "category": "grains",
    },
    {
        "name": "Sweet Potato",
        "calories_per_100g": 86.0,
        "proteins_per_100g": 1.6,
        "fat_per_100g": 0.1,
        "carbs_per_100g": 20.1,
        "price_per_100g_cents": 220,
        "category": "vegetables",
    },
    # Dairy
    {
        "name": "Greek Yogurt",
        "calories_per_100g": 59.0,
        "proteins_per_100g": 10.0,
        "fat_per_100g": 0.4,
        "carbs_per_100g": 3.6,
        "price_per_100g_cents": 800,
        "category": "dairy",
    },
    {
        "name": "Cheddar Cheese",
        "calories_per_100g": 403.0,
        "proteins_per_100g": 25.0,
        "fat_per_100g": 33.0,
        "carbs_per_100g": 1.3,
        "price_per_100g_cents": 1500,
        "category": "dairy",
    },
    # Oils and Fats
    {
        "name": "Olive Oil",
        "calories_per_100g": 884.0,
        "proteins_per_100g": 0.0,
        "fat_per_100g": 100.0,
        "carbs_per_100g": 0.0,
        "price_per_100g_cents": 800,
        "category": "oils",
    },
    {
        "name": "Avocado",
        "calories_per_100g": 160.0,
        "proteins_per_100g": 2.0,
        "fat_per_100g": 14.7,
        "carbs_per_100g": 8.5,
        "price_per_100g_cents": 600,
        "category": "fruits",
    },
    # Fruits
    {
        "name": "Apple",
        "calories_per_100g": 52.0,
        "proteins_per_100g": 0.3,
        "fat_per_100g": 0.2,
        "carbs_per_100g": 13.8,
        "price_per_100g_cents": 300,
        "category": "fruits",
    },
    {
        "name": "Banana",
        "calories_per_100g": 89.0,
        "proteins_per_100g": 1.1,
        "fat_per_100g": 0.3,
        "carbs_per_100g": 22.8,
        "price_per_100g_cents": 250,
        "category": "fruits",
    },
    # Legumes
    {
        "name": "Black Beans",
        "calories_per_100g": 132.0,
        "proteins_per_100g": 8.9,
        "fat_per_100g": 0.5,
        "carbs_per_100g": 23.0,
        "price_per_100g_cents": 400,
        "category": "legumes",
    },
    {
        "name": "Lentils",
        "calories_per_100g": 116.0,
        "proteins_per_100g": 9.0,
        "fat_per_100g": 0.4,
        "carbs_per_100g": 20.0,
        "price_per_100g_cents": 500,
        "category": "legumes",
    },
    # Nuts and Seeds
    {
        "name": "Almonds",
        "calories_per_100g": 579.0,
        "proteins_per_100g": 21.0,
        "fat_per_100g": 49.9,
        "carbs_per_100g": 21.6,
        "price_per_100g_cents": 2000,
        "category": "nuts",
    },
    {
        "name": "Chia Seeds",
        "calories_per_100g": 486.0,
        "proteins_per_100g": 17.0,
        "fat_per_100g": 31.0,
        "carbs_per_100g": 42.0,
        "price_per_100g_cents": 2500,
        "category": "seeds",
    },
    # Herbs and Spices
    {
        "name": "Fresh Basil",
        "calories_per_100g": 22.0,
        "proteins_per_100g": 3.2,
        "fat_per_100g": 0.6,
        "carbs_per_100g": 2.6,
        "price_per_100g_cents": 1200,
        "category": "herbs",
    },
    {
        "name": "Garlic",
        "calories_per_100g": 149.0,
        "proteins_per_100g": 6.4,
        "fat_per_100g": 0.5,
        "carbs_per_100g": 33.1,
        "price_per_100g_cents": 800,
        "category": "vegetables",
    },
]


# Test scenarios for different use cases
TEST_SCENARIOS = {
    "high_protein": [
        "Chicken Breast",
        "Salmon Fillet",
        "Eggs",
        "Greek Yogurt",
        "Almonds",
    ],
    "low_calorie": ["Tomato", "Spinach", "Carrot", "Apple", "Fresh Basil"],
    "high_fat": ["Olive Oil", "Avocado", "Cheddar Cheese", "Almonds", "Chia Seeds"],
    "vegetarian": [
        "Tomato",
        "Spinach",
        "Brown Rice",
        "Greek Yogurt",
        "Black Beans",
        "Lentils",
    ],
    "expensive": [
        "Salmon Fillet",
        "Chia Seeds",
        "Almonds",
        "Cheddar Cheese",
        "Fresh Basil",
    ],
    "budget_friendly": [
        "Carrot",
        "Banana",
        "Sweet Potato",
        "Brown Rice",
        "Black Beans",
    ],
}


# Sample ingredient responses (as they would come from the API)
SAMPLE_RESPONSES = [
    {
        "ingredient_id": str(uuid4()),
        "name": "Tomato",
        "calories_per_100g": 18.0,
        "proteins_per_100g": 0.9,
        "fat_per_100g": 0.2,
        "carbs_per_100g": 3.9,
        "price_per_100g_cents": 250,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    },
    {
        "ingredient_id": str(uuid4()),
        "name": "Chicken Breast",
        "calories_per_100g": 165.0,
        "proteins_per_100g": 31.0,
        "fat_per_100g": 3.6,
        "carbs_per_100g": 0.0,
        "price_per_100g_cents": 1200,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    },
]


# Invalid data for validation testing
INVALID_INGREDIENTS = [
    {
        "name": "",  # Empty name
        "calories_per_100g": 100.0,
        "proteins_per_100g": 10.0,
        "fat_per_100g": 5.0,
        "carbs_per_100g": 15.0,
        "price_per_100g_cents": 500,
        "error_type": "empty_name",
    },
    {
        "name": "Test Ingredient",
        "calories_per_100g": -50.0,  # Negative calories
        "proteins_per_100g": 10.0,
        "fat_per_100g": 5.0,
        "carbs_per_100g": 15.0,
        "price_per_100g_cents": 500,
        "error_type": "negative_calories",
    },
    {
        "name": "Test Ingredient",
        "calories_per_100g": 100.0,
        "proteins_per_100g": 10.0,
        "fat_per_100g": 5.0,
        "carbs_per_100g": 15.0,
        "price_per_100g_cents": -100,  # Negative price
        "error_type": "negative_price",
    },
    {
        "name": "A" * 300,  # Name too long
        "calories_per_100g": 100.0,
        "proteins_per_100g": 10.0,
        "fat_per_100g": 5.0,
        "carbs_per_100g": 15.0,
        "price_per_100g_cents": 500,
        "error_type": "name_too_long",
    },
]


def get_ingredients_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all sample ingredients for a specific category."""
    return [ing for ing in SAMPLE_INGREDIENTS if ing.get("category") == category]


def get_ingredients_by_scenario(scenario: str) -> List[Dict[str, Any]]:
    """Get ingredients for a specific test scenario."""
    ingredient_names = TEST_SCENARIOS.get(scenario, [])
    return [ing for ing in SAMPLE_INGREDIENTS if ing["name"] in ingredient_names]


def get_random_ingredient() -> Dict[str, Any]:
    """Get a random sample ingredient."""
    import random

    return random.choice(SAMPLE_INGREDIENTS)


def get_ingredient_by_name(name: str) -> Dict[str, Any]:
    """Get a specific ingredient by name."""
    for ingredient in SAMPLE_INGREDIENTS:
        if ingredient["name"] == name:
            return ingredient
    raise ValueError(f"Ingredient '{name}' not found in sample data")
