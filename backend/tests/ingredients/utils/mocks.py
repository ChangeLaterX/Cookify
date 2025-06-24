"""
Mock Utilities for Ingredients Testing.

This module provides mock factories and context managers for Ingredients tests.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

from domains.ingredients.schemas import (
    IngredientListResponse,
    IngredientMasterCreate,
    IngredientMasterResponse,
    IngredientMasterUpdate,
)


class IngredientsMockFactory:
    """Factory for creating Ingredients-related mocks."""

    @staticmethod
    def create_ingredient_create(
        name: Optional[str] = None,
        calories_per_100g: Optional[float] = None,
        proteins_per_100g: Optional[float] = None,
        fat_per_100g: Optional[float] = None,
        carbs_per_100g: Optional[float] = None,
    ) -> IngredientMasterCreate:
        """Create a mock IngredientMasterCreate schema."""
        return IngredientMasterCreate(
            name=name or f"Test Ingredient {uuid.uuid4().hex[:8]}",
            calories_per_100g=calories_per_100g or 100.0,
            proteins_per_100g=proteins_per_100g or 10.0,
            fat_per_100g=fat_per_100g or 5.0,
            carbs_per_100g=carbs_per_100g or 15.0,
        )

    @staticmethod
    def create_ingredient_update(
        name: Optional[str] = None,
        calories_per_100g: Optional[float] = None,
        proteins_per_100g: Optional[float] = None,
        fat_per_100g: Optional[float] = None,
        carbs_per_100g: Optional[float] = None,
        price_per_100g_cents: Optional[int] = None,
    ) -> IngredientMasterUpdate:
        """Create a mock IngredientMasterUpdate schema."""
        return IngredientMasterUpdate(
            name=name,
            calories_per_100g=calories_per_100g,
            proteins_per_100g=proteins_per_100g,
            fat_per_100g=fat_per_100g,
            carbs_per_100g=carbs_per_100g,
            price_per_100g_cents=price_per_100g_cents,
        )

    @staticmethod
    def create_ingredient_response(
        ingredient_id: Optional[str] = None,
        name: Optional[str] = None,
        calories_per_100g: Optional[float] = None,
        proteins_per_100g: Optional[float] = None,
        fat_per_100g: Optional[float] = None,
        carbs_per_100g: Optional[float] = None,
        price_per_100g_cents: Optional[int] = None,
    ) -> IngredientMasterResponse:
        """Create a mock IngredientMasterResponse."""
        return IngredientMasterResponse(
            ingredient_id=ingredient_id or str(uuid.uuid4()),
            name=name or f"Test Ingredient {uuid.uuid4().hex[:8]}",
            calories_per_100g=calories_per_100g or 100.0,
            proteins_per_100g=proteins_per_100g or 10.0,
            fat_per_100g=fat_per_100g or 5.0,
            carbs_per_100g=carbs_per_100g or 15.0,
            price_per_100g_cents=price_per_100g_cents or 500,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @staticmethod
    def create_ingredient_dict(
        ingredient_id: Optional[str] = None,
        name: Optional[str] = None,
        calories_per_100g: Optional[float] = None,
        proteins_per_100g: Optional[float] = None,
        fat_per_100g: Optional[float] = None,
        carbs_per_100g: Optional[float] = None,
        price_per_100g_cents: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a mock ingredient dictionary."""
        return {
            "ingredient_id": ingredient_id or str(uuid.uuid4()),
            "name": name or f"Test Ingredient {uuid.uuid4().hex[:8]}",
            "calories_per_100g": calories_per_100g or 100.0,
            "proteins_per_100g": proteins_per_100g or 10.0,
            "fat_per_100g": fat_per_100g or 5.0,
            "carbs_per_100g": carbs_per_100g or 15.0,
            "price_per_100g_cents": price_per_100g_cents or 500,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def create_supabase_response(
        success: bool = True,
        data: Optional[List[Dict[str, Any]]] = None,
        error_message: Optional[str] = None,
    ) -> Mock:
        """Create a mock Supabase response object."""
        response = Mock()

        if success:
            response.data = data or [IngredientsMockFactory.create_ingredient_dict()]
            response.error = None
        else:
            response.data = None
            response.error = error_message or "Database error"

        return response

    @staticmethod
    def create_ingredient_list_response(
        ingredients: Optional[List[Dict[str, Any]]] = None,
        total: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> IngredientListResponse:
        """Create a mock IngredientListResponse."""
        if ingredients is None:
            ingredients = [
                IngredientsMockFactory.create_ingredient_dict() for _ in range(3)
            ]

        ingredient_responses = [IngredientMasterResponse(**ing) for ing in ingredients]

        return IngredientListResponse(
            ingredients=ingredient_responses,
            total=total or len(ingredients),
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def create_ingredient_error(
        message: str = "Ingredient operation failed", error_code: Optional[str] = None
    ) -> Exception:
        """Create a mock ingredient error."""
        from domains.ingredients.services import IngredientError

        return IngredientError(message, error_code)


class MockContextManager:
    """Context manager for setting up Ingredients mocks."""

    def __init__(
        self,
        mock_supabase: bool = True,
        success_responses: bool = True,
        mock_data: Optional[List[Dict[str, Any]]] = None,
    ):
        self.mock_supabase = mock_supabase
        self.success_responses = success_responses
        self.mock_data = mock_data or []
        self.patches = []

    def __enter__(self):
        """Setup mocks when entering context."""
        if self.mock_supabase:
            # Mock Supabase client
            self.patches.append(
                patch(
                    "domains.ingredients.services.get_supabase_client",
                    return_value=self._create_mock_supabase_client(),
                )
            )

        # Start all patches
        for p in self.patches:
            p.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup mocks when exiting context."""
        for p in self.patches:
            p.stop()

    def _create_mock_supabase_client(self) -> Mock:
        """Create a mock Supabase client."""
        client = Mock()

        # Mock table operations
        table_mock = Mock()
        client.table.return_value = table_mock

        if self.success_responses:
            # Chain mock for query building
            query_chain = Mock()

            # Mock data for responses
            response_data = self.mock_data or [
                IngredientsMockFactory.create_ingredient_dict()
            ]

            # Mock execute responses
            execute_response = Mock()
            execute_response.data = response_data
            execute_response.error = None

            # Setup method chaining
            table_mock.select.return_value = query_chain
            table_mock.insert.return_value = query_chain
            table_mock.update.return_value = query_chain
            table_mock.delete.return_value = query_chain

            query_chain.range.return_value = query_chain
            query_chain.order.return_value = query_chain
            query_chain.eq.return_value = query_chain
            query_chain.ilike.return_value = query_chain
            query_chain.execute.return_value = execute_response

        else:
            # Mock error responses
            error_response = Mock()
            error_response.data = None
            error_response.error = "Database error"

            # Setup method chaining for errors
            query_chain = Mock()
            table_mock.select.return_value = query_chain
            table_mock.insert.return_value = query_chain
            table_mock.update.return_value = query_chain
            table_mock.delete.return_value = query_chain

            query_chain.range.return_value = query_chain
            query_chain.order.return_value = query_chain
            query_chain.eq.return_value = query_chain
            query_chain.ilike.return_value = query_chain
            query_chain.execute.return_value = error_response

        return client


def with_mocked_ingredients(
    success: bool = True, mock_data: Optional[List[Dict[str, Any]]] = None
):
    """Decorator for mocking Ingredients dependencies in tests."""

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with MockContextManager(success_responses=success, mock_data=mock_data):
                return test_func(*args, **kwargs)

        return wrapper

    return decorator


class MockIngredientSearch:
    """Mock ingredient search functionality for testing."""

    def __init__(self, ingredients: List[Dict[str, Any]]):
        self.ingredients = ingredients

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Mock search functionality."""
        results = []
        query_lower = query.lower()

        for ingredient in self.ingredients:
            if query_lower in ingredient.get("name", "").lower():
                results.append(ingredient)

        return results

    def fuzzy_search(self, query: str, threshold: float = 0.6) -> List[Dict[str, Any]]:
        """Mock fuzzy search functionality."""
        # Simple mock - in real implementation would use fuzzy matching
        return self.search(query)


class MockIngredientValidator:
    """Mock ingredient validation for testing."""

    @staticmethod
    def validate_nutrition_data(
        calories: float, proteins: float, fat: float, carbs: float
    ) -> bool:
        """Mock nutrition data validation."""
        # Simple validation rules
        return all(
            [
                calories >= 0,
                proteins >= 0,
                fat >= 0,
                carbs >= 0,
                calories <= 1000,  # Reasonable upper limit
                proteins <= 100,
                fat <= 100,
                carbs <= 100,
            ]
        )

    @staticmethod
    def validate_price(price_cents: int) -> bool:
        """Mock price validation."""
        return 0 <= price_cents <= 100000  # $0 to $1000

    @staticmethod
    def validate_name(name: str) -> bool:
        """Mock name validation."""
        return len(name.strip()) > 0 and len(name) <= 255


class MockIngredientCache:
    """Mock ingredient caching for testing."""

    def __init__(self):
        self.cache = {}
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Mock cache get."""
        if key in self.cache:
            self.hit_count += 1
            return self.cache[key]
        else:
            self.miss_count += 1
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Mock cache set."""
        self.cache[key] = value

    def delete(self, key: str) -> bool:
        """Mock cache delete."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Mock cache clear."""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "hits": self.hit_count,
            "misses": self.miss_count,
            "items": len(self.cache),
        }
