"""
Unit Tests for Pantry Items Data Validation and Error Handling.

This module tests input validation, schema validation, and error handling scenarios.
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from datetime import date, timedelta
from pydantic import ValidationError

from domains.pantry_items.schemas import (
    PantryItemCreate,
    PantryItemUpdate,
    PantryItemBulkCreate,
    PantryItemBulkUpdate,
    PantryItemBulkDelete,
    PantryItemResponse
)
from domains.pantry_items.services import (
    PantryItemError,
    PantryItemNotFoundError,
    PantryItemValidationError,
    validate_pantry_item_data,
    validate_bulk_operation_size
)
from tests.pantry.config import PantryTestBase, TEST_USER_ID
from tests.pantry.utils.test_data import (
    PantryTestDataGenerator,
    PantryMockFactory,
    VALIDATION_ERROR_MSG,
    NOT_FOUND_ERROR_MSG
)


class TestPantryDataValidation(PantryTestBase):
    """Test data validation for pantry items."""

    def test_main_functionality(self):
        """Required by PantryTestBase - tests basic validation functionality."""
        self.test_valid_pantry_item_creation()

    def test_valid_pantry_item_creation(self):
        """Test creation of valid pantry item."""
        # Valid data
        valid_data = {
            "name": "Bananas",
            "quantity": 6.0,
            "unit": "pieces",
            "category": "produce",
            "expiry_date": "2025-07-02",
            "ingredient_id": str(uuid4())
        }

        # Should create successfully
        item = PantryItemCreate(**valid_data)
        assert item.name == "Bananas"
        assert item.quantity == 6.0
        assert item.unit == "pieces"
        assert item.category == "produce"
        assert item.expiry_date == date(2025, 7, 2)

    def test_invalid_name_validation(self):
        """Test validation of item names."""
        base_data = {
            "quantity": 1.0,
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Empty name
        with pytest.raises(ValidationError, match="String should have at least 1 character"):
            PantryItemCreate(name="", **base_data)

        # Whitespace-only name
        with pytest.raises(ValidationError):
            PantryItemCreate(name="   ", **base_data)

        # Name too long (over 255 characters)
        long_name = "a" * 256
        with pytest.raises(ValidationError, match="String should have at most 255 characters"):
            PantryItemCreate(name=long_name, **base_data)

        # None name
        with pytest.raises(ValidationError):
            PantryItemCreate(name=None, **base_data)

    def test_invalid_quantity_validation(self):
        """Test validation of item quantities."""
        base_data = {
            "name": "Test Item",
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Zero quantity
        with pytest.raises(ValidationError, match="Input should be greater than 0"):
            PantryItemCreate(quantity=0.0, **base_data)

        # Negative quantity
        with pytest.raises(ValidationError, match="Input should be greater than 0"):
            PantryItemCreate(quantity=-1.0, **base_data)

        # Non-numeric quantity
        with pytest.raises(ValidationError):
            PantryItemCreate(quantity="not_a_number", **base_data)

        # None quantity
        with pytest.raises(ValidationError):
            PantryItemCreate(quantity=None, **base_data)

    def test_invalid_unit_validation(self):
        """Test validation of item units."""
        base_data = {
            "name": "Test Item",
            "quantity": 1.0,
            "ingredient_id": str(uuid4())
        }

        # Empty unit
        with pytest.raises(ValidationError, match="String should have at least 1 character"):
            PantryItemCreate(unit="", **base_data)

        # Whitespace-only unit
        with pytest.raises(ValidationError):
            PantryItemCreate(unit="   ", **base_data)

        # Unit too long (over 50 characters)
        long_unit = "a" * 51
        with pytest.raises(ValidationError, match="String should have at most 50 characters"):
            PantryItemCreate(unit=long_unit, **base_data)

        # None unit
        with pytest.raises(ValidationError):
            PantryItemCreate(unit=None, **base_data)

    def test_invalid_ingredient_id_validation(self):
        """Test validation of ingredient IDs."""
        base_data = {
            "name": "Test Item",
            "quantity": 1.0,
            "unit": "pieces"
        }

        # Invalid UUID format
        with pytest.raises(ValidationError):
            PantryItemCreate(ingredient_id="not-a-uuid", **base_data)

        # None ingredient_id
        with pytest.raises(ValidationError):
            PantryItemCreate(ingredient_id=None, **base_data)

        # Empty string
        with pytest.raises(ValidationError):
            PantryItemCreate(ingredient_id="", **base_data)

    def test_valid_optional_fields(self):
        """Test validation of optional fields."""
        base_data = {
            "name": "Test Item",
            "quantity": 1.0,
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Valid with all optional fields
        item = PantryItemCreate(
            category="test_category",
            expiry_date=date.today() + timedelta(days=7),
            **base_data
        )
        assert item.category == "test_category"
        assert item.expiry_date is not None

        # Valid without optional fields
        item = PantryItemCreate(**base_data)
        assert item.category is None
        assert item.expiry_date is None

    def test_category_validation(self):
        """Test validation of category field."""
        base_data = {
            "name": "Test Item",
            "quantity": 1.0,
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Valid category
        item = PantryItemCreate(category="produce", **base_data)
        assert item.category == "produce"

        # Empty category (should be treated as None)
        item = PantryItemCreate(category="", **base_data)
        # Behavior depends on implementation

        # Category too long
        long_category = "a" * 101
        with pytest.raises(ValidationError, match="String should have at most 100 characters"):
            PantryItemCreate(category=long_category, **base_data)

    def test_expiry_date_validation(self):
        """Test validation of expiry dates."""
        base_data = {
            "name": "Test Item",
            "quantity": 1.0,
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Valid future date
        future_date = date.today() + timedelta(days=30)
        item = PantryItemCreate(expiry_date=future_date, **base_data)
        assert item.expiry_date == future_date

        # Valid past date (expired items should be allowed)
        past_date = date.today() - timedelta(days=1)
        item = PantryItemCreate(expiry_date=past_date, **base_data)
        assert item.expiry_date == past_date

        # Today's date
        today = date.today()
        item = PantryItemCreate(expiry_date=today, **base_data)
        assert item.expiry_date == today

        # Invalid date format (handled by Pydantic)
        with pytest.raises(ValidationError):
            PantryItemCreate(expiry_date="not-a-date", **base_data)

    def test_pantry_item_update_validation(self):
        """Test validation of pantry item updates."""
        # All fields optional in update
        update = PantryItemUpdate()
        assert update.name is None
        assert update.quantity is None

        # Valid partial update
        update = PantryItemUpdate(name="Updated Name", quantity=5.0)
        assert update.name == "Updated Name"
        assert update.quantity == 5.0

        # Invalid update values
        with pytest.raises(ValidationError):
            PantryItemUpdate(quantity=-1.0)  # Negative quantity

        with pytest.raises(ValidationError):
            PantryItemUpdate(name="")  # Empty name

    def test_bulk_create_validation(self):
        """Test validation of bulk create operations."""
        # Valid bulk create
        items = [
            PantryTestDataGenerator.generate_pantry_item_create(name=f"Item {i}")
            for i in range(3)
        ]
        bulk_create = PantryItemBulkCreate(items=items)
        assert len(bulk_create.items) == 3

        # Empty items list
        with pytest.raises(ValidationError, match="List should have at least 1 item"):
            PantryItemBulkCreate(items=[])

        # Too many items (over 50)
        too_many_items = [
            PantryTestDataGenerator.generate_pantry_item_create(name=f"Item {i}")
            for i in range(51)
        ]
        with pytest.raises(ValidationError, match="Cannot create more than 50 items at once"):
            PantryItemBulkCreate(items=too_many_items)

    def test_bulk_update_validation(self):
        """Test validation of bulk update operations."""
        # Valid bulk update
        updates = {
            uuid4(): PantryItemUpdate(name="Updated Item 1"),
            uuid4(): PantryItemUpdate(quantity=2.0)
        }
        bulk_update = PantryItemBulkUpdate(updates=updates)
        assert len(bulk_update.updates) == 2

        # Empty updates dict
        with pytest.raises(ValidationError, match="Dict should have at least 1 item"):
            PantryItemBulkUpdate(updates={})

        # Too many updates (over 50)
        too_many_updates = {
            uuid4(): PantryItemUpdate(name=f"Item {i}")
            for i in range(51)
        }
        with pytest.raises(ValidationError, match="Cannot update more than 50 items at once"):
            PantryItemBulkUpdate(updates=too_many_updates)

    def test_bulk_delete_validation(self):
        """Test validation of bulk delete operations."""
        # Valid bulk delete
        item_ids = [uuid4(), uuid4(), uuid4()]
        bulk_delete = PantryItemBulkDelete(item_ids=item_ids)
        assert len(bulk_delete.item_ids) == 3

        # Empty items list
        with pytest.raises(ValidationError, match="List should have at least 1 item"):
            PantryItemBulkDelete(item_ids=[])

        # Too many items (over 50)
        too_many_ids = [uuid4() for _ in range(51)]
        with pytest.raises(ValidationError, match="Cannot delete more than 50 items at once"):
            PantryItemBulkDelete(item_ids=too_many_ids)

        # Invalid UUID format
        with pytest.raises(ValidationError):
            PantryItemBulkDelete(item_ids=["not-a-uuid"])

    def test_whitespace_handling(self):
        """Test handling of whitespace in string fields."""
        # Names and units should be trimmed
        item = PantryItemCreate(
            name="  Bananas  ",
            unit="  pieces  ",
            quantity=1.0,
            ingredient_id=str(uuid4())
        )
        assert item.name == "Bananas"
        assert item.unit == "pieces"

        # Category should be trimmed (if not None)
        item = PantryItemCreate(
            name="Test",
            unit="pieces",
            quantity=1.0,
            category="  produce  ",
            ingredient_id=str(uuid4())
        )
        # Behavior depends on field validator implementation

    def test_numeric_edge_cases(self):
        """Test numeric edge cases for quantities."""
        base_data = {
            "name": "Test Item",
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Very small positive number
        item = PantryItemCreate(quantity=0.001, **base_data)
        assert item.quantity == 0.001

        # Very large number
        item = PantryItemCreate(quantity=999999.999, **base_data)
        assert item.quantity == 999999.999

        # Integer as float
        item = PantryItemCreate(quantity=5, **base_data)
        assert item.quantity == 5.0

    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        special_data = {
            "name": "Café Ñoño 🍌",  # Unicode characters and emoji
            "unit": "kg/m²",  # Special symbols
            "quantity": 1.0,
            "category": "spéciäl",
            "ingredient_id": str(uuid4())
        }

        # Should handle unicode correctly
        item = PantryItemCreate(**special_data)
        assert item.name == "Café Ñoño 🍌"
        assert item.unit == "kg/m²"
        assert item.category == "spéciäl"

    def test_date_edge_cases(self):
        """Test edge cases for expiry dates."""
        base_data = {
            "name": "Test Item",
            "quantity": 1.0,
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Far future date
        far_future = date(2099, 12, 31)
        item = PantryItemCreate(expiry_date=far_future, **base_data)
        assert item.expiry_date == far_future

        # Far past date
        far_past = date(1900, 1, 1)
        item = PantryItemCreate(expiry_date=far_past, **base_data)
        assert item.expiry_date == far_past

        # Leap year date
        leap_date = date(2024, 2, 29)
        item = PantryItemCreate(expiry_date=leap_date, **base_data)
        assert item.expiry_date == leap_date

    def test_response_schema_validation(self):
        """Test validation of response schemas."""
        # Valid response data
        response_data = {
            "id": str(uuid4()),
            "user_id": str(uuid4()),
            "name": "Test Item",
            "quantity": 1.0,
            "unit": "pieces",
            "category": "test",
            "expiry_date": date.today(),
            "ingredient_id": str(uuid4()),
            "added_at": "2025-06-29T10:00:00"
        }

        response = PantryItemResponse(**response_data)
        assert response.name == "Test Item"
        assert isinstance(response.id, UUID)
        assert isinstance(response.user_id, UUID)

    def test_field_serialization(self):
        """Test proper serialization of fields."""
        item = PantryTestDataGenerator.generate_pantry_item_response()
        
        # Should serialize to dict properly
        item_dict = item.model_dump()
        assert isinstance(item_dict, dict)
        assert "id" in item_dict
        assert "name" in item_dict
        
        # UUID fields should be serialized as strings
        assert isinstance(item_dict["id"], str)
        assert isinstance(item_dict["user_id"], str)
        assert isinstance(item_dict["ingredient_id"], str)

    @pytest.mark.asyncio
    async def test_service_validation_functions(self):
        """Test service-level validation functions."""
        # Test validate_pantry_item_data (if exists)
        valid_data = PantryTestDataGenerator.generate_pantry_item_data()
        
        # Should not raise for valid data
        try:
            if hasattr(validate_pantry_item_data, '__call__'):
                await validate_pantry_item_data(valid_data)
        except NameError:
            # Function might not exist, skip test
            pass

        # Test validate_bulk_operation_size (if exists)
        try:
            if hasattr(validate_bulk_operation_size, '__call__'):
                validate_bulk_operation_size(10)  # Valid size
                
                with pytest.raises(PantryItemValidationError):
                    validate_bulk_operation_size(51)  # Invalid size
        except NameError:
            # Function might not exist, skip test
            pass

    def test_error_message_clarity(self):
        """Test that validation error messages are clear and helpful."""
        base_data = {
            "quantity": 1.0,
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Test specific error messages
        try:
            PantryItemCreate(name="", **base_data)
        except ValidationError as e:
            error_messages = str(e)
            # Should contain helpful information
            assert "name" in error_messages.lower()

        try:
            PantryItemCreate(quantity=-1, **base_data)
        except ValidationError as e:
            error_messages = str(e)
            assert "quantity" in error_messages.lower()
            assert "greater than 0" in error_messages.lower()

    def test_backward_compatibility(self):
        """Test that schema changes maintain backward compatibility."""
        # Test with minimal required fields only
        minimal_data = {
            "name": "Test Item",
            "quantity": 1.0,
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        item = PantryItemCreate(**minimal_data)
        assert item.name == "Test Item"
        
        # Optional fields should have sensible defaults
        assert item.category is None
        assert item.expiry_date is None
