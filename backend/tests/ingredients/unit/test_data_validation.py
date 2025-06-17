"""
Unit Tests for Ingredient Data Validation.

This module tests ingredient data validation and schema validation.
"""

import pytest
from pydantic import ValidationError
from uuid import uuid4

from domains.ingredients.schemas import (
    IngredientMasterCreate,
    IngredientMasterUpdate,
    IngredientMasterResponse
)
from domains.ingredients.services import IngredientError
from tests.ingredients.config import IngredientsTestBase
from tests.ingredients.utils.mocks import IngredientsMockFactory
from tests.ingredients.utils.test_data import TestDataGenerator, TestScenarios


class TestIngredientValidation(IngredientsTestBase):
    """Test ingredient data validation."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic validation."""
        self.test_valid_ingredient_create_schema()

    def test_valid_ingredient_create_schema(self):
        """Test valid ingredient creation schema."""
        valid_data = {
            "name": "Test Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "price_per_100g_cents": 500
        }
        
        ingredient = IngredientMasterCreate(**valid_data)
        
        assert ingredient.name == "Test Ingredient"
        assert ingredient.calories_per_100g == 100.0
        assert ingredient.proteins_per_100g == 10.0
        assert ingredient.fat_per_100g == 5.0
        assert ingredient.carbs_per_100g == 15.0
        assert ingredient.price_per_100g_cents == 500

    def test_ingredient_create_name_validation(self):
        """Test ingredient name validation."""
        base_data = {
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "price_per_100g_cents": 500
        }
        
        # Test empty name
        with pytest.raises(ValidationError):
            IngredientMasterCreate(name="", **base_data)
        
        # Test name with only whitespace
        with pytest.raises(ValidationError):
            IngredientMasterCreate(name="   ", **base_data)
        
        # Test name that's too long
        long_name = "A" * 300
        with pytest.raises(ValidationError):
            IngredientMasterCreate(name=long_name, **base_data)
        
        # Test valid name with whitespace (should be trimmed)
        ingredient = IngredientMasterCreate(name="  Valid Name  ", **base_data)
        assert ingredient.name == "Valid Name"

    def test_ingredient_create_nutrition_validation(self):
        """Test nutritional value validation."""
        base_data = {
            "name": "Test Ingredient",
            "price_per_100g_cents": 500
        }
        
        # Test negative values
        negative_fields = [
            "calories_per_100g",
            "proteins_per_100g", 
            "fat_per_100g",
            "carbs_per_100g"
        ]
        
        for field in negative_fields:
            invalid_data = {
                **base_data,
                "calories_per_100g": 100.0,
                "proteins_per_100g": 10.0,
                "fat_per_100g": 5.0,
                "carbs_per_100g": 15.0,
                field: -1.0  # Invalid negative value
            }
            
            with pytest.raises(ValidationError):
                IngredientMasterCreate(**invalid_data)
        
        # Test zero values (should be valid)
        zero_data = {
            **base_data,
            "calories_per_100g": 0.0,
            "proteins_per_100g": 0.0,
            "fat_per_100g": 0.0,
            "carbs_per_100g": 0.0
        }
        
        ingredient = IngredientMasterCreate(**zero_data)
        assert ingredient.calories_per_100g == 0.0

    def test_ingredient_create_price_validation(self):
        """Test price validation."""
        base_data = {
            "name": "Test Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0
        }
        
        # Test negative price
        with pytest.raises(ValidationError):
            IngredientMasterCreate(price_per_100g_cents=-100, **base_data)
        
        # Test zero price (should be valid)
        ingredient = IngredientMasterCreate(price_per_100g_cents=0, **base_data)
        assert ingredient.price_per_100g_cents == 0
        
        # Test large price (should be valid)
        ingredient = IngredientMasterCreate(price_per_100g_cents=999999, **base_data)
        assert ingredient.price_per_100g_cents == 999999

    def test_ingredient_update_schema_validation(self):
        """Test ingredient update schema validation."""
        # Test partial update (all fields optional)
        update_data = IngredientMasterUpdate(name="Updated Name")
        assert update_data.name == "Updated Name"
        assert update_data.calories_per_100g is None
        
        # Test full update
        full_update = IngredientMasterUpdate(
            name="Updated Ingredient",
            calories_per_100g=150.0,
            proteins_per_100g=12.0,
            fat_per_100g=7.0,
            carbs_per_100g=18.0,
            price_per_100g_cents=600
        )
        
        assert full_update.name == "Updated Ingredient"
        assert full_update.calories_per_100g == 150.0
        
        # Test empty update (all fields None)
        empty_update = IngredientMasterUpdate()
        assert empty_update.name is None
        assert empty_update.calories_per_100g is None

    def test_ingredient_update_validation_rules(self):
        """Test validation rules for ingredient updates."""
        # Test invalid name in update
        with pytest.raises(ValidationError):
            IngredientMasterUpdate(name="")
        
        # Test negative values in update
        with pytest.raises(ValidationError):
            IngredientMasterUpdate(calories_per_100g=-10.0)
        
        with pytest.raises(ValidationError):
            IngredientMasterUpdate(price_per_100g_cents=-50)

    def test_ingredient_response_schema(self):
        """Test ingredient response schema."""
        response_data = {
            "ingredient_id": str(uuid4()),
            "name": "Response Ingredient",
            "calories_per_100g": 120.0,
            "proteins_per_100g": 11.0,
            "fat_per_100g": 6.0,
            "carbs_per_100g": 16.0,
            "price_per_100g_cents": 550,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        response = IngredientMasterResponse(**response_data)
        
        assert response.ingredient_id == response_data["ingredient_id"]
        assert response.name == response_data["name"]
        assert response.calories_per_100g == response_data["calories_per_100g"]

    def test_realistic_nutrition_values(self):
        """Test with realistic nutritional values for different ingredient types."""
        # Test vegetable (low calories, minimal fat)
        vegetable = IngredientMasterCreate(
            name="Tomato",
            calories_per_100g=18.0,
            proteins_per_100g=0.9,
            fat_per_100g=0.2,
            carbs_per_100g=3.9,
            price_per_100g_cents=200
        )
        assert vegetable.name == "Tomato"
        
        # Test meat (high protein, higher calories)
        meat = IngredientMasterCreate(
            name="Chicken Breast",
            calories_per_100g=165.0,
            proteins_per_100g=31.0,
            fat_per_100g=3.6,
            carbs_per_100g=0.0,
            price_per_100g_cents=1200
        )
        assert meat.proteins_per_100g == 31.0
        
        # Test oil (very high fat and calories)
        oil = IngredientMasterCreate(
            name="Olive Oil",
            calories_per_100g=884.0,
            proteins_per_100g=0.0,
            fat_per_100g=100.0,
            carbs_per_100g=0.0,
            price_per_100g_cents=800
        )
        assert oil.fat_per_100g == 100.0

    def test_edge_case_values(self):
        """Test edge case nutritional values."""
        # Test very small decimal values
        ingredient = IngredientMasterCreate(
            name="Low Nutrition",
            calories_per_100g=0.1,
            proteins_per_100g=0.01,
            fat_per_100g=0.001,
            carbs_per_100g=0.1,
            price_per_100g_cents=1
        )
        assert ingredient.calories_per_100g == 0.1
        
        # Test very large values
        high_nutrition = IngredientMasterCreate(
            name="High Nutrition",
            calories_per_100g=999.9,
            proteins_per_100g=99.9,
            fat_per_100g=99.9,
            carbs_per_100g=99.9,
            price_per_100g_cents=50000
        )
        assert high_nutrition.calories_per_100g == 999.9

    def test_validation_scenarios_from_test_data(self):
        """Test validation scenarios using predefined test scenarios."""
        scenarios = TestScenarios.validation_scenarios()
        
        for scenario in scenarios:
            with pytest.raises(ValidationError):
                IngredientMasterCreate(**scenario["data"])

    def test_field_type_validation(self):
        """Test that fields accept correct types."""
        # Test negative values (should fail validation)
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                name="Test",
                calories_per_100g=-10.0,  # Should be >= 0
                proteins_per_100g=10.0,
                fat_per_100g=5.0,
                carbs_per_100g=15.0,
                price_per_100g_cents=500
            )
        
        # Test negative price
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                name="Test",
                calories_per_100g=100.0,
                proteins_per_100g=10.0,
                fat_per_100g=5.0,
                carbs_per_100g=15.0,
                price_per_100g_cents=-100  # Should be >= 0
            )

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        # Test missing name
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                calories_per_100g=100.0,
                proteins_per_100g=10.0,
                fat_per_100g=5.0,
                carbs_per_100g=15.0,
                price_per_100g_cents=500
            )
        
        # Test missing nutritional values
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                name="Test Ingredient",
                # Missing all nutritional fields
            )
