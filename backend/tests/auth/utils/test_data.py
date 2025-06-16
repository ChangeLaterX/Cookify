"""
Test Data Generators for Auth Testing.

This module provides utilities for generating test data for Auth tests.
"""

import uuid
import random
import string
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from domains.auth.schemas import UserCreate, UserLogin


@dataclass
class TestUserData:
    """Container for test user data."""
    email: str
    password: str
    username: str
    user_id: str
    
    def to_user_create(self) -> UserCreate:
        """Convert to UserCreate schema."""
        return UserCreate(
            email=self.email,
            password=self.password,
            username=self.username
        )
    
    def to_user_login(self) -> UserLogin:
        """Convert to UserLogin schema."""
        return UserLogin(
            email=self.email,
            password=self.password
        )


class TestDataGenerator:
    """Generator for creating test data for Auth tests."""
    
    # Common test domains for email generation
    TEST_DOMAINS = [
        "test.cookify.app",
        "example.com", 
        "test.local",
        "mockdomain.org"
    ]
    
    # Common username prefixes
    USERNAME_PREFIXES = [
        "testuser",
        "mockuser", 
        "demouser",
        "user",
        "test"
    ]
    
    @classmethod
    def generate_user_data(cls, 
                          email_prefix: Optional[str] = None,
                          username_prefix: Optional[str] = None,
                          weak_password: bool = False) -> TestUserData:
        """Generate complete test user data."""
        
        # Generate email
        prefix = email_prefix or random.choice(["test", "user", "demo"])
        domain = random.choice(cls.TEST_DOMAINS)
        unique_id = uuid.uuid4().hex[:8]
        email = f"{prefix}_{unique_id}@{domain}"
        
        # Generate username
        username_base = username_prefix or random.choice(cls.USERNAME_PREFIXES)
        username = f"{username_base}_{unique_id[:6]}"
        
        # Generate password
        password = cls.generate_password(weak=weak_password)
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        return TestUserData(
            email=email,
            password=password,
            username=username,
            user_id=user_id
        )
    
    @classmethod
    def generate_password(cls, weak: bool = False, length: int = 12) -> str:
        """Generate a test password."""
        if weak:
            # Generate a weak password for negative testing
            return "123456"
        
        # Generate a strong password
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        
        # Ensure it meets requirements
        if not any(c.isupper() for c in password):
            password = password[:-1] + 'A'
        if not any(c.islower() for c in password):
            password = password[:-2] + 'a' + password[-1]
        if not any(c.isdigit() for c in password):
            password = password[:-3] + '1' + password[-2:]
        if not any(c in "!@#$%^&*" for c in password):
            password = password[:-4] + '!' + password[-3:]
            
        return password
    
    @classmethod
    def generate_bulk_users(cls, count: int = 10) -> List[TestUserData]:
        """Generate multiple test users."""
        return [cls.generate_user_data() for _ in range(count)]
    
    @classmethod
    def generate_invalid_emails(cls) -> List[str]:
        """Generate list of invalid email addresses for testing."""
        return [
            "invalid.email",
            "@invalid.com",
            "invalid@",
            "invalid@.com",
            "invalid..email@test.com",
            "invalid email@test.com",
            "",
            "a" * 256 + "@test.com",  # Too long
        ]
    
    @classmethod
    def generate_weak_passwords(cls) -> List[str]:
        """Generate list of weak passwords for testing."""
        return [
            "123456",
            "password",
            "12345",
            "qwerty",
            "abc123",
            "123",
            "",
            "a",  # Too short
            "a" * 200,  # Too long
            "onlylowercase",
            "ONLYUPPERCASE",
            "12345678901234567890",  # Only numbers
        ]
    
    @classmethod
    def generate_supabase_user_dict(cls, user_data: TestUserData) -> Dict[str, Any]:
        """Generate a Supabase user dictionary from test user data."""
        return {
            "id": user_data.user_id,
            "email": user_data.email,
            "user_metadata": {
                "username": user_data.username,
                "display_name": user_data.username
            },
            "email_confirmed_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "aud": "authenticated",
            "role": "authenticated",
            "app_metadata": {
                "provider": "email",
                "providers": ["email"]
            }
        }
    
    @classmethod
    def generate_supabase_session_dict(cls, user_data: TestUserData) -> Dict[str, Any]:
        """Generate a Supabase session dictionary."""
        expires_in = 3600
        return {
            "access_token": f"access_token_{uuid.uuid4().hex[:16]}",
            "refresh_token": f"refresh_token_{uuid.uuid4().hex[:16]}",
            "expires_in": expires_in,
            "token_type": "bearer",
            "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp(),
            "user": cls.generate_supabase_user_dict(user_data)
        }
    
    @classmethod
    def generate_test_tokens(cls) -> Dict[str, str]:
        """Generate test tokens."""
        return {
            "access_token": f"access_token_{uuid.uuid4().hex[:16]}",
            "refresh_token": f"refresh_token_{uuid.uuid4().hex[:16]}",
            "verification_token": f"verify_{uuid.uuid4().hex[:12]}",
            "reset_token": f"reset_{uuid.uuid4().hex[:12]}"
        }
    
    @classmethod
    def generate_rate_limit_test_data(cls) -> Dict[str, Any]:
        """Generate data for rate limiting tests."""
        return {
            "ip_address": f"192.168.1.{random.randint(1, 254)}",
            "user_agent": "TestAgent/1.0",
            "endpoint": random.choice(["/auth/login", "/auth/register", "/auth/reset-password"]),
            "request_count": random.randint(1, 100),
            "time_window": random.randint(60, 3600)  # 1 minute to 1 hour
        }


