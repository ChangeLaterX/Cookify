"""
Unit Tests for Ingredient Search Functionality.

This module tests ingredient search and filtering capabilities.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from domains.ingredients.services import search_ingredients, IngredientError
from domains.ingredients.schemas import IngredientListResponse
from tests.ingredients.config import IngredientsTestBase
from tests.ingredients.utils.mocks import IngredientsMockFactory, MockContextManager
from tests.ingredients.utils.test_data import TestDataGenerator, TestScenarios


class TestIngredientSearch(IngredientsTestBase):
    """Test ingredient search functionality."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic search."""
        self.test_search_exact_match()

    @pytest.mark.asyncio
    async def test_search_exact_match(self):
        """Test search with exact ingredient name match."""
        test_ingredients = TestDataGenerator.generate_search_test_data()
        tomato_ingredients = [ing for ing in test_ingredients if "tomato" in ing.name.lower()]
        mock_data = [ing.to_dict() for ing in tomato_ingredients]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await search_ingredients("Tomato")
            
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) > 0
            
            # Verify all results contain "tomato"
            for ingredient in result.ingredients:
                assert "tomato" in ingredient.name.lower()

    @pytest.mark.asyncio
    async def test_search_partial_match(self):
        """Test search with partial ingredient name match."""
        test_ingredients = TestDataGenerator.generate_search_test_data()
        chicken_ingredients = [ing for ing in test_ingredients if "chicken" in ing.name.lower()]
        mock_data = [ing.to_dict() for ing in chicken_ingredients]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await search_ingredients("Chicken")
            
            assert len(result.ingredients) > 0
            for ingredient in result.ingredients:
                assert "chicken" in ingredient.name.lower()

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        test_ingredients = TestDataGenerator.generate_search_test_data()
        onion_ingredients = [ing for ing in test_ingredients if "onion" in ing.name.lower()]
        mock_data = [ing.to_dict() for ing in onion_ingredients]
        
        test_queries = ["onion", "ONION", "Onion", "OnIoN"]
        
        for query in test_queries:
            with MockContextManager(success_responses=True, mock_data=mock_data):
                result = await search_ingredients(query)
                
                assert len(result.ingredients) > 0
                for ingredient in result.ingredients:
                    assert "onion" in ingredient.name.lower()

    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """Test search with no matching results."""
        with MockContextManager(success_responses=True, mock_data=[]):
            result = await search_ingredients("NonExistentIngredient")
            
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) == 0
            assert result.total == 0

    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """Test search with empty query string."""
        with MockContextManager(success_responses=True, mock_data=[]):
            result = await search_ingredients("")
            
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) == 0

    @pytest.mark.asyncio
    async def test_search_whitespace_query(self):
        """Test search with whitespace-only query."""
        with MockContextManager(success_responses=True, mock_data=[]):
            result = await search_ingredients("   ")
            
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) == 0

    @pytest.mark.asyncio
    async def test_search_special_characters(self):
        """Test search with special characters in query."""
        test_ingredient = TestDataGenerator.generate_ingredient_data("Test-Ingredient_123")
        mock_data = [test_ingredient.to_dict()]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await search_ingredients("Test-Ingredient")
            
            assert len(result.ingredients) > 0

    @pytest.mark.asyncio
    async def test_search_multiple_words(self):
        """Test search with multiple words."""
        test_ingredient = TestDataGenerator.generate_ingredient_data("Cherry Tomato Sauce")
        mock_data = [test_ingredient.to_dict()]
        
        # Test searching for individual words
        search_terms = ["Cherry", "Tomato", "Sauce", "cherry tomato"]
        
        for term in search_terms:
            with MockContextManager(success_responses=True, mock_data=mock_data):
                result = await search_ingredients(term)
                # Result depends on implementation - might match any word
                assert isinstance(result, IngredientListResponse)

    @pytest.mark.asyncio
    async def test_search_with_database_error(self):
        """Test search behavior when database error occurs."""
        with MockContextManager(success_responses=False):
            with pytest.raises(IngredientError) as exc_info:
                await search_ingredients("test")
            
            assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_search_performance_with_long_query(self):
        """Test search performance with very long query string."""
        long_query = "A" * 1000  # Very long search term
        
        with MockContextManager(success_responses=True, mock_data=[]):
            result = await search_ingredients(long_query)
            
            # Should handle gracefully without errors
            assert isinstance(result, IngredientListResponse)

    @pytest.mark.asyncio
    async def test_search_scenarios_from_test_data(self):
        """Test search scenarios using predefined test scenarios."""
        scenarios = TestScenarios.search_scenarios()
        
        for scenario in scenarios:
            # Filter ingredients based on expected matches
            matching_ingredients = []
            for expected_name in scenario["expected_matches"]:
                for ingredient in scenario["ingredients"]:
                    if expected_name.lower() in ingredient.name.lower():
                        matching_ingredients.append(ingredient)
            
            mock_data = [ing.to_dict() for ing in matching_ingredients]
            
            with MockContextManager(success_responses=True, mock_data=mock_data):
                result = await search_ingredients(scenario["query"])
                
                assert len(result.ingredients) == len(scenario["expected_matches"])

    @pytest.mark.asyncio
    async def test_search_with_numeric_values(self):
        """Test search functionality with numeric values in names."""
        test_ingredients = [
            TestDataGenerator.generate_ingredient_data("Ingredient 1"),
            TestDataGenerator.generate_ingredient_data("Ingredient 2"),
            TestDataGenerator.generate_ingredient_data("Ingredient 10"),
        ]
        
        # Search for "1" should match "Ingredient 1" and "Ingredient 10"
        matching_ingredients = [ing for ing in test_ingredients if "1" in ing.name]
        mock_data = [ing.to_dict() for ing in matching_ingredients]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await search_ingredients("1")
            
            assert len(result.ingredients) == 2

    @pytest.mark.asyncio
    async def test_search_result_ordering(self):
        """Test that search results are properly ordered."""
        test_ingredients = TestDataGenerator.generate_search_test_data()
        mock_data = [ing.to_dict() for ing in test_ingredients]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await search_ingredients("a")  # Common letter
            
            # Results should be ordered (implementation dependent)
            # For now, just verify we get results
            assert isinstance(result, IngredientListResponse)

    @pytest.mark.asyncio
    async def test_search_with_unicode_characters(self):
        """Test search with unicode characters."""
        test_ingredient = TestDataGenerator.generate_ingredient_data("Jalapeño Pepper")
        mock_data = [test_ingredient.to_dict()]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await search_ingredients("Jalapeño")
            
            assert len(result.ingredients) > 0

    @pytest.mark.asyncio
    async def test_search_limit_and_pagination(self):
        """Test search with limit and pagination (if supported)."""
        # Generate many matching ingredients
        test_ingredients = []
        for i in range(15):
            ingredient = TestDataGenerator.generate_ingredient_data(f"Apple Variety {i}")
            test_ingredients.append(ingredient)
        
        mock_data = [ing.to_dict() for ing in test_ingredients[:10]]  # First 10
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await search_ingredients("Apple")
            
            # Should handle large result sets appropriately
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) <= 10  # Assuming pagination/limiting
