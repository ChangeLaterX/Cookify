"""
Pantry Test Utilities and Helper Functions.

This module provides utility functions and helpers for pantry testing.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4, UUID
from unittest.mock import Mock

from domains.pantry_items.schemas import (
    PantryItemCreate,
    PantryItemResponse,
    PantryItemBulkCreate,
    PantryItemBulkUpdate,
    PantryItemBulkDelete,
    PantryStatsOverview,
    PantryCategoryStats,
    CategoryStats,
    PantryExpiryReport,
    ExpiryItem,
    PantryLowStockReport,
    LowStockItem
)


class PantryTestDataGenerator:
    """Generator for test data for pantry items."""

    @staticmethod
    def generate_pantry_item_data(
        name: str = "Test Item",
        quantity: float = 1.0,
        unit: str = "pieces",
        category: Optional[str] = "test",
        expiry_date: Optional[date] = None,
        ingredient_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Generate pantry item data dictionary."""
        return {
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "category": category,
            "expiry_date": expiry_date or (date.today() + timedelta(days=7)),
            "ingredient_id": ingredient_id or uuid4()
        }

    @staticmethod
    def generate_pantry_item_create(
        name: str = "Test Item",
        quantity: float = 1.0,
        unit: str = "pieces",
        category: Optional[str] = "test",
        expiry_date: Optional[date] = None,
        ingredient_id: Optional[UUID] = None
    ) -> PantryItemCreate:
        """Generate a PantryItemCreate instance."""
        data = PantryTestDataGenerator.generate_pantry_item_data(
            name=name,
            quantity=quantity,
            unit=unit,
            category=category,
            expiry_date=expiry_date,
            ingredient_id=ingredient_id
        )
        return PantryItemCreate(**data)

    @staticmethod
    def generate_pantry_item_response(
        id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        name: str = "Test Item",
        quantity: float = 1.0,
        unit: str = "pieces",
        category: Optional[str] = "test",
        expiry_date: Optional[date] = None,
        ingredient_id: Optional[UUID] = None,
        added_at: Optional[datetime] = None
    ) -> PantryItemResponse:
        """Generate a PantryItemResponse instance."""
        return PantryItemResponse(
            id=id or uuid4(),
            user_id=user_id or uuid4(),
            name=name,
            quantity=quantity,
            unit=unit,
            category=category,
            expiry_date=expiry_date or (date.today() + timedelta(days=7)),
            ingredient_id=ingredient_id or uuid4(),
            added_at=added_at or datetime.now()
        )

    @staticmethod
    def generate_bulk_create_data(count: int = 3) -> PantryItemBulkCreate:
        """Generate bulk create data with specified number of items."""
        items = []
        for i in range(count):
            items.append(PantryTestDataGenerator.generate_pantry_item_create(
                name=f"Test Item {i+1}",
                quantity=float(i+1),
                category=f"category_{i%3}" if i % 3 != 0 else None
            ))
        return PantryItemBulkCreate(items=items)

    @staticmethod
    def generate_bulk_update_data(item_ids: List[UUID]) -> PantryItemBulkUpdate:
        """Generate bulk update data for specified item IDs."""
        from domains.pantry_items.schemas import PantryItemUpdate
        
        updates = {}
        for i, item_id in enumerate(item_ids):
            updates[item_id] = PantryItemUpdate(
                quantity=float(i+10),
                name=f"Updated Item {i+1}"
            )
        return PantryItemBulkUpdate(updates=updates)

    @staticmethod
    def generate_bulk_delete_data(item_ids: List[UUID]) -> PantryItemBulkDelete:
        """Generate bulk delete data for specified item IDs."""
        return PantryItemBulkDelete(item_ids=item_ids)

    @staticmethod
    def generate_stats_overview(
        total_items: int = 25,
        total_categories: int = 6,
        items_expiring_soon: int = 3,
        expired_items: int = 1,
        low_stock_items: int = 5,
        estimated_total_value: float = 0.0,
        most_common_category: Optional[str] = "produce"
    ) -> PantryStatsOverview:
        """Generate pantry statistics overview."""
        return PantryStatsOverview(
            total_items=total_items,
            total_categories=total_categories,
            items_expiring_soon=items_expiring_soon,
            expired_items=expired_items,
            low_stock_items=low_stock_items,
            estimated_total_value=estimated_total_value,
            most_common_category=most_common_category
        )

    @staticmethod
    def generate_category_stats() -> PantryCategoryStats:
        """Generate category statistics."""
        categories = [
            CategoryStats(category="produce", item_count=8, percentage=32.0),
            CategoryStats(category="dairy", item_count=5, percentage=20.0),
            CategoryStats(category="bakery", item_count=3, percentage=12.0),
            CategoryStats(category="spices", item_count=2, percentage=8.0)
        ]
        return PantryCategoryStats(categories=categories, uncategorized_count=2)

    @staticmethod
    def generate_expiry_report() -> PantryExpiryReport:
        """Generate expiry report with sample data."""
        today = date.today()
        
        expiring_soon = [
            ExpiryItem(
                id=uuid4(),
                name="Bananas",
                quantity=6.0,
                unit="pieces",
                expiry_date=today + timedelta(days=2),
                days_until_expiry=2
            )
        ]
        
        expired = [
            ExpiryItem(
                id=uuid4(),
                name="Old Bread",
                quantity=1.0,
                unit="loaf",
                expiry_date=today - timedelta(days=2),
                days_until_expiry=-2
            )
        ]
        
        fresh = [
            ExpiryItem(
                id=uuid4(),
                name="Canned Beans",
                quantity=3.0,
                unit="cans",
                expiry_date=today + timedelta(days=30),
                days_until_expiry=30
            )
        ]
        
        return PantryExpiryReport(
            expiring_soon=expiring_soon,
            expired=expired,
            fresh=fresh
        )

    @staticmethod
    def generate_low_stock_report(threshold: float = 1.0) -> PantryLowStockReport:
        """Generate low stock report."""
        low_stock_items = [
            LowStockItem(
                id=uuid4(),
                name="Salt",
                quantity=0.5,
                unit="kg",
                category="spices",
                suggested_restock_quantity=2.0
            ),
            LowStockItem(
                id=uuid4(),
                name="Sugar",
                quantity=0.8,
                unit="kg",
                category="baking",
                suggested_restock_quantity=1.5
            )
        ]
        
        return PantryLowStockReport(
            low_stock_items=low_stock_items,
            threshold_used=threshold
        )


