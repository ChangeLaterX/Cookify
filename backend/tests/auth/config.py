"""
Auth Test Configuration and Base Classes.

This module provides the base configuration and shared utilities for all Auth tests.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


@dataclass
class AuthTestConfig:
    """Configuration for Auth tests."""

    # Test modes
    MOCK_MODE: bool = os.getenv("AUTH_TEST_MOCK_MODE", "true").lower() == "true"
    INTEGRATION_MODE: bool = (
        os.getenv("AUTH_TEST_INTEGRATION", "false").lower() == "true"
    )

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    TEST_ROOT: Path = PROJECT_ROOT / "tests" / "auth"
    FIXTURES_PATH: Path = TEST_ROOT / "fixtures"

    # Dependencies
    SUPABASE_AVAILABLE: bool = (
        os.getenv("SUPABASE_URL") is not None
        and os.getenv("SUPABASE_ANON_KEY") is not None
    )

    # Test database settings
    TEST_DATABASE_URL: Optional[str] = os.getenv("TEST_SUPABASE_URL")
    TEST_ANON_KEY: Optional[str] = os.getenv("TEST_SUPABASE_ANON_KEY")

    # Rate limiting settings for tests
    RATE_LIMIT_TESTING: bool = (
        os.getenv("AUTH_TEST_RATE_LIMITING", "false").lower() == "true"
    )

    # Email testing settings
    EMAIL_TESTING_ENABLED: bool = (
        os.getenv("AUTH_TEST_EMAIL", "false").lower() == "true"
    )
    TEST_EMAIL_DOMAIN: str = os.getenv("AUTH_TEST_EMAIL_DOMAIN", "test.cookify.app")

    # Test environment
    TEST_ENVIRONMENT: str = os.getenv("TEST_ENVIRONMENT", "unit")

    # Performance thresholds
    AUTH_MAX_LOGIN_TIME_MS: int = int(os.getenv("AUTH_MAX_LOGIN_TIME_MS", "100"))
    AUTH_MAX_TOKEN_VALIDATION_TIME_MS: int = int(
        os.getenv("AUTH_MAX_TOKEN_VALIDATION_TIME_MS", "50")
    )
    AUTH_MIN_THROUGHPUT_LOGIN_PER_SEC: int = int(
        os.getenv("AUTH_MIN_THROUGHPUT_LOGIN_PER_SEC", "20")
    )

    # Security test settings
    SECURITY_TEST_ENABLED: bool = (
        os.getenv("SECURITY_TEST_ENABLED", "true").lower() == "true"
    )

    # Email verification bypass for testing
    BYPASS_EMAIL_VERIFICATION: bool = (
        os.getenv("BYPASS_EMAIL_VERIFICATION", "true").lower() == "true"
    )

    # Test user credentials (for integration tests)
    TEST_USER_EMAIL: str = os.getenv("TEST_USER_EMAIL", "krijajannis@gmail.com")
    TEST_USER_PASSWORD: str = os.getenv("TEST_USER_PASSWORD", "221224")

    # Test mode flags
    ALLOW_PASSWORD_RESET_BYPASS: bool = (
        os.getenv("ALLOW_PASSWORD_RESET_BYPASS", "true").lower() == "true"
    )
    ALLOW_ACCOUNT_DELETION_BYPASS: bool = (
        os.getenv("ALLOW_ACCOUNT_DELETION_BYPASS", "true").lower() == "true"
    )


class AuthTestBase(ABC):
    """
    Abstract base class for all Auth tests.
    Provides common setup and utilities.
    """

    @classmethod
    def setup_class(cls):
        """Setup class-level resources."""
        cls.config = AuthTestConfig()

    def setup_method(self):
        """Setup method-level resources."""
        self.config = AuthTestConfig()

    def teardown_method(self):
        """Cleanup after each test method."""
        pass

    @abstractmethod
    def test_main_functionality(self):
        """Each test class must implement its main test."""
        pass


class AuthTestUtils:
    """Utility methods for Auth testing."""

    @staticmethod
    def generate_test_email(prefix: str = "test") -> str:
        """Generate a unique test email address."""
        import uuid

        return f"{prefix}_{uuid.uuid4().hex[:8]}@test.cookify.app"

    @staticmethod
    def generate_test_password() -> str:
        """Generate a secure test password."""
        import secrets
        import string

        # Generate password with at least one uppercase, lowercase, digit, and special char
        length = 12
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(chars) for _ in range(length))

        # Ensure it has required character types
        if not any(c.isupper() for c in password):
            password = password[:-1] + "A"
        if not any(c.islower() for c in password):
            password = password[:-2] + "a" + password[-1]
        if not any(c.isdigit() for c in password):
            password = password[:-3] + "1" + password[-2:]
        if not any(c in "!@#$%^&*" for c in password):
            password = password[:-4] + "!" + password[-3:]

        return password

    @staticmethod
    def create_mock_supabase_response(
        success: bool = True, user_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a mock Supabase response."""
        if success:
            return {
                "user": user_data
                or {
                    "id": "12345678-1234-1234-1234-123456789012",
                    "email": "test@example.com",
                    "user_metadata": {
                        "username": "testuser",
                        "display_name": "Test User",
                    },
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                },
                "session": {
                    "access_token": "mock_access_token",
                    "refresh_token": "mock_refresh_token",
                    "expires_in": 3600,
                    "token_type": "bearer",
                },
            }
        else:
            return {"user": None, "session": None}


class MockSupabaseClient:
    """Mock Supabase client for testing."""

    def __init__(self, mock_responses: Optional[Dict[str, Any]] = None):
        self.mock_responses = mock_responses or {}
        self.auth = MockSupabaseAuth()

    def table(self, table_name: str):
        return MockSupabaseTable(table_name)


class MockSupabaseAuth:
    """Mock Supabase Auth for testing."""

    def __init__(self):
        self.sign_up_response = None
        self.sign_in_response = None
        self.sign_out_response = None

    def sign_up(self, credentials: Dict[str, Any]):
        if self.sign_up_response:
            return self.sign_up_response
        return AuthTestUtils.create_mock_supabase_response()

    def sign_in_with_password(self, credentials: Dict[str, Any]):
        if self.sign_in_response:
            return self.sign_in_response
        return AuthTestUtils.create_mock_supabase_response()

    def sign_out(self):
        if self.sign_out_response:
            return self.sign_out_response
        return {"error": None}


class MockSupabaseTable:
    """Mock Supabase table operations for testing."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.insert_response = None
        self.select_response = None
        self.update_response = None

    def insert(self, data: Dict[str, Any]):
        return MockSupabaseQuery(
            self.insert_response or {"data": [data], "error": None}
        )

    def select(self, columns: str = "*"):
        return MockSupabaseQuery(self.select_response or {"data": [], "error": None})

    def update(self, data: Dict[str, Any]):
        return MockSupabaseQuery(
            self.update_response or {"data": [data], "error": None}
        )


class MockSupabaseQuery:
    """Mock Supabase query for testing."""

    def __init__(self, response: Dict[str, Any]):
        self.response = response

    def eq(self, column: str, value: Any):
        return self

    def execute(self):
        return self.response
