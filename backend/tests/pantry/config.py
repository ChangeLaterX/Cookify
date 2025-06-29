"""
Pantry Test Configuration and Base Classes.

This module provides the base configuration and shared utilities for all Pantry tests.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

import pytest


@dataclass
class PantryTestConfig:
    """Configuration for Pantry tests."""

    # Test modes
    MOCK_MODE: bool = os.getenv("PANTRY_TEST_MOCK_MODE", "true").lower() == "true"
    INTEGRATION_MODE: bool = os.getenv("PANTRY_TEST_INTEGRATION", "false").lower() == "true"

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    TEST_ROOT: Path = PROJECT_ROOT / "tests" / "pantry"
    FIXTURES_PATH: Path = TEST_ROOT / "fixtures"

    # Dependencies
    SUPABASE_AVAILABLE: bool = (
        os.getenv("SUPABASE_URL") is not None and os.getenv("SUPABASE_ANON_KEY") is not None
    )

    # Test database settings
    TEST_DATABASE_URL: Optional[str] = os.getenv("TEST_SUPABASE_URL")
    TEST_ANON_KEY: Optional[str] = os.getenv("TEST_SUPABASE_ANON_KEY")

    # Bulk operation limits for testing
    MAX_BULK_ITEMS: int = 50
    TEST_BULK_SIZE: int = 10

    # Statistics thresholds for testing
    EXPIRING_SOON_DAYS: int = 3
    LOW_STOCK_THRESHOLD: float = 1.0

    # Test environment
    TEST_ENVIRONMENT: str = os.getenv("TEST_ENVIRONMENT", "unit")

    # Performance thresholds
    PANTRY_MAX_QUERY_TIME_MS: int = int(os.getenv("PANTRY_MAX_QUERY_TIME_MS", "500"))
    PANTRY_MAX_BULK_TIME_MS: int = int(os.getenv("PANTRY_MAX_BULK_TIME_MS", "2000"))


class PantryTestBase(ABC):
    """
    Abstract base class for all Pantry tests.
    
    Provides common setup and teardown functionality for all Pantry test classes.
    """

    config = PantryTestConfig()

    def setup_method(self, method):
        """Set up test method."""
        self.test_data = {}
        self.mocks = {}

    def teardown_method(self, method):
        """Clean up after test method."""
        # Clean up any created test data
        self.test_data.clear()
        
        # Stop any mocks
        for mock in self.mocks.values():
            if hasattr(mock, "stop"):
                mock.stop()
        self.mocks.clear()

    def test_main_functionality(self):
        """
        Test the main functionality for this test class.
        
        Each test class must implement this method to demonstrate core functionality.
        This ensures all test classes have at least one working test.
        """
        pass

    def create_mock_user(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a mock user for testing."""
        from uuid import uuid4
        
        return {
            "id": user_id or str(uuid4()),
            "email": "test@cookify.app",
            "email_confirmed_at": "2025-06-29T10:00:00.000Z",
            "created_at": "2025-06-29T10:00:00.000Z"
        }

    def create_mock_supabase_client(self) -> Mock:
        """Create a mock Supabase client with pantry-specific methods."""
        mock_client = Mock()
        
        # Mock table operations
        mock_table = Mock()
        mock_table.insert = Mock()
        mock_table.update = Mock()
        mock_table.select = Mock()
        mock_table.eq = Mock()
        mock_table.neq = Mock()
        mock_table.ilike = Mock()
        mock_table.range = Mock()
        mock_table.order = Mock()
        mock_table.execute = Mock()
        mock_table.delete = Mock()
        mock_table.gte = Mock()
        mock_table.lte = Mock()
        mock_table.is_ = Mock()
        mock_table.in_ = Mock()
        
        mock_client.table.return_value = mock_table
        
        return mock_client

    def skip_if_no_database(self):
        """Skip test if database is not available."""
        if not self.config.SUPABASE_AVAILABLE:
            pytest.skip("Supabase database not available for testing")

    def skip_if_mock_mode(self):
        """Skip test if in mock mode."""
        if self.config.MOCK_MODE:
            pytest.skip("Test requires real database (mock mode disabled)")

    def skip_if_integration_mode(self):
        """Skip test if in integration mode."""
        if self.config.INTEGRATION_MODE:
            pytest.skip("Test not applicable in integration mode")


class PantryMockContextManager:
    """Context manager for handling pantry-specific mocks."""

    def __init__(self, mock_supabase: bool = True, mock_auth: bool = True):
        self.mock_supabase = mock_supabase
        self.mock_auth = mock_auth
        self.patches = []

    def __enter__(self):
        """Enter the mock context."""
        if self.mock_supabase:
            # Mock Supabase client
            supabase_patch = patch("domains.pantry_items.services.get_db")
            self.patches.append(supabase_patch)
            self.mock_db = supabase_patch.start()

        if self.mock_auth:
            # Mock authentication
            auth_patch = patch("middleware.security.get_current_user")
            self.patches.append(auth_patch)
            self.mock_user = auth_patch.start()
            self.mock_user.return_value = {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "test@cookify.app"
            }

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the mock context."""
        for patch in reversed(self.patches):
            patch.stop()


def with_mock_pantry(func):
    """Decorator to automatically apply pantry mocks to test functions."""
    def wrapper(*args, **kwargs):
        with PantryMockContextManager():
            return func(*args, **kwargs)
    return wrapper


# Test data constants
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_INGREDIENT_ID = "550e8400-e29b-41d4-a716-446655440001"
TEST_PANTRY_ITEM_ID = "550e8400-e29b-41d4-a716-446655440002"

# Sample test data
SAMPLE_PANTRY_ITEM = {
    "name": "Bananas",
    "quantity": 6.0,
    "unit": "pieces",
    "category": "produce",
    "expiry_date": "2025-07-02",
    "ingredient_id": TEST_INGREDIENT_ID
}

SAMPLE_PANTRY_ITEMS_BULK = [
    {
        "name": "Bananas",
        "quantity": 6.0,
        "unit": "pieces",
        "category": "produce",
        "expiry_date": "2025-07-02",
        "ingredient_id": TEST_INGREDIENT_ID
    },
    {
        "name": "Milk",
        "quantity": 1.0,
        "unit": "liter",
        "category": "dairy",
        "expiry_date": "2025-07-05",
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440003"
    },
    {
        "name": "Bread",
        "quantity": 1.0,
        "unit": "loaf",
        "category": "bakery",
        "expiry_date": "2025-06-30",
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440004"
    }
]