class PantryMockFactory:
    """Factory for creating pantry-related mocks."""

    @staticmethod
    def create_supabase_response(
        success: bool = True,
        data: Optional[List[Dict]] = None,
        error: Optional[str] = None
    ) -> Mock:
        """Create a mock Supabase response."""
        mock_response = Mock()
        
        if success:
            mock_response.data = data or []
            mock_response.error = None
        else:
            mock_response.data = []
            mock_response.error = Mock()
            mock_response.error.message = error or "Mock error"
            mock_response.error.details = "Mock error details"
        
        return mock_response

    @staticmethod
    def create_pantry_item_db_row(
        id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        name: str = "Test Item",
        quantity: float = 1.0,
        unit: str = "pieces",
        category: Optional[str] = "test",
        expiry_date: Optional[str] = None,
        ingredient_id: Optional[UUID] = None,
        added_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a mock database row for a pantry item."""
        today = date.today()
        return {
            "id": str(id or uuid4()),
            "user_id": str(user_id or uuid4()),
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "category": category,
            "expiry_date": expiry_date or (today + timedelta(days=7)).isoformat(),
            "ingredient_id": str(ingredient_id or uuid4()),
            "added_at": added_at or datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    @staticmethod
    def create_bulk_operation_response(
        successful_count: int = 2,
        failed_count: int = 0,
        total_processed: int = 2
    ) -> Dict[str, Any]:
        """Create a mock bulk operation response."""
        successful_items = [
            PantryMockFactory.create_pantry_item_db_row(name=f"Item {i+1}")
            for i in range(successful_count)
        ]
        
        failed_items = [
            {
                "item": {"name": f"Failed Item {i+1}"},
                "error": "Mock validation error"
            }
            for i in range(failed_count)
        ]
        
        return {
            "successful": successful_items,
            "failed": failed_items,
            "total_processed": total_processed,
            "success_count": successful_count,
            "failure_count": failed_count
        }


class PantryTestScenarios:
    """Common test scenarios for pantry operations."""

    @staticmethod
    def valid_item_creation():
        """Scenario: Valid item creation."""
        return {
            "name": "Test creating a valid pantry item",
            "input": PantryTestDataGenerator.generate_pantry_item_create(),
            "expected_success": True
        }

    @staticmethod
    def invalid_item_creation():
        """Scenario: Invalid item creation."""
        return {
            "name": "Test creating an invalid pantry item",
            "input": PantryTestDataGenerator.generate_pantry_item_create(
                name="",  # Invalid empty name
                quantity=-1.0  # Invalid negative quantity
            ),
            "expected_success": False,
            "expected_error": "validation"
        }

    @staticmethod
    def bulk_create_within_limit():
        """Scenario: Bulk create within limits."""
        return {
            "name": "Test bulk create within 50 item limit",
            "input": PantryTestDataGenerator.generate_bulk_create_data(10),
            "expected_success": True
        }

    @staticmethod
    def bulk_create_exceeds_limit():
        """Scenario: Bulk create exceeding limits."""
        return {
            "name": "Test bulk create exceeding 50 item limit",
            "input": PantryTestDataGenerator.generate_bulk_create_data(51),
            "expected_success": False,
            "expected_error": "validation"
        }

    @staticmethod
    def stats_with_data():
        """Scenario: Getting stats with existing data."""
        return {
            "name": "Test getting pantry statistics with data",
            "expected_stats": PantryTestDataGenerator.generate_stats_overview(),
            "expected_success": True
        }

    @staticmethod
    def stats_empty_pantry():
        """Scenario: Getting stats with empty pantry."""
        return {
            "name": "Test getting pantry statistics with empty pantry",
            "expected_stats": PantryTestDataGenerator.generate_stats_overview(
                total_items=0,
                total_categories=0,
                items_expiring_soon=0,
                expired_items=0,
                low_stock_items=0,
                most_common_category=None
            ),
            "expected_success": True
        }


# Common test constants
VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"
INVALID_UUID = "invalid-uuid"
NON_EXISTENT_UUID = "00000000-0000-0000-0000-000000000000"

# Error messages
VALIDATION_ERROR_MSG = "Validation error"
NOT_FOUND_ERROR_MSG = "Item not found"
UNAUTHORIZED_ERROR_MSG = "Unauthorized"
BULK_LIMIT_ERROR_MSG = "Cannot create more than 50 items at once"
