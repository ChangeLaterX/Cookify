"""
Unit Tests for Ingredient Data Validation.

This module tests ingredient data validation and schema validation using Smart Mocks.
"""

from uuid import uuid4

import pytest
from domains.ingredients.schemas import (
    IngredientMasterCreate,
    IngredientMasterResponse,
    IngredientMasterUpdate,
)
from domains.ingredients.services import IngredientError
from pydantic import ValidationError
from tests.ingredients.config import IngredientsTestBase


class TestIngredientValidation(IngredientsTestBase):
    """Test ingredient data validation with Smart Mocks."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic validation."""
        # IngredientsTestBase automatically sets up Smart Mocks
        pass

    def test_valid_ingredient_create_schema(self):
        """Test valid ingredient creation schema."""
        valid_data = {
            "name": "Test Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "category": "vegetables",
        }

        ingredient = IngredientMasterCreate(**valid_data)

        assert ingredient.name == "Test Ingredient"
        assert ingredient.calories_per_100g == 100.0
        assert ingredient.proteins_per_100g == 10.0
        assert ingredient.fat_per_100g == 5.0
        assert ingredient.carbs_per_100g == 15.0
        assert ingredient.category == "vegetables"

    def test_ingredient_create_minimal_valid_data(self):
        """Test ingredient creation with minimal valid data."""
        minimal_data = {
            "name": "Simple Ingredient",
            "calories_per_100g": 50.0,
            "proteins_per_100g": 2.0,
            "fat_per_100g": 1.0,
            "carbs_per_100g": 10.0,
        }

        ingredient = IngredientMasterCreate(**minimal_data)

        assert ingredient.name == "Simple Ingredient"
        assert ingredient.category is None  # Optional field

    def test_ingredient_create_name_validation(self):
        """Test ingredient name validation."""
        # Empty name should fail
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                name="",
                calories_per_100g=100.0,
                proteins_per_100g=10.0,
                fat_per_100g=5.0,
                carbs_per_100g=15.0,
            )

        # Name too long should fail
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                name="A" * 300,
                calories_per_100g=100.0,
                proteins_per_100g=10.0,
                fat_per_100g=5.0,
                carbs_per_100g=15.0,
            )

    def test_ingredient_create_negative_values_validation(self):
        """Test that negative nutritional values are rejected."""
        base_data = {
            "name": "Test Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
        }

        # Test negative calories
        with pytest.raises(ValidationError):
            data = base_data.copy()
            data["calories_per_100g"] = -10.0
            IngredientMasterCreate(**data)

        # Test negative proteins
        with pytest.raises(ValidationError):
            data = base_data.copy()
            data["proteins_per_100g"] = -5.0
            IngredientMasterCreate(**data)

        # Test negative fat
        with pytest.raises(ValidationError):
            data = base_data.copy()
            data["fat_per_100g"] = -2.0
            IngredientMasterCreate(**data)

        # Test negative carbs
        with pytest.raises(ValidationError):
            data = base_data.copy()
            data["carbs_per_100g"] = -8.0
            IngredientMasterCreate(**data)

    def test_ingredient_create_zero_values_allowed(self):
        """Test that zero nutritional values are allowed."""
        valid_data = {
            "name": "Zero Ingredient",
            "calories_per_100g": 0.0,
            "proteins_per_100g": 0.0,
            "fat_per_100g": 0.0,
            "carbs_per_100g": 0.0,
        }

        ingredient = IngredientMasterCreate(**valid_data)

        assert ingredient.calories_per_100g == 0.0
        assert ingredient.proteins_per_100g == 0.0
        assert ingredient.fat_per_100g == 0.0
        assert ingredient.carbs_per_100g == 0.0

    def test_ingredient_update_schema(self):
        """Test ingredient update schema validation."""
        # Partial update - only name
        update_data = {"name": "Updated Name"}
        update = IngredientMasterUpdate(**update_data)
        assert update.name == "Updated Name"
        assert update.calories_per_100g is None

        # Partial update - only nutritional values
        update_data = {"calories_per_100g": 150.0, "proteins_per_100g": 20.0}
        update = IngredientMasterUpdate(**update_data)
        assert update.calories_per_100g == 150.0
        assert update.proteins_per_100g == 20.0
        assert update.name is None

    def test_ingredient_update_negative_values_validation(self):
        """Test that negative values are rejected in update schema."""
        with pytest.raises(ValidationError):
            IngredientMasterUpdate(calories_per_100g=-10.0)

        with pytest.raises(ValidationError):
            IngredientMasterUpdate(proteins_per_100g=-5.0)

        with pytest.raises(ValidationError):
            IngredientMasterUpdate(fat_per_100g=-2.0)

        with pytest.raises(ValidationError):
            IngredientMasterUpdate(carbs_per_100g=-8.0)

    def test_ingredient_update_empty_name_validation(self):
        """Test that empty name is rejected in update schema."""
        with pytest.raises(ValidationError):
            IngredientMasterUpdate(name="")

        with pytest.raises(ValidationError):
            IngredientMasterUpdate(name="   ")  # Whitespace only

    def test_ingredient_response_schema(self):
        """Test ingredient response schema."""
        response_data = {
            "ingredient_id": uuid4(),
            "name": "Response Ingredient",
            "calories_per_100g": 200.0,
            "proteins_per_100g": 25.0,
            "fat_per_100g": 10.0,
            "carbs_per_100g": 30.0,
            "category": "meat",
        }

        response = IngredientMasterResponse(**response_data)

        assert response.ingredient_id == response_data["ingredient_id"]
        assert response.name == "Response Ingredient"
        assert response.calories_per_100g == 200.0
        assert response.category == "meat"

    def test_ingredient_name_trimming(self):
        """Test that ingredient names are trimmed of whitespace."""
        data = {
            "name": "  Trimmed Ingredient  ",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
        }

        ingredient = IngredientMasterCreate(**data)
        assert ingredient.name == "Trimmed Ingredient"

    def test_ingredient_category_validation(self):
        """Test ingredient category field validation."""
        # Valid category
        data = {
            "name": "Categorized Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "category": "vegetables",
        }

        ingredient = IngredientMasterCreate(**data)
        assert ingredient.category == "vegetables"

        # None category should be allowed
        data["category"] = None
        ingredient = IngredientMasterCreate(**data)
        assert ingredient.category is None

    def test_large_nutritional_values(self):
        """Test handling of large but realistic nutritional values."""
        data = {
            "name": "High Energy Ingredient",
            "calories_per_100g": 900.0,  # Like oils
            "proteins_per_100g": 50.0,  # High protein
            "fat_per_100g": 90.0,  # High fat
            "carbs_per_100g": 80.0,  # High carbs
        }

        ingredient = IngredientMasterCreate(**data)

        assert ingredient.calories_per_100g == 900.0
        assert ingredient.proteins_per_100g == 50.0
        assert ingredient.fat_per_100g == 90.0
        assert ingredient.carbs_per_100g == 80.0

    def test_decimal_nutritional_values(self):
        """Test handling of decimal nutritional values."""
        data = {
            "name": "Precise Ingredient",
            "calories_per_100g": 123.45,
            "proteins_per_100g": 12.34,
            "fat_per_100g": 5.67,
            "carbs_per_100g": 15.89,
        }

        ingredient = IngredientMasterCreate(**data)

        assert ingredient.calories_per_100g == 123.45
        assert ingredient.proteins_per_100g == 12.34
        assert ingredient.fat_per_100g == 5.67
        assert ingredient.carbs_per_100g == 15.89

    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        # Missing name
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                calories_per_100g=100.0,
                proteins_per_100g=10.0,
                fat_per_100g=5.0,
                carbs_per_100g=15.0,
            )

        # Missing calories
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                name="Test",
                proteins_per_100g=10.0,
                fat_per_100g=5.0,
                carbs_per_100g=15.0,
            )

        # Missing proteins
        with pytest.raises(ValidationError):
            IngredientMasterCreate(
                name="Test",
                calories_per_100g=100.0,
                fat_per_100g=5.0,
                carbs_per_100g=15.0,
            )

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored in schemas."""
        data = {
            "name": "Test Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "extra_field": "should be ignored",
        }

        # Should not raise an error and extra field should be ignored
        ingredient = IngredientMasterCreate(**data)
        assert not hasattr(ingredient, "extra_field")
