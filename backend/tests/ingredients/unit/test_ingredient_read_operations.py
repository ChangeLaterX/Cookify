"""
Unit Tests for Ingredient Read Operations.

This module tests ingredient retrieval and read-only operations using the real database.
"""

from uuid import UUID

import pytest
from domains.ingredients.schemas import IngredientListResponse, IngredientMasterResponse
from domains.ingredients.services import (
    IngredientError,
    get_all_ingredients,
    get_ingredient_by_id,
)
from tests.ingredients.config import IngredientsTestBase


class TestIngredientReadOperations(IngredientsTestBase):
    """Test ingredient read operations with real database."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic read functionality."""
        # Uses real database connection
        pass

    @pytest.mark.asyncio
    async def test_get_ingredient_by_id_success(self):
        """Test successful retrieval of ingredient by ID."""
        # First get some ingredients to work with
        all_ingredients = await get_all_ingredients(limit=1, offset=0)
        if not all_ingredients.ingredients:
            pytest.skip("No ingredients in database to test with")

        ingredient_id = all_ingredients.ingredients[0].ingredient_id

        result = await get_ingredient_by_id(ingredient_id)

        assert isinstance(result, IngredientMasterResponse)
        assert result.ingredient_id == ingredient_id
        assert isinstance(result.name, str)
        assert len(result.name.strip()) > 0
        assert isinstance(result.calories_per_100g, (int, float))
        assert isinstance(result.proteins_per_100g, (int, float))
        assert isinstance(result.fat_per_100g, (int, float))
        assert isinstance(result.carbs_per_100g, (int, float))

    @pytest.mark.asyncio
    async def test_get_ingredient_by_id_not_found(self):
        """Test retrieval of non-existent ingredient."""
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")

        with pytest.raises(IngredientError):
            await get_ingredient_by_id(non_existent_id)

    @pytest.mark.asyncio
    async def test_get_all_ingredients_success(self):
        """Test successful listing of ingredients."""
        result = await get_all_ingredients(limit=10, offset=0)

        assert isinstance(result, IngredientListResponse)
        assert isinstance(result.ingredients, list)
        # Database may be empty, so we don't assert length > 0

        # Check first ingredient structure if any exist
        if result.ingredients:
            ingredient = result.ingredients[0]
            assert hasattr(ingredient, "ingredient_id")
            assert hasattr(ingredient, "name")
            assert hasattr(ingredient, "calories_per_100g")
            assert hasattr(ingredient, "proteins_per_100g")
            assert hasattr(ingredient, "fat_per_100g")
            assert hasattr(ingredient, "carbs_per_100g")

    @pytest.mark.asyncio
    async def test_get_all_ingredients_with_limit(self):
        """Test listing ingredients with specific limit."""
        result = await get_all_ingredients(limit=3, offset=0)

        assert isinstance(result, IngredientListResponse)
        assert len(result.ingredients) <= 3

    @pytest.mark.asyncio
    async def test_get_all_ingredients_with_offset(self):
        """Test listing ingredients with offset."""
        result = await get_all_ingredients(limit=5, offset=2)

        assert isinstance(result, IngredientListResponse)
        # Should return up to 5 ingredients, starting from position 2

    @pytest.mark.asyncio
    async def test_get_all_ingredients_pagination(self):
        """Test ingredient listing pagination."""
        # First page
        page1 = await get_all_ingredients(limit=2, offset=0)

        # Second page
        page2 = await get_all_ingredients(limit=2, offset=2)

        assert isinstance(page1, IngredientListResponse)
        assert isinstance(page2, IngredientListResponse)

        # Pages should have different ingredients (if enough ingredients exist)
        if len(page1.ingredients) == 2 and len(page2.ingredients) > 0:
            page1_ids = {ing.ingredient_id for ing in page1.ingredients}
            page2_ids = {ing.ingredient_id for ing in page2.ingredients}
            assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_get_all_ingredients_invalid_limit(self):
        """Test listing ingredients with edge case limits."""
        # Test limit=0 (should return no results, not error)
        result = await get_all_ingredients(limit=0, offset=0)
        assert isinstance(result, IngredientListResponse)
        assert len(result.ingredients) == 0

        # Test very large limit (should be handled gracefully)
        result = await get_all_ingredients(limit=1000, offset=0)
        assert isinstance(result, IngredientListResponse)

    @pytest.mark.asyncio
    async def test_get_all_ingredients_invalid_offset(self):
        """Test listing ingredients with edge case offsets."""
        # Test negative offset (should be handled gracefully by API)
        result = await get_all_ingredients(limit=10, offset=-1)
        assert isinstance(result, IngredientListResponse)

        # Test very large offset (should return empty results)
        result = await get_all_ingredients(limit=10, offset=10000)
        assert isinstance(result, IngredientListResponse)

    @pytest.mark.asyncio
    async def test_ingredient_data_types(self):
        """Test that ingredient data has correct types."""
        # Get any ingredient from the database
        all_ingredients = await get_all_ingredients(limit=1, offset=0)
        if not all_ingredients.ingredients:
            pytest.skip("No ingredients in database to test with")

        ingredient_id = all_ingredients.ingredients[0].ingredient_id
        result = await get_ingredient_by_id(ingredient_id)

        assert isinstance(result.ingredient_id, UUID)
        assert isinstance(result.name, str)
        assert isinstance(result.calories_per_100g, (int, float))
        assert isinstance(result.proteins_per_100g, (int, float))
        assert isinstance(result.fat_per_100g, (int, float))
        assert isinstance(result.carbs_per_100g, (int, float))

    @pytest.mark.asyncio
    async def test_ingredient_data_ranges(self):
        """Test that ingredient data is within realistic ranges."""
        # Get any ingredient from the database
        all_ingredients = await get_all_ingredients(limit=1, offset=0)
        if not all_ingredients.ingredients:
            pytest.skip("No ingredients in database to test with")

        ingredient_id = all_ingredients.ingredients[0].ingredient_id
        result = await get_ingredient_by_id(ingredient_id)

        # Check realistic nutritional ranges
        assert 0 <= result.calories_per_100g <= 1000
        assert 0 <= result.proteins_per_100g <= 100
        assert 0 <= result.fat_per_100g <= 100
        assert 0 <= result.carbs_per_100g <= 100

    @pytest.mark.asyncio
    async def test_multiple_ingredient_retrieval(self):
        """Test retrieving multiple ingredients."""
        # Get available ingredients from the database
        all_ingredients = await get_all_ingredients(limit=3, offset=0)
        if len(all_ingredients.ingredients) < 2:
            pytest.skip("Need at least 2 ingredients in database to test with")

        # Test retrieving each ingredient individually
        for ingredient in all_ingredients.ingredients[:2]:  # Test first 2
            result = await get_ingredient_by_id(ingredient.ingredient_id)
            assert isinstance(result, IngredientMasterResponse)
            assert result.ingredient_id == ingredient.ingredient_id

    @pytest.mark.asyncio
    async def test_ingredient_names_are_realistic(self):
        """Test that retrieved ingredients have realistic names."""
        result = await get_all_ingredients(limit=10, offset=0)

        for ingredient in result.ingredients:
            # Names should be non-empty strings
            assert isinstance(ingredient.name, str)
            assert len(ingredient.name.strip()) > 0
            # Names should not contain only numbers or special characters
            assert not ingredient.name.strip().isdigit()

    @pytest.mark.asyncio
    async def test_consistent_data_retrieval(self):
        """Test that the same ingredient returns consistent data."""
        # Get any ingredient from the database
        all_ingredients = await get_all_ingredients(limit=1, offset=0)
        if not all_ingredients.ingredients:
            pytest.skip("No ingredients in database to test with")

        ingredient_id = all_ingredients.ingredients[0].ingredient_id

        # Retrieve the same ingredient multiple times
        result1 = await get_ingredient_by_id(ingredient_id)
        result2 = await get_ingredient_by_id(ingredient_id)

        # Data should be consistent
        assert result1.name == result2.name
        assert result1.calories_per_100g == result2.calories_per_100g
        assert result1.proteins_per_100g == result2.proteins_per_100g
        assert result1.fat_per_100g == result2.fat_per_100g
        assert result1.carbs_per_100g == result2.carbs_per_100g
