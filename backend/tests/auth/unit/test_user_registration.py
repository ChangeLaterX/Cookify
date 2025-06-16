"""
Unit Tests for User Registration Functionality.

This module tests user registration logic in the Auth service.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from domains.auth.services import AuthService, AuthenticationError
from domains.auth.schemas import UserCreate, TokenResponse
from tests.auth.config import AuthTestBase
from tests.auth.utils.mocks import AuthMockFactory, MockContextManager, with_mocked_auth
from tests.auth.utils.test_data import TestDataGenerator, TestScenarios


class TestUserRegistration(AuthTestBase):
    """Test user registration functionality."""

    def test_main_functionality(self):
        """Required by AuthTestBase - tests basic registration."""
        self.test_successful_user_registration()

    @pytest.mark.asyncio
    async def test_successful_user_registration(self):
        """Test successful user registration flow."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock successful Supabase response
            mock_response = AuthMockFactory.create_supabase_response(
                success=True,
                user_data=TestDataGenerator.generate_supabase_user_dict(user_data)
            )
            service.supabase.auth.sign_up.return_value = mock_response
            
            # Test registration
            result = await service.register_user(user_data.to_user_create())
            
            # Verify result
            assert isinstance(result, TokenResponse)
            assert result.access_token is not None
            assert result.refresh_token is not None
            assert result.token_type == "bearer"
            assert result.expires_in > 0
            assert result.user is not None

    @pytest.mark.asyncio
    async def test_registration_with_existing_email(self):
        """Test registration fails when email already exists."""
        with MockContextManager(success_responses=False) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock Supabase auth error for existing user
            auth_error = AuthMockFactory.create_auth_error("User already exists", 400)
            service.supabase.auth.sign_up.side_effect = auth_error
            
            # Test registration should fail
            with pytest.raises(AuthenticationError) as exc_info:
                await service.register_user(user_data.to_user_create())
            
            assert exc_info.value.error_code == "REGISTRATION_FAILED"

    @pytest.mark.asyncio
    async def test_registration_with_invalid_email(self):
        """Test registration with invalid email addresses."""
        invalid_emails = TestDataGenerator.generate_invalid_emails()
        
        for invalid_email in invalid_emails[:3]:  # Test first 3 invalid emails
            with pytest.raises(Exception):  # Should fail validation
                UserCreate(
                    email=invalid_email,
                    password="ValidPassword123!",
                    username="testuser"
                )

    @pytest.mark.asyncio
    async def test_registration_with_weak_passwords(self):
        """Test registration with weak passwords."""
        weak_passwords = TestDataGenerator.generate_weak_passwords()
        
        for weak_password in weak_passwords[:3]:  # Test first 3 weak passwords
            with pytest.raises(Exception):  # Should fail validation
                UserCreate(
                    email="test@example.com",
                    password=weak_password,
                    username="testuser"
                )

    @pytest.mark.asyncio
    async def test_registration_supabase_response_parsing(self):
        """Test parsing of Supabase registration response."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Create detailed mock response
            supabase_user = TestDataGenerator.generate_supabase_user_dict(user_data)
            supabase_session = TestDataGenerator.generate_supabase_session_dict(user_data)
            
            mock_response = AuthMockFactory.create_supabase_response(
                success=True,
                user_data=supabase_user,
                session_data=supabase_session
            )
            service.supabase.auth.sign_up.return_value = mock_response
            
            # Test registration
            result = await service.register_user(user_data.to_user_create())
            
            # Verify response parsing
            assert result.user.email == user_data.email
            assert result.user.username == user_data.username

    @pytest.mark.asyncio
    async def test_registration_without_username(self):
        """Test registration without providing username."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            
            # Create user data without username
            user_create = UserCreate(
                email="test@example.com",
                password="ValidPassword123!"
                # username is optional
            )
            
            mock_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.sign_up.return_value = mock_response
            
            # Should succeed even without username
            result = await service.register_user(user_create)
            assert isinstance(result, TokenResponse)

    @pytest.mark.asyncio
    async def test_registration_supabase_user_creation_failed(self):
        """Test registration when Supabase user creation fails."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock response with no user created
            mock_response = MagicMock()
            mock_response.user = None
            mock_response.session = None
            service.supabase.auth.sign_up.return_value = mock_response
            
            # Test registration should fail
            with pytest.raises(AuthenticationError) as exc_info:
                await service.register_user(user_data.to_user_create())
            
            assert exc_info.value.error_code == "USER_CREATION_FAILED"

    @pytest.mark.asyncio
    async def test_registration_logging(self):
        """Test that registration attempts are properly logged."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock logger to capture calls
            mock_logger = MagicMock()
            service.logger = mock_logger
            
            mock_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.sign_up.return_value = mock_response
            
            # Test registration
            await service.register_user(user_data.to_user_create())
            
            # Verify logging occurred
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_registration_profile_creation(self):
        """Test that user profile is created during registration."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock successful registration
            mock_response = AuthMockFactory.create_supabase_response(
                success=True,
                user_data=TestDataGenerator.generate_supabase_user_dict(user_data)
            )
            service.supabase.auth.sign_up.return_value = mock_response
            
            # Mock profile table operations
            mock_table = MagicMock()
            mock_table.insert.return_value.execute.return_value = MagicMock(error=None)
            service.supabase.table.return_value = mock_table
            
            # Test registration
            result = await service.register_user(user_data.to_user_create())
            
            # Verify profile creation was attempted
            service.supabase.table.assert_called_with('user_profiles')

    @pytest.mark.asyncio
    async def test_multiple_registration_scenarios(self):
        """Test multiple registration scenarios from TestScenarios."""
        scenarios = TestScenarios.failed_registration_scenarios()
        
        for scenario in scenarios[:2]:  # Test first 2 scenarios
            if scenario["name"] == "email_already_exists":
                with MockContextManager(success_responses=False) as mock_ctx:
                    service = AuthService()
                    
                    # Mock existing user error
                    auth_error = AuthMockFactory.create_auth_error(scenario["error_message"])
                    service.supabase.auth.sign_up.side_effect = auth_error
                    
                    with pytest.raises(AuthenticationError):
                        await service.register_user(scenario["user_data"].to_user_create())
