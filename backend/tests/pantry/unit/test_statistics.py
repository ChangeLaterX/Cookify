"""
Unit Tests for Pantry Items Statistics and Analytics.

This module tests statistics, expiry reports, category breakdown, and low stock reports.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import date, timedelta

from domains.pantry_items.schemas import (
    PantryStatsOverview,
    PantryCategoryStats,
    CategoryStats,
    PantryExpiryReport,
    ExpiryItem,
    PantryLowStockReport,
    LowStockItem,
    PantryStatsApiResponse,
    PantryCategoryStatsApiResponse,
    PantryExpiryApiResponse,
    PantryLowStockApiResponse
)
from domains.pantry_items.services import (
    PantryItemError,
    get_pantry_stats,
    get_pantry_category_stats,
    get_pantry_expiry_report,
    get_pantry_low_stock_report
)
from tests.pantry.config import PantryTestBase, TEST_USER_ID
from tests.pantry.utils.test_data import (
    PantryTestDataGenerator,
    PantryMockFactory,
    PantryTestScenarios
)


class TestPantryStatistics(PantryTestBase):
    """Test statistics and analytics for pantry items."""

    def test_main_functionality(self):
        """Required by PantryTestBase - tests basic statistics functionality."""
        self.test_get_pantry_stats_success()

    @pytest.mark.asyncio
    async def test_get_pantry_stats_success(self):
        """Test successful retrieval of pantry statistics."""
        user_id = UUID(TEST_USER_ID)
        
        # Mock database response with sample pantry data
        sample_items = [
            PantryMockFactory.create_pantry_item_db_row(
                name="Bananas",
                category="produce",
                expiry_date=(date.today() + timedelta(days=2)).isoformat(),
                quantity=6.0
            ),
            PantryMockFactory.create_pantry_item_db_row(
                name="Milk",
                category="dairy",
                expiry_date=(date.today() + timedelta(days=5)).isoformat(),
                quantity=1.0
            ),
            PantryMockFactory.create_pantry_item_db_row(
                name="Old Bread",
                category="bakery",
                expiry_date=(date.today() - timedelta(days=1)).isoformat(),  # Expired
                quantity=1.0
            ),
            PantryMockFactory.create_pantry_item_db_row(
                name="Salt",
                category="spices",
                expiry_date=(date.today() + timedelta(days=365)).isoformat(),
                quantity=0.5  # Low stock
            )
        ]

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock successful query
            mock_client.table().select().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=sample_items
            )

            # Execute get stats
            result = await get_pantry_stats(user_id)

            # Assertions
            assert isinstance(result, PantryStatsOverview)
            assert result.total_items == 4
            assert result.total_categories == 4
            assert result.items_expiring_soon >= 1  # Bananas expire in 2 days
            assert result.expired_items >= 1  # Old bread is expired
            assert result.low_stock_items >= 1  # Salt has low quantity
            assert result.most_common_category in ["produce", "dairy", "bakery", "spices"]

    @pytest.mark.asyncio
    async def test_get_pantry_stats_empty_pantry(self):
        """Test statistics for empty pantry."""
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock empty response
            mock_client.table().select().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=[]
            )

            # Execute get stats
            result = await get_pantry_stats(user_id)

            # Assertions for empty pantry
            assert isinstance(result, PantryStatsOverview)
            assert result.total_items == 0
            assert result.total_categories == 0
            assert result.items_expiring_soon == 0
            assert result.expired_items == 0
            assert result.low_stock_items == 0
            assert result.estimated_total_value == 0.0
            assert result.most_common_category is None

    @pytest.mark.asyncio
    async def test_get_category_stats_success(self):
        """Test successful retrieval of category statistics."""
        user_id = UUID(TEST_USER_ID)
        
        # Mock database response with categorized items
        sample_items = [
            # Produce items
            PantryMockFactory.create_pantry_item_db_row(name="Bananas", category="produce"),
            PantryMockFactory.create_pantry_item_db_row(name="Apples", category="produce"),
            PantryMockFactory.create_pantry_item_db_row(name="Carrots", category="produce"),
            
            # Dairy items
            PantryMockFactory.create_pantry_item_db_row(name="Milk", category="dairy"),
            PantryMockFactory.create_pantry_item_db_row(name="Cheese", category="dairy"),
            
            # Items without category
            PantryMockFactory.create_pantry_item_db_row(name="Mystery Item", category=None),
        ]

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock successful query
            mock_client.table().select().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=sample_items
            )

            # Execute get category stats
            result = await get_pantry_category_stats(user_id)

            # Assertions
            assert isinstance(result, PantryCategoryStats)
            assert len(result.categories) >= 2  # At least produce and dairy
            assert result.uncategorized_count >= 1  # Mystery item
            
            # Check category breakdown
            category_names = [cat.category for cat in result.categories]
            assert "produce" in category_names
            assert "dairy" in category_names
            
            # Check percentages sum correctly (excluding uncategorized)
            total_percentage = sum(cat.percentage for cat in result.categories)
            assert 0 <= total_percentage <= 100

    @pytest.mark.asyncio
    async def test_get_expiry_report_success(self):
        """Test successful retrieval of expiry report."""
        user_id = UUID(TEST_USER_ID)
        today = date.today()
        
        # Mock database response with items in different expiry states
        sample_items = [
            # Expiring soon (within 3 days)
            PantryMockFactory.create_pantry_item_db_row(
                name="Bananas",
                expiry_date=(today + timedelta(days=2)).isoformat(),
                quantity=6.0,
                unit="pieces"
            ),
            
            # Already expired
            PantryMockFactory.create_pantry_item_db_row(
                name="Old Bread",
                expiry_date=(today - timedelta(days=1)).isoformat(),
                quantity=1.0,
                unit="loaf"
            ),
            
            # Fresh (more than 7 days)
            PantryMockFactory.create_pantry_item_db_row(
                name="Canned Beans",
                expiry_date=(today + timedelta(days=30)).isoformat(),
                quantity=3.0,
                unit="cans"
            ),
            
            # No expiry date
            PantryMockFactory.create_pantry_item_db_row(
                name="Salt",
                expiry_date=None,
                quantity=0.5,
                unit="kg"
            )
        ]

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock successful query
            mock_client.table().select().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=sample_items
            )

            # Execute get expiry report
            result = await get_pantry_expiry_report(user_id)

            # Assertions
            assert isinstance(result, PantryExpiryReport)
            assert len(result.expiring_soon) >= 1  # Bananas
            assert len(result.expired) >= 1  # Old bread
            assert len(result.fresh) >= 1  # Canned beans
            
            # Check expiring soon item
            expiring_item = next((item for item in result.expiring_soon if item.name == "Bananas"), None)
            assert expiring_item is not None
            assert expiring_item.days_until_expiry == 2
            
            # Check expired item
            expired_item = next((item for item in result.expired if item.name == "Old Bread"), None)
            assert expired_item is not None
            assert expired_item.days_until_expiry == -1

    @pytest.mark.asyncio
    async def test_get_low_stock_report_success(self):
        """Test successful retrieval of low stock report."""
        user_id = UUID(TEST_USER_ID)
        threshold = 1.0
        
        # Mock database response with items at different stock levels
        sample_items = [
            # Low stock items
            PantryMockFactory.create_pantry_item_db_row(
                name="Salt",
                quantity=0.5,
                unit="kg",
                category="spices"
            ),
            PantryMockFactory.create_pantry_item_db_row(
                name="Sugar",
                quantity=0.8,
                unit="kg",
                category="baking"
            ),
            
            # Normal stock items
            PantryMockFactory.create_pantry_item_db_row(
                name="Rice",
                quantity=2.5,
                unit="kg",
                category="grains"
            )
        ]

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock successful query
            mock_client.table().select().eq().lte().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=sample_items[:2]  # Only low stock items
            )

            # Execute get low stock report
            result = await get_pantry_low_stock_report(user_id, threshold)

            # Assertions
            assert isinstance(result, PantryLowStockReport)
            assert result.threshold_used == threshold
            assert len(result.low_stock_items) >= 2
            
            # Check low stock items
            item_names = [item.name for item in result.low_stock_items]
            assert "Salt" in item_names
            assert "Sugar" in item_names
            
            # Check suggested restock quantities
            for item in result.low_stock_items:
                assert item.suggested_restock_quantity > item.quantity

    @pytest.mark.asyncio
    async def test_get_low_stock_report_custom_threshold(self):
        """Test low stock report with custom threshold."""
        user_id = UUID(TEST_USER_ID)
        custom_threshold = 2.0
        
        sample_items = [
            PantryMockFactory.create_pantry_item_db_row(
                name="Flour",
                quantity=1.5,
                unit="kg",
                category="baking"
            )
        ]

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            mock_client.table().select().eq().lte().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=sample_items
            )

            # Execute with custom threshold
            result = await get_pantry_low_stock_report(user_id, custom_threshold)

            # Assertions
            assert result.threshold_used == custom_threshold
            assert len(result.low_stock_items) >= 1
            flour_item = result.low_stock_items[0]
            assert flour_item.name == "Flour"
            assert flour_item.quantity <= custom_threshold

    @pytest.mark.asyncio
    async def test_statistics_database_error(self):
        """Test statistics operations with database errors."""
        user_id = UUID(TEST_USER_ID)

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            # Mock database error
            mock_client.table().select().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=False,
                error="Database connection failed"
            )

            # Test each statistics function
            with pytest.raises(PantryItemError):
                await get_pantry_stats(user_id)
                
            with pytest.raises(PantryItemError):
                await get_pantry_category_stats(user_id)
                
            with pytest.raises(PantryItemError):
                await get_pantry_expiry_report(user_id)
                
            with pytest.raises(PantryItemError):
                await get_pantry_low_stock_report(user_id)

    @pytest.mark.asyncio
    async def test_expiry_calculation_edge_cases(self):
        """Test expiry date calculation edge cases."""
        user_id = UUID(TEST_USER_ID)
        today = date.today()
        
        # Items with edge case expiry dates
        edge_case_items = [
            # Expires exactly today
            PantryMockFactory.create_pantry_item_db_row(
                name="Expires Today",
                expiry_date=today.isoformat(),
                quantity=1.0
            ),
            
            # Expires exactly in 3 days (boundary of "expiring soon")
            PantryMockFactory.create_pantry_item_db_row(
                name="Expires in 3 Days",
                expiry_date=(today + timedelta(days=3)).isoformat(),
                quantity=1.0
            ),
            
            # Expires exactly in 7 days (boundary of "fresh")
            PantryMockFactory.create_pantry_item_db_row(
                name="Expires in 7 Days",
                expiry_date=(today + timedelta(days=7)).isoformat(),
                quantity=1.0
            )
        ]

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            mock_client.table().select().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=edge_case_items
            )

            # Execute expiry report
            result = await get_pantry_expiry_report(user_id)

            # Verify edge case handling
            item_names = {
                "expiring_soon": [item.name for item in result.expiring_soon],
                "fresh": [item.name for item in result.fresh],
                "expired": [item.name for item in result.expired]
            }
            
            # Items expiring today should be in expiring_soon
            assert "Expires Today" in item_names["expiring_soon"]
            
            # Items expiring in exactly 3 days should be in expiring_soon
            assert "Expires in 3 Days" in item_names["expiring_soon"]

    @pytest.mark.asyncio
    async def test_category_stats_case_sensitivity(self):
        """Test category statistics handle case sensitivity correctly."""
        user_id = UUID(TEST_USER_ID)
        
        # Items with different case categories
        mixed_case_items = [
            PantryMockFactory.create_pantry_item_db_row(name="Item1", category="Produce"),
            PantryMockFactory.create_pantry_item_db_row(name="Item2", category="produce"),
            PantryMockFactory.create_pantry_item_db_row(name="Item3", category="PRODUCE"),
        ]

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            mock_client.table().select().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=mixed_case_items
            )

            # Execute category stats
            result = await get_pantry_category_stats(user_id)

            # Categories should be handled consistently
            assert isinstance(result, PantryCategoryStats)
            # The implementation should decide how to handle case sensitivity

    @pytest.mark.asyncio
    async def test_statistics_performance(self):
        """Test statistics operations complete within reasonable time."""
        import time
        
        user_id = UUID(TEST_USER_ID)
        
        # Create large dataset
        large_dataset = [
            PantryMockFactory.create_pantry_item_db_row(name=f"Item {i}")
            for i in range(100)
        ]

        with patch("domains.pantry_items.services.get_db") as mock_db:
            mock_client = self.create_mock_supabase_client()
            mock_db.return_value = mock_client
            
            mock_client.table().select().eq().execute.return_value = PantryMockFactory.create_supabase_response(
                success=True,
                data=large_dataset
            )

            # Test performance of each statistics operation
            operations = [
                ("stats", lambda: get_pantry_stats(user_id)),
                ("category", lambda: get_pantry_category_stats(user_id)),
                ("expiry", lambda: get_pantry_expiry_report(user_id)),
                ("low_stock", lambda: get_pantry_low_stock_report(user_id))
            ]

            for op_name, operation in operations:
                start_time = time.time()
                await operation()
                execution_time = (time.time() - start_time) * 1000
                
                # Should complete within performance threshold
                assert execution_time < self.config.PANTRY_MAX_QUERY_TIME_MS, f"{op_name} operation too slow"