class TestScenarios:
    """Pre-defined test scenarios for Auth testing."""
    
    @staticmethod
    def successful_registration_flow() -> Dict[str, Any]:
        """Generate data for successful registration flow."""
        user_data = TestDataGenerator.generate_user_data()
        return {
            "user_data": user_data,
            "expected_response": {
                "access_token": f"access_token_{uuid.uuid4().hex[:16]}",
                "refresh_token": f"refresh_token_{uuid.uuid4().hex[:16]}",
                "token_type": "bearer",
                "expires_in": 3600
            },
            "supabase_response": TestDataGenerator.generate_supabase_session_dict(user_data)
        }
    
    @staticmethod
    def failed_registration_scenarios() -> List[Dict[str, Any]]:
        """Generate data for failed registration scenarios."""
        scenarios = []
        
        # Email already exists
        existing_user = TestDataGenerator.generate_user_data()
        scenarios.append({
            "name": "email_already_exists",
            "user_data": existing_user,
            "error_type": "USER_ALREADY_EXISTS",
            "error_message": "User with this email already exists"
        })
        
        # Invalid email
        invalid_emails = TestDataGenerator.generate_invalid_emails()
        for email in invalid_emails[:3]:  # Test first 3 invalid emails
            scenarios.append({
                "name": "invalid_email",
                "user_data": TestUserData(
                    email=email,
                    password="ValidPassword123!",
                    username="testuser",
                    user_id=str(uuid.uuid4())
                ),
                "error_type": "VALIDATION_ERROR",
                "error_message": "Invalid email format"
            })
        
        # Weak passwords
        weak_passwords = TestDataGenerator.generate_weak_passwords()
        for password in weak_passwords[:3]:  # Test first 3 weak passwords
            scenarios.append({
                "name": "weak_password",
                "user_data": TestUserData(
                    email="test@test.com",
                    password=password,
                    username="testuser",
                    user_id=str(uuid.uuid4())
                ),
                "error_type": "WEAK_PASSWORD",
                "error_message": "Password does not meet security requirements"
            })
        
        return scenarios
    
    @staticmethod
    def authentication_flow_scenarios() -> List[Dict[str, Any]]:
        """Generate scenarios for authentication flows."""
        user_data = TestDataGenerator.generate_user_data()
        
        return [
            {
                "name": "successful_login",
                "user_data": user_data,
                "credentials": user_data.to_user_login(),
                "expected_success": True
            },
            {
                "name": "wrong_password",
                "user_data": user_data,
                "credentials": UserLogin(
                    email=user_data.email,
                    password="WrongPassword123!"
                ),
                "expected_success": False,
                "error_type": "INVALID_CREDENTIALS"
            },
            {
                "name": "non_existent_user",
                "user_data": None,
                "credentials": UserLogin(
                    email="nonexistent@test.com",
                    password="AnyPassword123!"
                ),
                "expected_success": False,
                "error_type": "USER_NOT_FOUND"
            }
        ]
