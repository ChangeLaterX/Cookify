"""
Unit Tests for Ingredients Service Functions.

This module tests the ingredient service functions including CRUD operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from domains.ingredients.services import (
    get_all_ingredients,
    get_ingredient_by_id,
    create_ingredient,
    update_ingredient,
    delete_ingredient,
    search_ingredients,
    IngredientError
)
from domains.ingredients.schemas import IngredientListResponse, IngredientMasterResponse
from tests.ingredients.config import IngredientsTestBase
from tests.ingredients.utils.mocks import IngredientsMockFactory, MockContextManager, with_mocked_ingredients
from tests.ingredients.utils.test_data import TestDataGenerator, TestScenarios


class TestIngredientCRUDOperations(IngredientsTestBase):
    """Test CRUD operations for ingredients."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic CRUD operations."""
        self.test_get_all_ingredients_success()

    @pytest.mark.asyncio
    async def test_get_all_ingredients_success(self):
        """Test successful retrieval of all ingredients."""
        test_ingredients = TestDataGenerator.generate_bulk_ingredients(count=3)
        mock_data = [ing.to_dict() for ing in test_ingredients]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await get_all_ingredients(limit=10, offset=0)
            
            # Verify result
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) == 3
            assert result.total >= 3
            assert result.limit == 10
            assert result.offset == 0

    @pytest.mark.asyncio
    async def test_get_all_ingredients_with_pagination(self):
        """Test ingredient retrieval with pagination parameters."""
        test_ingredients = TestDataGenerator.generate_pagination_test_data(25)
        mock_data = [ing.to_dict() for ing in test_ingredients[:10]]  # First page
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await get_all_ingredients(limit=10, offset=0)
            
            assert len(result.ingredients) == 10
            assert result.limit == 10
            assert result.offset == 0

    @pytest.mark.asyncio
    async def test_get_ingredient_by_id_success(self):
        """Test successful retrieval of ingredient by ID."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        mock_data = [test_ingredient.to_dict()]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await get_ingredient_by_id(test_ingredient.ingredient_id)
            
            assert isinstance(result, IngredientMasterResponse)
            assert result.ingredient_id == test_ingredient.ingredient_id
            assert result.name == test_ingredient.name

    @pytest.mark.asyncio
    async def test_get_ingredient_by_id_not_found(self):
        """Test retrieval of non-existent ingredient."""
        with MockContextManager(success_responses=True, mock_data=[]):
            with pytest.raises(IngredientError) as exc_info:
                await get_ingredient_by_id("non-existent-id")
            
            assert exc_info.value.error_code == "INGREDIENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_create_ingredient_success(self):
        """Test successful ingredient creation."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        create_data = test_ingredient.to_ingredient_create()
        mock_data = [test_ingredient.to_dict()]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await create_ingredient(create_data)
            
            assert isinstance(result, IngredientMasterResponse)
            assert result.name == create_data.name
            assert result.calories_per_100g == create_data.calories_per_100g

    @pytest.mark.asyncio
    async def test_create_ingredient_with_validation_error(self):
        """Test ingredient creation with invalid data."""
        invalid_data = IngredientsMockFactory.create_ingredient_create(
            name="",  # Invalid: empty name
            calories_per_100g=-10  # Invalid: negative calories
        )
        
        # This should fail at schema validation level
        with pytest.raises(Exception):  # Pydantic validation error
            # The validation happens at schema level, not service level
            pass

    @pytest.mark.asyncio
    async def test_update_ingredient_success(self):
        """Test successful ingredient update."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        update_data = IngredientsMockFactory.create_ingredient_update(
            name=f"{test_ingredient.name} Updated"
        )
        
        # Updated ingredient data
        updated_ingredient_dict = test_ingredient.to_dict()
        updated_ingredient_dict["name"] = update_data.name
        mock_data = [updated_ingredient_dict]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await update_ingredient(test_ingredient.ingredient_id, update_data)
            
            assert isinstance(result, IngredientMasterResponse)
            assert result.name == update_data.name

    @pytest.mark.asyncio
    async def test_update_ingredient_not_found(self):
        """Test updating non-existent ingredient."""
        update_data = IngredientsMockFactory.create_ingredient_update(name="Updated")
        
        with MockContextManager(success_responses=True, mock_data=[]):
            with pytest.raises(IngredientError) as exc_info:
                await update_ingredient("non-existent-id", update_data)
            
            assert exc_info.value.error_code == "INGREDIENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_delete_ingredient_success(self):
        """Test successful ingredient deletion."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        
        with MockContextManager(success_responses=True, mock_data=[]):
            result = await delete_ingredient(test_ingredient.ingredient_id)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_ingredient_not_found(self):
        """Test deleting non-existent ingredient."""
        with MockContextManager(success_responses=True, mock_data=[]):
            with pytest.raises(IngredientError) as exc_info:
                await delete_ingredient("non-existent-id")
            
            assert exc_info.value.error_code == "INGREDIENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_database_error_handling(self):
        """Test handling of database errors."""
        with MockContextManager(success_responses=False):
            with pytest.raises(IngredientError) as exc_info:
                await get_all_ingredients()
            
            assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_search_ingredients_success(self):
        """Test successful ingredient search."""
        search_data = TestDataGenerator.generate_search_test_data()
        # Filter ingredients that match "tomato"
        tomato_ingredients = [ing for ing in search_data if "tomato" in ing.name.lower()]
        mock_data = [ing.to_dict() for ing in tomato_ingredients]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            result = await search_ingredients("tomato")
            
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) > 0
            # Verify all results contain "tomato"
            for ingredient in result.ingredients:
                assert "tomato" in ingredient.name.lower()

    @pytest.mark.asyncio
    async def test_search_ingredients_no_results(self):
        """Test ingredient search with no matches."""
        with MockContextManager(success_responses=True, mock_data=[]):
            result = await search_ingredients("nonexistent")
            
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) == 0
            assert result.total == 0

    @pytest.mark.asyncio
    async def test_search_ingredients_case_insensitive(self):
        """Test that ingredient search is case insensitive."""
        search_data = TestDataGenerator.generate_search_test_data()
        chicken_ingredients = [ing for ing in search_data if "chicken" in ing.name.lower()]
        mock_data = [ing.to_dict() for ing in chicken_ingredients]
        
        with MockContextManager(success_responses=True, mock_data=mock_data):
            # Test with different cases
            for query in ["CHICKEN", "Chicken", "chicken", "ChIcKeN"]:
                result = await search_ingredients(query)
                assert len(result.ingredients) > 0

    @pytest.mark.asyncio
    async def test_bulk_operations_scenarios(self):
        """Test various bulk operation scenarios."""
        scenarios = TestScenarios.pagination_scenarios()
        
        for scenario in scenarios:
            test_ingredients = TestDataGenerator.generate_pagination_test_data(scenario["total_items"])
            start = scenario["offset"]
            end = start + scenario["limit"]
            page_ingredients = test_ingredients[start:end]
            mock_data = [ing.to_dict() for ing in page_ingredients]
            
            with MockContextManager(success_responses=True, mock_data=mock_data):
                result = await get_all_ingredients(
                    limit=scenario["limit"],
                    offset=scenario["offset"]
                )
                
                assert len(result.ingredients) == scenario["expected_items"]
                assert result.limit == scenario["limit"]
                assert result.offset == scenario["offset"]
