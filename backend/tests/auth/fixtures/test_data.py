"""
Test Fixtures for Auth Testing.

This module provides sample data and fixtures for Auth tests.
"""

import json
from typing import Dict, Any, List
from uuid import uuid4
from datetime import datetime, timedelta


# Sample valid user data
VALID_USER_DATA = {
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "username": "testuser"
}

# Sample invalid emails for testing validation
INVALID_EMAILS = [
    "invalid.email",
    "@invalid.com", 
    "invalid@",
    "invalid@.com",
    "invalid..email@test.com",
    "invalid email@test.com",
    "",
    "a" * 256 + "@test.com"  # Too long
]

# Sample weak passwords for testing validation
WEAK_PASSWORDS = [
    "123456",
    "password", 
    "12345",
    "qwerty",
    "abc123",
    "123",
    "",
    "a",  # Too short
    "onlylowercase",
    "ONLYUPPERCASE", 
    "1234567890"  # Only numbers
]

# Sample Supabase user response
SAMPLE_SUPABASE_USER = {
    "id": "12345678-1234-1234-1234-123456789012",
    "email": "test@example.com",
    "user_metadata": {
        "username": "testuser",
        "display_name": "Test User"
    },
    "email_confirmed_at": "2023-01-01T00:00:00Z",
    "created_at": "2023-01-01T00:00:00Z", 
    "updated_at": "2023-01-01T00:00:00Z",
    "aud": "authenticated",
    "role": "authenticated"
}

# Sample Supabase session response
SAMPLE_SUPABASE_SESSION = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_example",
    "expires_in": 3600,
    "token_type": "bearer",
    "expires_at": 1640995200
}

# Sample error responses
SAMPLE_AUTH_ERRORS = {
    "user_exists": {
        "message": "User already registered",
        "status": 422,
        "error_code": "signup_disabled"
    },
    "invalid_credentials": {
        "message": "Invalid login credentials",
        "status": 400,
        "error_code": "invalid_credentials"
    },
    "weak_password": {
        "message": "Password should be at least 6 characters",
        "status": 422,
        "error_code": "weak_password"
    }
}

# Test scenarios for registration
REGISTRATION_TEST_SCENARIOS = [
    {
        "name": "successful_registration",
        "input": VALID_USER_DATA,
        "expected_success": True,
        "expected_tokens": True
    },
    {
        "name": "duplicate_email",
        "input": VALID_USER_DATA,  # Same email as above
        "expected_success": False,
        "expected_error": "USER_ALREADY_EXISTS"
    }
]

# Test scenarios for authentication  
AUTHENTICATION_TEST_SCENARIOS = [
    {
        "name": "successful_login",
        "input": {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        },
        "expected_success": True,
        "expected_tokens": True
    },
    {
        "name": "wrong_password", 
        "input": {
            "email": "test@example.com",
            "password": "WrongPassword123!"
        },
        "expected_success": False,
        "expected_error": "INVALID_CREDENTIALS"
    },
    {
        "name": "nonexistent_user",
        "input": {
            "email": "nonexistent@example.com", 
            "password": "AnyPassword123!"
        },
        "expected_success": False,
        "expected_error": "USER_NOT_FOUND"
    }
]


def save_fixtures_to_file(filepath: str):
    """Save all fixtures to a JSON file for easy loading."""
    fixtures = {
        "valid_user_data": VALID_USER_DATA,
        "invalid_emails": INVALID_EMAILS,
        "weak_passwords": WEAK_PASSWORDS,
        "sample_supabase_user": SAMPLE_SUPABASE_USER,
        "sample_supabase_session": SAMPLE_SUPABASE_SESSION,
        "sample_auth_errors": SAMPLE_AUTH_ERRORS,
        "registration_scenarios": REGISTRATION_TEST_SCENARIOS,
        "authentication_scenarios": AUTHENTICATION_TEST_SCENARIOS
    }
    
    with open(filepath, 'w') as f:
        json.dump(fixtures, f, indent=2)


if __name__ == "__main__":
    # Save fixtures when run directly
    import os
    fixtures_dir = os.path.dirname(__file__)
    save_fixtures_to_file(os.path.join(fixtures_dir, "auth_test_data.json"))
