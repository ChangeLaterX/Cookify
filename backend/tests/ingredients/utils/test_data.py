"""
Test Data Generators for Ingredients Testing.

This module provides utilities for generating test data for Ingredients tests.
"""

import random
import string
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Smart test data generator removed - using basic test data generation

try:
    from domains.ingredients.schemas import (
        IngredientMasterCreate,
        IngredientMasterUpdate,
    )
except ImportError:
    # Mock schemas for standalone testing
    class IngredientMasterCreate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class IngredientMasterUpdate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


@dataclass
class TestIngredientData:
    """Container for test ingredient data."""

    ingredient_id: str
    name: str
    calories_per_100g: float
    proteins_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    category: Optional[str] = None

    def to_ingredient_create(self) -> IngredientMasterCreate:
        """Convert to IngredientMasterCreate schema."""
        return IngredientMasterCreate(
            name=self.name,
            calories_per_100g=self.calories_per_100g,
            proteins_per_100g=self.proteins_per_100g,
            fat_per_100g=self.fat_per_100g,
            carbs_per_100g=self.carbs_per_100g,
            category=self.category,
        )

    def to_ingredient_update(self, partial: bool = False) -> IngredientMasterUpdate:
        """Convert to IngredientMasterUpdate schema."""
        if partial:
            # Return partial update with random fields
            fields = {}
            if random.choice([True, False]):
                fields["name"] = self.name
            if random.choice([True, False]):
                fields["calories_per_100g"] = self.calories_per_100g
            if random.choice([True, False]):
                fields["proteins_per_100g"] = self.proteins_per_100g
            if random.choice([True, False]) and self.category:
                fields["category"] = self.category
            return IngredientMasterUpdate(**fields)

        return IngredientMasterUpdate(
            name=self.name,
            calories_per_100g=self.calories_per_100g,
            proteins_per_100g=self.proteins_per_100g,
            fat_per_100g=self.fat_per_100g,
            carbs_per_100g=self.carbs_per_100g,
            category=self.category,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "ingredient_id": self.ingredient_id,
            "name": self.name,
            "calories_per_100g": self.calories_per_100g,
            "proteins_per_100g": self.proteins_per_100g,
            "fat_per_100g": self.fat_per_100g,
            "carbs_per_100g": self.carbs_per_100g,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        if self.category:
            result["category"] = self.category
        return result


class TestDataGenerator:
    """Generator for creating test data for Ingredients tests."""

    # Common ingredient names for realistic testing
    INGREDIENT_NAMES = [
        "Tomato",
        "Onion",
        "Garlic",
        "Carrot",
        "Potato",
        "Bell Pepper",
        "Cucumber",
        "Lettuce",
        "Spinach",
        "Broccoli",
        "Cauliflower",
        "Chicken Breast",
        "Ground Beef",
        "Salmon",
        "Tuna",
        "Eggs",
        "Milk",
        "Cheddar Cheese",
        "Yogurt",
        "Butter",
        "Olive Oil",
        "Rice",
        "Pasta",
        "Bread",
        "Flour",
        "Sugar",
        "Salt",
        "Black Pepper",
        "Basil",
        "Oregano",
        "Thyme",
        "Parsley",
        "Lemon",
        "Lime",
        "Apple",
        "Banana",
        "Orange",
        "Strawberry",
        "Blueberry",
    ]

    # Nutritional value ranges for different ingredient types
    NUTRITION_RANGES = {
        "vegetables": {
            "calories": (15, 40),
            "proteins": (0.5, 3.0),
            "fat": (0.1, 0.5),
            "carbs": (2.0, 8.0),
        },
        "fruits": {
            "calories": (30, 80),
            "proteins": (0.3, 1.5),
            "fat": (0.1, 0.8),
            "carbs": (8.0, 20.0),
        },
        "meat": {
            "calories": (100, 300),
            "proteins": (15.0, 30.0),
            "fat": (3.0, 25.0),
            "carbs": (0.0, 2.0),
        },
        "dairy": {
            "calories": (50, 350),
            "proteins": (3.0, 25.0),
            "fat": (0.5, 30.0),
            "carbs": (3.0, 15.0),
        },
        "grains": {
            "calories": (300, 400),
            "proteins": (8.0, 15.0),
            "fat": (1.0, 5.0),
            "carbs": (60.0, 80.0),
        },
        "oils": {
            "calories": (800, 900),
            "proteins": (0.0, 0.1),
            "fat": (90.0, 100.0),
            "carbs": (0.0, 0.1),
        },
    }

    @classmethod
    def generate_ingredient_data(
        cls,
        name: Optional[str] = None,
        category: Optional[str] = None,
        realistic: bool = True,
    ) -> TestIngredientData:
        """Generate complete test ingredient data."""

        # Generate name
        if name is None:
            name = random.choice(cls.INGREDIENT_NAMES)
            # Add uniqueness to avoid conflicts
            name = f"{name} {uuid.uuid4().hex[:6]}"

        # Determine category for realistic nutritional values
        if category is None and realistic:
            category = cls._guess_category(name)

        # Generate nutritional values
        if realistic and category in cls.NUTRITION_RANGES:
            ranges = cls.NUTRITION_RANGES[category]
            calories = round(random.uniform(*ranges["calories"]), 1)
            proteins = round(random.uniform(*ranges["proteins"]), 1)
            fat = round(random.uniform(*ranges["fat"]), 1)
            carbs = round(random.uniform(*ranges["carbs"]), 1)
        else:
            # Generate random values
            calories = round(random.uniform(10, 500), 1)
            proteins = round(random.uniform(0, 30), 1)
            fat = round(random.uniform(0, 50), 1)
            carbs = round(random.uniform(0, 80), 1)

        return TestIngredientData(
            ingredient_id=str(uuid.uuid4()),
            name=name,
            calories_per_100g=calories,
            proteins_per_100g=proteins,
            fat_per_100g=fat,
            carbs_per_100g=carbs,
            category=category,
        )

    @classmethod
    def _guess_category(cls, name: str) -> str:
        """Guess ingredient category from name."""
        name_lower = name.lower()

        vegetables = [
            "tomato",
            "onion",
            "garlic",
            "carrot",
            "potato",
            "pepper",
            "cucumber",
            "lettuce",
            "spinach",
            "broccoli",
            "cauliflower",
        ]
        fruits = [
            "apple",
            "banana",
            "orange",
            "strawberry",
            "blueberry",
            "lemon",
            "lime",
        ]
        meat = ["chicken", "beef", "salmon", "tuna", "pork", "turkey"]
        dairy = ["milk", "cheese", "yogurt", "butter", "cream"]
        grains = ["rice", "pasta", "bread", "flour", "wheat", "oats"]
        oils = ["oil", "olive oil", "coconut oil"]

        for category, keywords in [
            ("vegetables", vegetables),
            ("fruits", fruits),
            ("meat", meat),
            ("dairy", dairy),
            ("grains", grains),
            ("oils", oils),
        ]:
            if any(keyword in name_lower for keyword in keywords):
                return category

        return "vegetables"  # Default category

    @classmethod
    def generate_bulk_ingredients(
        cls, count: int = 10, realistic: bool = True
    ) -> List[TestIngredientData]:
        """Generate multiple test ingredients."""
        return [cls.generate_ingredient_data(realistic=realistic) for _ in range(count)]

    @classmethod
    def generate_invalid_ingredient_data(cls) -> List[Dict[str, Any]]:
        """Generate list of invalid ingredient data for testing."""
        return [
            {
                "name": "",
                "calories_per_100g": 100,
                "proteins_per_100g": 10,
                "fat_per_100g": 5,
                "carbs_per_100g": 15,
            },  # Empty name
            {
                "name": "Test",
                "calories_per_100g": -10,
                "proteins_per_100g": 10,
                "fat_per_100g": 5,
                "carbs_per_100g": 15,
            },  # Negative calories
            {
                "name": "Test",
                "calories_per_100g": 100,
                "proteins_per_100g": -5,
                "fat_per_100g": 5,
                "carbs_per_100g": 15,
            },  # Negative proteins
            {
                "name": "Test",
                "calories_per_100g": 100,
                "proteins_per_100g": 10,
                "fat_per_100g": -2,
                "carbs_per_100g": 15,
            },  # Negative fat
            {
                "name": "Test",
                "calories_per_100g": 100,
                "proteins_per_100g": 10,
                "fat_per_100g": 5,
                "carbs_per_100g": -8,
            },  # Negative carbs
            {
                "name": "A" * 300,
                "calories_per_100g": 100,
                "proteins_per_100g": 10,
                "fat_per_100g": 5,
                "carbs_per_100g": 15,
            },  # Name too long
        ]

    @classmethod
    def generate_search_test_data(cls) -> List[TestIngredientData]:
        """Generate ingredients specifically for search testing."""
        search_ingredients = [
            cls.generate_ingredient_data("Tomato", "vegetables"),
            cls.generate_ingredient_data("Cherry Tomato", "vegetables"),
            cls.generate_ingredient_data("Tomato Sauce", "vegetables"),
            cls.generate_ingredient_data("Onion", "vegetables"),
            cls.generate_ingredient_data("Green Onion", "vegetables"),
            cls.generate_ingredient_data("Red Onion", "vegetables"),
            cls.generate_ingredient_data("Chicken Breast", "meat"),
            cls.generate_ingredient_data("Chicken Thigh", "meat"),
            cls.generate_ingredient_data("Ground Chicken", "meat"),
            cls.generate_ingredient_data("Apple", "fruits"),
        ]
        return search_ingredients

    @classmethod
    def generate_pagination_test_data(
        cls, total_items: int = 50
    ) -> List[TestIngredientData]:
        """Generate ingredients for pagination testing."""
        ingredients = []
        for i in range(total_items):
            name = f"Test Ingredient {i+1:03d}"
            ingredient = cls.generate_ingredient_data(name=name, realistic=False)
            ingredients.append(ingredient)
        return ingredients

    @classmethod
    def generate_update_scenarios(
        cls, base_ingredient: TestIngredientData
    ) -> List[Dict[str, Any]]:
        """Generate various update scenarios for testing."""
        scenarios = [
            # Update name only
            {"name": f"{base_ingredient.name} Updated"},
            # Update nutritional values
            {
                "calories_per_100g": base_ingredient.calories_per_100g + 10,
                "proteins_per_100g": base_ingredient.proteins_per_100g + 1,
            },
            # Update all fields
            {
                "name": f"{base_ingredient.name} Completely Updated",
                "calories_per_100g": base_ingredient.calories_per_100g * 1.2,
                "proteins_per_100g": base_ingredient.proteins_per_100g * 1.1,
                "fat_per_100g": base_ingredient.fat_per_100g * 1.3,
                "carbs_per_100g": base_ingredient.carbs_per_100g * 0.9,
            },
            # Edge case: minimal values
            {
                "calories_per_100g": 0.1,
                "proteins_per_100g": 0.0,
                "fat_per_100g": 0.0,
                "carbs_per_100g": 0.1,
            },
        ]
        return scenarios

    @staticmethod
    def generate_ingredients_by_category(
        category: str, count: int
    ) -> List[Dict[str, Any]]:
        """Generate ingredients for a specific category."""
        # Generate basic ingredients data
        ingredients = []
        for i in range(count):
            ingredient_data = TestDataGenerator.generate_ingredient_data(
                name=f"Test Ingredient {i+1}", category=category
            )
            ingredients.append(ingredient_data.to_dict())
        return ingredients

    @staticmethod
    def validation_scenarios() -> List[Dict[str, Any]]:
        """Generate validation test scenarios."""
        invalid_data = TestDataGenerator.generate_invalid_ingredient_data()

        scenarios: List[Dict[str, Any]] = []
        scenario_names = [
            "empty_name",
            "negative_calories",
            "negative_proteins",
            "negative_fat",
            "negative_carbs",
            "name_too_long",
        ]

        for i, data in enumerate(invalid_data):
            scenario_name = (
                scenario_names[i] if i < len(scenario_names) else f"invalid_data_{i}"
            )

            scenarios.append(
                {
                    "name": scenario_name,
                    "data": data,
                    "expected_error": "VALIDATION_ERROR",
                }
            )

        return scenarios


class TestScenarios:
    """Test scenarios provider that creates test scenarios on demand."""

    @staticmethod
    def search_scenarios() -> List[Dict[str, Any]]:
        """Get search test scenarios."""
        return [
            {
                "query": "Tomato",
                "expected_matches": ["Tomato", "Cherry Tomato", "Tomato Sauce"],
            },
            {"query": "Chicken", "expected_matches": ["Chicken Breast"]},
            {"query": "nonexistent", "expected_matches": []},
        ]

    @staticmethod
    def pagination_scenarios() -> List[Dict[str, Any]]:
        """Get pagination test scenarios."""
        return [
            {
                "name": "first_page",
                "limit": 5,
                "offset": 0,
                "total_items": 25,
                "expected_items": 5,
            },
            {
                "name": "middle_page",
                "limit": 10,
                "offset": 10,
                "total_items": 25,
                "expected_items": 10,
            },
            {
                "name": "last_page",
                "limit": 10,
                "offset": 20,
                "total_items": 25,
                "expected_items": 5,
            },
        ]

    @staticmethod
    def validation_scenarios() -> List[Dict[str, Any]]:
        """Get validation test scenarios."""
        return [
            {
                "name": "empty_name",
                "data": {"name": "", "calories_per_100g": 100},
                "expected_error": "VALIDATION_ERROR",
            },
            {
                "name": "negative_calories",
                "data": {"name": "Test", "calories_per_100g": -10},
                "expected_error": "VALIDATION_ERROR",
            },
        ]
