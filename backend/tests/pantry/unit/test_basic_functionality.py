"""
Basic Unit Tests for Pantry Items Schemas and Data Validation.

This module tests the basic functionality of pantry schemas and validation.
"""

import pytest
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
from tests.pantry.config import PantryTestBase


class TestPantryBasicFunctionality(PantryTestBase):
    """Test basic pantry functionality."""

    def test_main_functionality(self):
        """Required by PantryTestBase - tests basic functionality."""
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

        # Empty name should fail
        with pytest.raises(ValidationError):
            PantryItemCreate(name="", **base_data)

        # Name too long (over 255 characters) should fail
        long_name = "a" * 256
        with pytest.raises(ValidationError):
            PantryItemCreate(name=long_name, **base_data)

    def test_invalid_quantity_validation(self):
        """Test validation of item quantities."""
        base_data = {
            "name": "Test Item",
            "unit": "pieces",
            "ingredient_id": str(uuid4())
        }

        # Zero quantity should fail
        with pytest.raises(ValidationError):
            PantryItemCreate(quantity=0.0, **base_data)

        # Negative quantity should fail
        with pytest.raises(ValidationError):
            PantryItemCreate(quantity=-1.0, **base_data)

    def test_bulk_create_validation(self):
        """Test validation of bulk create operations."""
        # Valid bulk create
        items = [
            PantryItemCreate(
                name=f"Item {i}",
                quantity=1.0,
                unit="pieces",
                ingredient_id=str(uuid4())
            )
            for i in range(3)
        ]
        bulk_create = PantryItemBulkCreate(items=items)
        assert len(bulk_create.items) == 3

        # Empty items list should fail
        with pytest.raises(ValidationError):
            PantryItemBulkCreate(items=[])

        # Too many items (over 50) should fail
        too_many_items = [
            PantryItemCreate(
                name=f"Item {i}",
                quantity=1.0,
                unit="pieces",
                ingredient_id=str(uuid4())
            )
            for i in range(51)
        ]
        with pytest.raises(ValidationError):
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

        # Empty updates dict should fail
        with pytest.raises(ValidationError):
            PantryItemBulkUpdate(updates={})

        # Too many updates (over 50) should fail
        too_many_updates = {
            uuid4(): PantryItemUpdate(name=f"Item {i}")
            for i in range(51)
        }
        with pytest.raises(ValidationError):
            PantryItemBulkUpdate(updates=too_many_updates)

    def test_bulk_delete_validation(self):
        """Test validation of bulk delete operations."""
        # Valid bulk delete
        item_ids = [uuid4(), uuid4(), uuid4()]
        bulk_delete = PantryItemBulkDelete(item_ids=item_ids)
        assert len(bulk_delete.item_ids) == 3

        # Empty items list should fail
        with pytest.raises(ValidationError):
            PantryItemBulkDelete(item_ids=[])

        # Too many items (over 50) should fail
        too_many_ids = [uuid4() for _ in range(51)]
        with pytest.raises(ValidationError):
            PantryItemBulkDelete(item_ids=too_many_ids)

    def test_pantry_item_update_optional_fields(self):
        """Test that update fields are optional."""
        # All fields optional in update
        update = PantryItemUpdate()
        assert update.name is None
        assert update.quantity is None
        assert update.unit is None
        assert update.category is None
        assert update.expiry_date is None
        assert update.ingredient_id is None

        # Valid partial update
        update = PantryItemUpdate(name="Updated Name", quantity=5.0)
        assert update.name == "Updated Name"
        assert update.quantity == 5.0
        assert update.unit is None  # Still optional

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

    def test_whitespace_trimming(self):
        """Test that whitespace is properly handled."""
        item = PantryItemCreate(
            name="  Bananas  ",
            unit="  pieces  ",
            quantity=1.0,
            ingredient_id=str(uuid4())
        )
        # Names and units should be trimmed
        assert item.name == "Bananas"
        assert item.unit == "pieces"

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
