"""
Test data generators and utilities for authentication domain tests.
"""

import secrets
import string
from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class TestUserData:
    """Test user data structure."""

    email: str
    password: str
    user_id: Optional[str] = None
    name: Optional[str] = None
    is_verified: bool = False


class TestDataGenerator:
    """Generate test data for authentication tests."""

    @staticmethod
    def generate_email(domain: str = "test.com") -> str:
        """Generate a test email address."""
        username = "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
        return f"{username}@{domain}"

    @staticmethod
    def generate_password(length: int = 12, include_special: bool = True) -> str:
        """Generate a test password."""
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += "!@#$%^&*"
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def generate_user_id() -> str:
        """Generate a test user ID."""
        return str(uuid4())

    @staticmethod
    def create_test_user(
        email: Optional[str] = None,
        password: Optional[str] = None,
        verified: bool = False,
    ) -> TestUserData:
        """Create a complete test user."""
        return TestUserData(
            email=email or TestDataGenerator.generate_email(),
            password=password or TestDataGenerator.generate_password(),
            user_id=TestDataGenerator.generate_user_id(),
            name=f"Test User {secrets.randbelow(1000)}",
            is_verified=verified,
        )


class TestScenarios:
    """Common test scenarios for authentication."""

    @staticmethod
    def valid_registration_data() -> Dict:
        """Valid user registration data."""
        return {
            "email": TestDataGenerator.generate_email(),
            "password": TestDataGenerator.generate_password(),
            "name": "Test User",
        }

    @staticmethod
    def valid_login_data() -> Dict:
        """Valid login credentials."""
        return {"email": "test@example.com", "password": "ValidPassword123!"}

    @staticmethod
    def invalid_email_formats() -> List[str]:
        """List of invalid email formats for testing."""
        return [
            "invalid.email",
            "@domain.com",
            "user@",
            "user@domain",
            "user name@domain.com",
            "",
            "user@domain..com",
        ]

    @staticmethod
    def weak_passwords() -> List[str]:
        """List of weak passwords for testing."""
        return ["123", "password", "abc", "", "12345678", "aaaaaaaa"]

    @staticmethod
    def strong_passwords() -> List[str]:
        """List of strong passwords for testing."""
        return [
            "StrongPass123!",
            "MySecureP@ssw0rd",
            "C0mpl3x!P@ssword",
            "Secur3#Passw0rd!",
        ]


class MockAuthResponses:
    """Mock responses for authentication API calls."""

    @staticmethod
    def successful_registration():
        """Mock successful registration response."""
        return {
            "user": {
                "id": TestDataGenerator.generate_user_id(),
                "email": TestDataGenerator.generate_email(),
                "email_confirmed_at": None,
                "created_at": "2024-01-01T00:00:00Z",
            },
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
        }

    @staticmethod
    def successful_login():
        """Mock successful login response."""
        return {
            "access_token": "mock_access_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
            "user": {
                "id": TestDataGenerator.generate_user_id(),
                "email": "test@example.com",
            },
        }

    @staticmethod
    def error_response(message: str, code: int = 400):
        """Mock error response."""
        return {"error": {"message": message, "code": code}}
