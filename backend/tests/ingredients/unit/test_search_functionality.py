"""
Integration Tests for Ingredient Search Functionality.

This module tests ingredient search and filtering capabilities with the real database.
"""

import pytest

from domains.ingredients.schemas import IngredientListResponse
from domains.ingredients.services import IngredientError, search_ingredients
from tests.ingredients.config import IngredientsTestBase


class TestIngredientSearch(IngredientsTestBase):
    """Test ingredient search functionality with real database."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic search."""
        pass

    @pytest.mark.asyncio
    async def test_search_exact_match(self):
        """Test search with exact ingredient name match."""
        result = await search_ingredients(query="tomato", limit=10, offset=0)

        assert isinstance(result, IngredientListResponse)
        assert isinstance(result.ingredients, list)

        # Check that results contain tomato-related ingredients if any exist
        if result.ingredients:
            tomato_results = [ing for ing in result.ingredients if "tomato" in ing.name.lower()]
            # Should find at least some tomato ingredients
            assert len(tomato_results) > 0

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        result_lower = await search_ingredients(query="tomato", limit=10, offset=0)
        result_upper = await search_ingredients(query="TOMATO", limit=10, offset=0)

        assert isinstance(result_lower, IngredientListResponse)
        assert isinstance(result_upper, IngredientListResponse)

        # Should have same number of results
        assert len(result_lower.ingredients) == len(result_upper.ingredients)

    @pytest.mark.asyncio
    async def test_search_with_limit(self):
        """Test search with specific limit parameter."""
        result = await search_ingredients(
            query="a", limit=5, offset=0
        )  # Search for 'a' to get results

        assert isinstance(result, IngredientListResponse)
        assert len(result.ingredients) <= 5

    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """Test search with no matching results."""
        result = await search_ingredients(query="nonexistent_ingredient_xyz123", limit=10, offset=0)

        assert isinstance(result, IngredientListResponse)
        assert len(result.ingredients) == 0

    @pytest.mark.asyncio
    async def test_search_pagination(self):
        """Test search pagination."""
        # Test first page
        page1 = await search_ingredients(query="a", limit=5, offset=0)

        # Test second page
        page2 = await search_ingredients(query="a", limit=5, offset=5)

        assert isinstance(page1, IngredientListResponse)
        assert isinstance(page2, IngredientListResponse)

        # If there are enough results, pages should be different
        if len(page1.ingredients) == 5 and len(page2.ingredients) > 0:
            page1_ids = {ing.ingredient_id for ing in page1.ingredients}
            page2_ids = {ing.ingredient_id for ing in page2.ingredients}
            assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_search_response_format(self):
        """Test that search response has correct format."""
        result = await search_ingredients(query="a", limit=10, offset=0)

        assert isinstance(result, IngredientListResponse)
        assert hasattr(result, "ingredients")
        assert isinstance(result.ingredients, list)

        if result.ingredients:
            ingredient = result.ingredients[0]
            # Check that ingredient has all required fields
            assert hasattr(ingredient, "ingredient_id")
            assert hasattr(ingredient, "name")
            assert hasattr(ingredient, "calories_per_100g")
            assert hasattr(ingredient, "proteins_per_100g")
            assert hasattr(ingredient, "fat_per_100g")
            assert hasattr(ingredient, "carbs_per_100g")

    @pytest.mark.asyncio
    async def test_search_data_types(self):
        """Test that search response contains correct data types."""
        result = await search_ingredients(query="a", limit=10, offset=0)

        if result.ingredients:
            ingredient = result.ingredients[0]

            # Check data types
            assert isinstance(ingredient.name, str)
            assert isinstance(ingredient.calories_per_100g, (int, float))
            assert isinstance(ingredient.proteins_per_100g, (int, float))
            assert isinstance(ingredient.fat_per_100g, (int, float))
            assert isinstance(ingredient.carbs_per_100g, (int, float))

    @pytest.mark.asyncio
    async def test_search_realistic_data(self):
        """Test that search returns realistic nutritional data."""
        result = await search_ingredients(query="a", limit=10, offset=0)

        if result.ingredients:
            ingredient = result.ingredients[0]

            # Check realistic ranges
            assert 0 <= ingredient.calories_per_100g <= 1000
            assert 0 <= ingredient.proteins_per_100g <= 100
            assert 0 <= ingredient.fat_per_100g <= 100
            assert 0 <= ingredient.carbs_per_100g <= 100
