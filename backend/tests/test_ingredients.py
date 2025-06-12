"""
Pytest-based tests for ingredients domain - Functional approach
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

# Test the service layer functions directly
from domains.ingredients.services import (
    get_all_ingredients,
    get_ingredient_by_id,
    create_ingredient,
    update_ingredient,
    delete_ingredient,
    search_ingredients,
    IngredientError,
)
from domains.ingredients.schemas import (
    IngredientMasterCreate,
    IngredientMasterUpdate,
    IngredientMasterResponse,
    IngredientListResponse,
)


class TestIngredientServicesUnit:
    """Unit tests for ingredient service functions."""

    @pytest.mark.asyncio
    async def test_get_all_ingredients_success(self):
        """Test successful retrieval of ingredients."""
        mock_supabase_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            {
                "ingredient_id": str(uuid4()),
                "name": "Test Ingredient",
                "calories_per_100g": 100.0,
                "proteins_per_100g": 10.0,
                "fat_per_100g": 5.0,
                "carbs_per_100g": 15.0,
                "price_per_100g_cents": 500
            }
        ]
        
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response
        mock_supabase_client.table.return_value.select.return_value.range.return_value.order.return_value.execute.return_value = mock_response
        
        with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
            result = await get_all_ingredients(limit=10, offset=0)
            
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) == 1
            assert result.total == 1
            assert result.limit == 10
            assert result.offset == 0

    @pytest.mark.asyncio
    async def test_get_ingredient_by_id_success(self):
        """Test successful retrieval of ingredient by ID."""
        ingredient_id = uuid4()
        mock_supabase_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            {
                "ingredient_id": str(ingredient_id),
                "name": "Test Ingredient",
                "calories_per_100g": 100.0,
                "proteins_per_100g": 10.0,
                "fat_per_100g": 5.0,
                "carbs_per_100g": 15.0,
                "price_per_100g_cents": 500
            }
        ]
        
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
            result = await get_ingredient_by_id(ingredient_id)
            
            assert isinstance(result, IngredientMasterResponse)
            assert str(result.ingredient_id) == str(ingredient_id)
            assert result.name == "Test Ingredient"

    @pytest.mark.asyncio
    async def test_get_ingredient_by_id_not_found(self):
        """Test handling when ingredient is not found."""
        ingredient_id = uuid4()
        mock_supabase_client = Mock()
        mock_response = Mock()
        mock_response.data = []
        
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
            with pytest.raises(IngredientError) as exc_info:
                await get_ingredient_by_id(ingredient_id)
            
            assert exc_info.value.error_code == "INGREDIENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_create_ingredient_success(self):
        """Test successful ingredient creation."""
        create_data = IngredientMasterCreate(
            name="Test Ingredient",
            calories_per_100g=100.0,
            proteins_per_100g=10.0,
            fat_per_100g=5.0,
            carbs_per_100g=15.0,
            price_per_100g_cents=500
        )
        
        mock_supabase_client = Mock()
        
        # Mock check for existing ingredient (none found)
        mock_existing_response = Mock()
        mock_existing_response.data = []
        
        # Mock successful creation
        mock_create_response = Mock()
        mock_create_response.data = [
            {
                "ingredient_id": str(uuid4()),
                "name": "Test Ingredient",
                "calories_per_100g": 100.0,
                "proteins_per_100g": 10.0,
                "fat_per_100g": 5.0,
                "carbs_per_100g": 15.0,
                "price_per_100g_cents": 500
            }
        ]
        
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_existing_response
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_create_response
        
        with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
            result = await create_ingredient(create_data)
            
            assert isinstance(result, IngredientMasterResponse)
            assert result.name == "Test Ingredient"

    @pytest.mark.asyncio
    async def test_create_ingredient_name_exists(self):
        """Test handling when ingredient name already exists."""
        create_data = IngredientMasterCreate(
            name="Existing Ingredient",
            calories_per_100g=100.0,
            proteins_per_100g=10.0,
            fat_per_100g=5.0,
            carbs_per_100g=15.0,
            price_per_100g_cents=500
        )
        
        mock_supabase_client = Mock()
        
        # Mock existing ingredient found
        mock_existing_response = Mock()
        mock_existing_response.data = [{"name": "Existing Ingredient"}]
        
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_existing_response
        
        with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
            with pytest.raises(IngredientError) as exc_info:
                await create_ingredient(create_data)
            
            assert exc_info.value.error_code == "INGREDIENT_NAME_EXISTS"

    @pytest.mark.asyncio
    async def test_search_ingredients_success(self):
        """Test successful ingredient search."""
        search_query = "chicken"
        
        mock_supabase_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            {
                "ingredient_id": str(uuid4()),
                "name": "Chicken Breast",
                "calories_per_100g": 165.0,
                "proteins_per_100g": 31.0,
                "fat_per_100g": 3.6,
                "carbs_per_100g": 0.0,
                "price_per_100g_cents": 899
            }
        ]
        
        mock_supabase_client.table.return_value.select.return_value.ilike.return_value.execute.return_value = mock_response
        mock_supabase_client.table.return_value.select.return_value.ilike.return_value.range.return_value.order.return_value.execute.return_value = mock_response
        
        with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
            result = await search_ingredients(query=search_query, limit=10, offset=0)
            
            assert isinstance(result, IngredientListResponse)
            assert len(result.ingredients) == 1
            assert "chicken" in result.ingredients[0].name.lower()


class TestIngredientSchemas:
    """Test cases for ingredient schema validation."""

    def test_ingredient_master_create_valid(self):
        """Test valid ingredient creation schema."""
        data = {
            "name": "Test Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "price_per_100g_cents": 500
        }
        
        schema = IngredientMasterCreate(**data)
        assert schema.name == "Test Ingredient"
        assert schema.calories_per_100g == 100.0

    def test_ingredient_master_create_invalid_negative_values(self):
        """Test ingredient creation schema with negative values."""
        data = {
            "name": "Test Ingredient",
            "calories_per_100g": -10,  # Invalid
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "price_per_100g_cents": 500
        }
        
        with pytest.raises(ValueError):
            IngredientMasterCreate(**data)

    def test_ingredient_master_create_empty_name(self):
        """Test ingredient creation schema with empty name."""
        data = {
            "name": "   ",  # Empty after strip
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "price_per_100g_cents": 500
        }
        
        with pytest.raises(ValueError, match="Ingredient name cannot be empty"):
            IngredientMasterCreate(**data)

    def test_ingredient_master_update_partial(self):
        """Test ingredient update schema with partial data."""
        data = {
            "name": "Updated Name",
            "calories_per_100g": 200.0
            # Other fields omitted
        }
        
        schema = IngredientMasterUpdate(**data)
        assert schema.name == "Updated Name"
        assert schema.calories_per_100g == 200.0
        assert schema.proteins_per_100g is None

    def test_ingredient_master_response_conversion(self):
        """Test ingredient response schema conversion."""
        data = {
            "ingredient_id": uuid4(),
            "name": "Test Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "price_per_100g_cents": 500
        }
        
        schema = IngredientMasterResponse(**data)
        assert schema.ingredient_id == data["ingredient_id"]
        assert schema.name == "Test Ingredient"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
