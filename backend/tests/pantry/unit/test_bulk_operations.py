"""
Unit Tests for Pantry Items Bulk Operations.

This module tests bulk create, update, and delete operations for pantry items.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import date, timedelta

from domains.pantry_items.schemas import (
    PantryItemBulkCreate,
    PantryItemBulkUpdate,
    PantryItemBulkDelete,
    PantryItemBulkApiResponse,
    PantryItemCreate,
    PantryItemUpdate,
    ErrorResponse
)
from domains.pantry_items.services import (
    PantryItemError,
    PantryItemValidationError,
    bulk_create_pantry_items,
    bulk_update_pantry_items,
    bulk_delete_pantry_items
)
from tests.pantry.config import PantryTestBase, TEST_USER_ID, SAMPLE_PANTRY_ITEMS_BULK
from tests.pantry.utils.test_data import (
    PantryTestDataGenerator,
    PantryMockFactory,
    PantryTestScenarios
)


class TestPantryBulkOperations(PantryTestBase):
    """Test bulk operations for pantry items."""

    def test_main_functionality(self):
        """Required by PantryTestBase - tests basic bulk functionality."""
        self.test_bulk_create_success()

    @pytest.mark.asyncio
    async def test_bulk_create_success(self):
        """Test successful bulk creation of pantry items."""
        # Prepare test data
        bulk_data = PantryTestDataGenerator.generate_bulk_create_data(3)
        user_id = UUID(TEST_USER_ID)

        # Mock successful database responses
        mock_responses = []
        for i, item in enumerate(bulk_data.items):
            db_row = PantryMockFactory.create_pantry_item_db_row(
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                category=item.category,
                ingredient_id=item.ingredient_id
            )
            mock_responses.append(db_row)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock successful insert
            mock_client.table().insert().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=mock_responses
            )

            # Execute bulk create
            result = await bulk_create_pantry_items(bulk_data, user_id)

            # Assertions
            assert result.success_count == 3
            assert result.failure_count == 0
            assert result.total_processed == 3
            assert len(result.successful) == 3
            assert len(result.failed) == 0

            # Verify database calls
            mock_client.table.assert_called_with("pantry_items")
            mock_client.table().insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_create_partial_failure(self):
        """Test bulk creation with some items failing validation."""
        # Prepare test data with one invalid item
        valid_items = [
            PantryTestDataGenerator.generate_pantry_item_create(name="Valid Item 1"),
            PantryTestDataGenerator.generate_pantry_item_create(name="Valid Item 2")
        ]
        
        # Create invalid item (empty name)
        invalid_item_data = PantryTestDataGenerator.generate_pantry_item_data()
        invalid_item_data["name"] = ""  # Invalid empty name
        
        # This should raise validation error when creating PantryItemCreate
        with pytest.raises(ValueError):
            PantryItemCreate(**invalid_item_data)

    @pytest.mark.asyncio
    async def test_bulk_create_exceeds_limit(self):
        """Test bulk creation exceeding the 50-item limit."""
        # Create data exceeding limit
        bulk_data = PantryTestDataGenerator.generate_bulk_create_data(51)
        user_id = UUID(TEST_USER_ID)

        # This should raise validation error due to limit
        with pytest.raises(ValueError, match="Cannot create more than 50 items at once"):
            await bulk_create_pantry_items(bulk_data, user_id)

    @pytest.mark.asyncio
    async def test_bulk_create_database_error(self):
        """Test bulk creation with database error."""
        bulk_data = PantryTestDataGenerator.generate_bulk_create_data(2)
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock database error
            mock_client.table().insert().execute.return_value = PantryMockFactory.create_supabase_response(
                success=False,
                error="Database connection failed"
            )

            # Execute and expect error
            with pytest.raises(PantryItemError):
                await bulk_create_pantry_items(bulk_data, user_id)

    @pytest.mark.asyncio
    async def test_bulk_update_success(self):
        """Test successful bulk update of pantry items."""
        # Prepare test data
        item_ids = [uuid4(), uuid4()]
        bulk_update = PantryTestDataGenerator.generate_bulk_update_data(item_ids)
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock successful updates for each item
            updated_rows = [
                PantryMockFactory.create_pantry_item_db_row(
                    id=item_id,
                    name=f"Updated Item {i+1}",
                    quantity=float(i+10)
                )
                for i, item_id in enumerate(item_ids)
            ]
            
            mock_client.table().update().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=updated_rows
            )

            # Execute bulk update
            result = await bulk_update_pantry_items(bulk_update, user_id)

            # Assertions
            assert result.success_count == 2
            assert result.failure_count == 0
            assert result.total_processed == 2
            assert len(result.successful) == 2
            assert len(result.failed) == 0

    @pytest.mark.asyncio
    async def test_bulk_update_item_not_found(self):
        """Test bulk update with non-existent item."""
        # Use non-existent item ID
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        bulk_update = PantryTestDataGenerator.generate_bulk_update_data([non_existent_id])
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock empty response (item not found)
            mock_client.table().update().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=[]  # No items updated
            )

            # Execute and expect error
            result = await bulk_update_pantry_items(bulk_update, user_id)
            
            # Should have one failed item
            assert result.success_count == 0
            assert result.failure_count == 1
            assert len(result.failed) == 1

    @pytest.mark.asyncio
    async def test_bulk_delete_success(self):
        """Test successful bulk deletion of pantry items."""
        # Prepare test data
        item_ids = [uuid4(), uuid4(), uuid4()]
        bulk_delete = PantryTestDataGenerator.generate_bulk_delete_data(item_ids)
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock successful deletion
            deleted_rows = [
                PantryMockFactory.create_pantry_item_db_row(id=item_id)
                for item_id in item_ids
            ]
            
            mock_client.table().delete().in_().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=deleted_rows
            )

            # Execute bulk delete
            result = await bulk_delete_pantry_items(bulk_delete, user_id)

            # Assertions
            assert result.success_count == 3
            assert result.failure_count == 0
            assert result.total_processed == 3
            assert len(result.successful) == 3
            assert len(result.failed) == 0

    @pytest.mark.asyncio
    async def test_bulk_delete_exceeds_limit(self):
        """Test bulk deletion exceeding the 50-item limit."""
        # Create data exceeding limit
        item_ids = [uuid4() for _ in range(51)]
        bulk_delete = PantryTestDataGenerator.generate_bulk_delete_data(item_ids)
        user_id = UUID(TEST_USER_ID)

        # This should raise validation error due to limit
        with pytest.raises(ValueError, match="Cannot delete more than 50 items at once"):
            await bulk_delete_pantry_items(bulk_delete, user_id)

    @pytest.mark.asyncio
    async def test_bulk_delete_partial_success(self):
        """Test bulk deletion with some items not found."""
        # Mix of existing and non-existent IDs
        existing_ids = [uuid4(), uuid4()]
        non_existent_ids = [uuid4()]
        all_ids = existing_ids + non_existent_ids
        
        bulk_delete = PantryTestDataGenerator.generate_bulk_delete_data(all_ids)
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock partial success (only existing items deleted)
            deleted_rows = [
                PantryMockFactory.create_pantry_item_db_row(id=item_id)
                for item_id in existing_ids
            ]
            
            mock_client.table().delete().in_().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=deleted_rows
            )

            # Execute bulk delete
            result = await bulk_delete_pantry_items(bulk_delete, user_id)

            # Assertions
            assert result.success_count == 2  # Only existing items deleted
            assert result.failure_count == 1  # One item not found
            assert result.total_processed == 3

    @pytest.mark.asyncio
    async def test_bulk_operations_empty_lists(self):
        """Test bulk operations with empty item lists."""
        user_id = UUID(TEST_USER_ID)

        # Test empty bulk create
        with pytest.raises(ValueError, match="min_length"):
            PantryItemBulkCreate(items=[])

        # Test empty bulk update
        with pytest.raises(ValueError, match="min_length"):
            PantryItemBulkUpdate(updates={})

        # Test empty bulk delete
        with pytest.raises(ValueError, match="min_length"):
            PantryItemBulkDelete(item_ids=[])

    @pytest.mark.asyncio 
    async def test_bulk_create_with_duplicate_ingredient_ids(self):
        """Test bulk creation with duplicate ingredient IDs (should be allowed)."""
        # Create items with same ingredient ID
        shared_ingredient_id = uuid4()
        items = [
            PantryTestDataGenerator.generate_pantry_item_create(
                name=f"Item {i+1}",
                ingredient_id=shared_ingredient_id
            )
            for i in range(3)
        ]
        
        bulk_data = PantryItemBulkCreate(items=items)
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock successful creation
            mock_responses = [
                PantryMockFactory.create_pantry_item_db_row(
                    name=item.name,
                    ingredient_id=item.ingredient_id
                )
                for item in items
            ]
            
            mock_client.table().insert().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=mock_responses
            )

            # Execute bulk create
            result = await bulk_create_pantry_items(bulk_data, user_id)

            # Should succeed even with duplicate ingredient IDs
            assert result.success_count == 3
            assert result.failure_count == 0

    @pytest.mark.asyncio
    async def test_bulk_update_validation_errors(self):
        """Test bulk update with validation errors in update data."""
        item_id = uuid4()
        user_id = UUID(TEST_USER_ID)
        
        # Create update with invalid data
        invalid_update = PantryItemUpdate(
            quantity=-1.0,  # Invalid negative quantity
            name=""  # Invalid empty name
        )
        
        # This should raise validation error
        with pytest.raises(ValueError):
            bulk_update = PantryItemBulkUpdate(updates={item_id: invalid_update})

    @pytest.mark.asyncio
    async def test_bulk_operations_performance(self):
        """Test bulk operations complete within reasonable time."""
        import time
        
        # Create moderate-sized bulk operation
        bulk_data = PantryTestDataGenerator.generate_bulk_create_data(20)
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock fast response
            mock_client.table().insert().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=[PantryMockFactory.create_pantry_item_db_row() for _ in range(20)]
            )

            # Measure execution time
            start_time = time.time()
            result = await bulk_create_pantry_items(bulk_data, user_id)
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Should complete within performance threshold
            assert execution_time < self.config.PANTRY_MAX_BULK_TIME_MS
            assert result.success_count == 20
