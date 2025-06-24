"""
Unit Tests for Error Handling in Ingredients Service.

This module tests error handling and exception scenarios with real database.
"""

from uuid import UUID

import pytest
from domains.ingredients.schemas import IngredientListResponse
from domains.ingredients.services import (IngredientError, get_all_ingredients,
                                          get_ingredient_by_id,
                                          search_ingredients)
from tests.ingredients.config import IngredientsTestBase


class TestIngredientsErrorHandling(IngredientsTestBase):
    """Test error handling scenarios for ingredients service."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic error handling functionality."""
        # Test that our error classes work
        error = IngredientError("Test error message")
        assert str(error) == "Test error message"

    def test_ingredient_error_creation(self):
        """Test that IngredientError can be created with different parameters."""
        # Test with message only
        error1 = IngredientError("Simple error")
        assert error1.message == "Simple error"

        # Test with message and code
        error2 = IngredientError("Error with code", "ERROR_CODE")
        assert error2.message == "Error with code"
        assert error2.error_code == "ERROR_CODE"

    def test_ingredient_error_inheritance(self):
        """Test that IngredientError inherits from Exception correctly."""
        error = IngredientError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, IngredientError)

    @pytest.mark.asyncio
    async def test_get_ingredient_by_id_not_found(self):
        """Test error when ingredient is not found by ID."""
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")

        with pytest.raises(IngredientError) as exc_info:
            await get_ingredient_by_id(non_existent_id)

        # Verify error details
        assert exc_info.value.error_code == "INGREDIENT_NOT_FOUND"
        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_search_ingredients_edge_cases(self):
        """Test search with edge case inputs."""
        # Empty query - should work (returns all)
        result1 = await search_ingredients(query="", limit=5, offset=0)
        assert isinstance(result1, IngredientListResponse)

        # Very long query - should work
        long_query = "a" * 100
        result2 = await search_ingredients(query=long_query, limit=5, offset=0)
        assert isinstance(result2, IngredientListResponse)

        # Special characters - should work
        result3 = await search_ingredients(query="@#$%", limit=5, offset=0)
        assert isinstance(result3, IngredientListResponse)

    @pytest.mark.asyncio
    async def test_search_ingredients_boundary_values(self):
        """Test search with boundary limit and offset values."""
        # Limit = 0 should return empty list
        result1 = await search_ingredients(query="test", limit=0, offset=0)
        assert isinstance(result1, IngredientListResponse)
        assert len(result1.ingredients) == 0

        # Very high offset should return empty list
        result2 = await search_ingredients(query="test", limit=10, offset=99999)
        assert isinstance(result2, IngredientListResponse)
        assert len(result2.ingredients) == 0

    @pytest.mark.asyncio
    async def test_get_all_ingredients_boundary_values(self):
        """Test get_all_ingredients with boundary values."""
        # Limit = 0 should return empty list
        result1 = await get_all_ingredients(limit=0, offset=0)
        assert isinstance(result1, IngredientListResponse)
        assert len(result1.ingredients) == 0

        # Very high offset should return empty list
        result2 = await get_all_ingredients(limit=10, offset=99999)
        assert isinstance(result2, IngredientListResponse)
        assert len(result2.ingredients) == 0

    @pytest.mark.asyncio
    async def test_large_limit_handling(self):
        """Test behavior with very large limits."""
        # Very large limit should be handled gracefully
        result = await search_ingredients(query="test", limit=10000, offset=0)
        assert isinstance(result, IngredientListResponse)
        assert len(result.ingredients) <= 10000  # Should not exceed actual data

    def test_error_message_formatting(self):
        """Test that error messages are properly formatted."""
        error1 = IngredientError("Simple message")
        assert len(str(error1)) > 0

        error2 = IngredientError("Message with code", "CODE123")
        assert len(str(error2)) > 0
        assert error2.error_code == "CODE123"

    def test_error_with_special_characters(self):
        """Test error handling with special characters in messages."""
        special_message = "Error with special chars: äöü @#$%^&*()"
        error = IngredientError(special_message)

        assert error.message == special_message
        assert str(error) == special_message

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test that concurrent operations work correctly."""
        import asyncio

        # Create multiple concurrent operations
        tasks = [
            search_ingredients(query="test", limit=5, offset=0),
            get_all_ingredients(limit=5, offset=0),
            search_ingredients(query="another", limit=3, offset=0),
        ]

        # All should complete successfully
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all results are valid responses
        for result in results:
            if isinstance(result, Exception):
                # Unexpected exception
                pytest.fail(f"Unexpected exception: {result}")
            else:
                assert isinstance(result, IngredientListResponse)

    @pytest.mark.asyncio
    async def test_invalid_uuid_formats(self):
        """Test behavior with various invalid UUID formats."""
        invalid_uuids = [
            "not-a-uuid",
            "123",
            "",
            "00000000-0000-0000-0000-00000000000",  # Too short
        ]

        for invalid_uuid in invalid_uuids:
            try:
                # This should fail at UUID conversion, not in our service
                uuid_obj = UUID(invalid_uuid)
                # If we get here, the UUID was valid enough
                with pytest.raises(IngredientError):
                    await get_ingredient_by_id(uuid_obj)
            except ValueError:
                # Expected - invalid UUID format
                pass

    @pytest.mark.asyncio
    async def test_error_consistency(self):
        """Test that errors are consistent across operations."""
        non_existent_id = UUID("11111111-1111-1111-1111-111111111111")

        # Multiple calls should give consistent errors
        for _ in range(3):
            with pytest.raises(IngredientError) as exc_info:
                await get_ingredient_by_id(non_existent_id)

            assert exc_info.value.error_code == "INGREDIENT_NOT_FOUND"
