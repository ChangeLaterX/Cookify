"""
Ingredients Test Configuration and Base Classes.

This module provides the base configuration and shared utilities for all Ingredients tests.
"""

import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

# Import smart mocks only when needed
# from .utils.smart_mocks import SmartMockContextManager, smart_ingredients_mock


@dataclass
class IngredientsTestConfig:
    """Configuration for Ingredients tests."""

    # Test modes
    MOCK_MODE: bool = os.getenv("INGREDIENTS_TEST_MOCK_MODE", "true").lower() == "true"
    INTEGRATION_MODE: bool = (
        os.getenv("INGREDIENTS_TEST_INTEGRATION", "false").lower() == "true"
    )

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    TEST_ROOT: Path = PROJECT_ROOT / "tests" / "ingredients"
    FIXTURES_PATH: Path = TEST_ROOT / "fixtures"

    # Dependencies
    SUPABASE_AVAILABLE: bool = all(
        [os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY")]
    )

    # Test database settings
    TEST_EMAIL_DOMAIN: str = os.getenv(
        "INGREDIENTS_TEST_EMAIL_DOMAIN", "test.cookify.app"
    )
    PERFORMANCE_TESTING: bool = (
        os.getenv("INGREDIENTS_TEST_PERFORMANCE", "false").lower() == "true"
    )

    # Feature flags for testing
    SEARCH_TESTING_ENABLED: bool = (
        os.getenv("INGREDIENTS_TEST_SEARCH", "true").lower() == "true"
    )
    VALIDATION_TESTING_ENABLED: bool = (
        os.getenv("INGREDIENTS_TEST_VALIDATION", "true").lower() == "true"
    )
    BULK_OPERATIONS_TESTING: bool = (
        os.getenv("INGREDIENTS_TEST_BULK", "true").lower() == "true"
    )


class IngredientsTestBase(ABC):
    """
    Abstract base class for all Ingredients tests.
    Provides common test utilities and ensures consistent test structure.
    """

    def setup_method(self, method):
        """Setup run before each test method."""
        self.config = IngredientsTestConfig()
        self.setup_test_data()
        self.mock_context = None

    def teardown_method(self, method):
        """Cleanup run after each test method."""
        self.cleanup_test_data()

    def setup_test_data(self):
        """Setup test data for ingredients tests."""
        # Smart Mocks können bei Bedarf in individuellen Tests verwendet werden
        pass

    def cleanup_test_data(self):
        """Cleanup test data after tests."""
        pass

    @abstractmethod
    def test_main_functionality(self):
        """
        Abstract method that each test class must implement.
        This ensures every test class has at least one meaningful test.
        """
        pass


class IngredientsTestUtils:
    """Utility methods for Ingredients testing."""

    @staticmethod
    def create_mock_supabase_client(success_responses: bool = True) -> Mock:
        """Create a mock Supabase client for ingredients READ-ONLY operations."""
        client = Mock()

        # Mock table operations
        table_mock = Mock()
        client.table.return_value = table_mock

        if success_responses:
            # Mock successful READ responses only
            table_mock.select.return_value.execute.return_value.data = [
                {
                    "ingredient_id": "test-id-123",
                    "name": "Test Ingredient",
                    "calories_per_100g": 100.0,
                    "proteins_per_100g": 10.0,
                    "fat_per_100g": 5.0,
                    "carbs_per_100g": 15.0,
                    "category": "vegetables",
                }
            ]

            # Note: No mock responses for insert/update/delete operations
            # as this test suite is READ-ONLY

        else:
            # Mock error responses for read operations only
            table_mock.select.return_value.execute.return_value.data = None

        # Mock chain methods for query building
        table_mock.select.return_value = table_mock
        table_mock.range.return_value = table_mock
        table_mock.order.return_value = table_mock
        table_mock.eq.return_value = table_mock
        table_mock.ilike.return_value = table_mock
        table_mock.execute.return_value = Mock(
            data=table_mock.select.return_value.execute.return_value.data
        )

        return client

    @staticmethod
    def create_sample_ingredient_data() -> Dict[str, Any]:
        """Create sample ingredient data for testing."""
        return {
            "ingredient_id": "sample-id-789",
            "name": "Sample Ingredient",
            "calories_per_100g": 150.0,
            "proteins_per_100g": 15.0,
            "fat_per_100g": 8.0,
            "carbs_per_100g": 20.0,
            "category": "dairy",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

    @staticmethod
    def create_invalid_ingredient_data() -> Dict[str, Any]:
        """Create invalid ingredient data for negative testing."""
        return {
            "name": "",  # Invalid: empty name
            "calories_per_100g": -10.0,  # Invalid: negative calories
            "proteins_per_100g": -5.0,  # Invalid: negative proteins
            "fat_per_100g": -2.0,  # Invalid: negative fat
            "carbs_per_100g": -8.0,  # Invalid: negative carbs
            "category": "invalid",
        }


class MockSupabaseIngredient:
    """Mock Supabase ingredient model for testing."""

    def __init__(self, data: Dict[str, Any]):
        self.ingredient_id = data.get("ingredient_id")
        self.name = data.get("name")
        self.calories_per_100g = data.get("calories_per_100g")
        self.proteins_per_100g = data.get("proteins_per_100g")
        self.fat_per_100g = data.get("fat_per_100g")
        self.carbs_per_100g = data.get("carbs_per_100g")
        self.category = data.get("category")
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "ingredient_id": self.ingredient_id,
            "name": self.name,
            "calories_per_100g": self.calories_per_100g,
            "proteins_per_100g": self.proteins_per_100g,
            "fat_per_100g": self.fat_per_100g,
            "carbs_per_100g": self.carbs_per_100g,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class MockIngredientDatabase:
    """Mock database for ingredients testing."""

    def __init__(self):
        self.ingredients = {}
        self.id_counter = 1

    def add_ingredient(self, data: Dict[str, Any]) -> str:
        """Add ingredient to mock database."""
        ingredient_id = f"mock-id-{self.id_counter}"
        self.id_counter += 1

        ingredient_data = {
            "ingredient_id": ingredient_id,
            **data,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        self.ingredients[ingredient_id] = MockSupabaseIngredient(ingredient_data)
        return ingredient_id

    def get_ingredient(self, ingredient_id: str) -> Optional[MockSupabaseIngredient]:
        """Get ingredient from mock database."""
        return self.ingredients.get(ingredient_id)

    def get_all_ingredients(self) -> List[MockSupabaseIngredient]:
        """Get all ingredients from mock database."""
        return list(self.ingredients.values())

    def update_ingredient(
        self, ingredient_id: str, data: Dict[str, Any]
    ) -> Optional[MockSupabaseIngredient]:
        """Update ingredient in mock database."""
        if ingredient_id in self.ingredients:
            ingredient = self.ingredients[ingredient_id]
            for key, value in data.items():
                if hasattr(ingredient, key):
                    setattr(ingredient, key, value)
            ingredient.updated_at = "2024-01-02T00:00:00Z"
            return ingredient
        return None

    def delete_ingredient(self, ingredient_id: str) -> bool:
        """Delete ingredient from mock database."""
        if ingredient_id in self.ingredients:
            del self.ingredients[ingredient_id]
            return True
        return False

    def search_ingredients(self, query: str) -> List[MockSupabaseIngredient]:
        """Search ingredients in mock database."""
        results = []
        query_lower = query.lower()
        for ingredient in self.ingredients.values():
            if query_lower in ingredient.name.lower():
                results.append(ingredient)
        return results

    def clear(self):
        """Clear all ingredients from mock database."""
        self.ingredients.clear()
        self.id_counter = 1
