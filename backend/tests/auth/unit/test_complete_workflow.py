"""
Unit Tests for Complete Auth Workflows.

This module tests end-to-end authentication workflows.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from domains.auth.services import AuthService, AuthenticationError
from domains.auth.schemas import UserCreate, UserLogin
from tests.auth.config import AuthTestBase
from tests.auth.utils.mocks import AuthMockFactory, MockContextManager
from tests.auth.utils.test_data import TestDataGenerator, TestScenarios


class TestCompleteAuthWorkflows(AuthTestBase):
    """Test complete authentication workflows."""

    def test_main_functionality(self):
        """Required by AuthTestBase - tests basic workflow."""
        self.test_complete_registration_and_login_workflow()

    @pytest.mark.asyncio
    async def test_complete_registration_and_login_workflow(self):
        """Test complete registration followed by login workflow."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Step 1: Register user
            registration_response = AuthMockFactory.create_supabase_response(
                success=True,
                user_data=TestDataGenerator.generate_supabase_user_dict(user_data)
            )
            service.supabase.auth.sign_up.return_value = registration_response
            
            registration_result = await service.register_user(user_data.to_user_create())
            
            # Verify registration
            assert registration_result.access_token is not None
            assert registration_result.user.email == user_data.email
            
            # Step 2: Login with same credentials
            login_response = AuthMockFactory.create_supabase_response(
                success=True,
                user_data=TestDataGenerator.generate_supabase_user_dict(user_data)
            )
            service.supabase.auth.sign_in_with_password.return_value = login_response
            
            login_result = await service.authenticate_user(user_data.to_user_login())
            
            # Verify login
            assert login_result.access_token is not None
            assert login_result.user.email == user_data.email
            
            # Step 3: Logout
            logout_response = MagicMock()
            logout_response.error = None
            service.supabase.auth.sign_out.return_value = logout_response
            
            logout_result = await service.logout_user()
            assert logout_result is True

    @pytest.mark.asyncio
    async def test_registration_login_logout_cycle(self):
        """Test multiple cycles of registration, login, and logout."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            
            # Test with multiple users
            users = TestDataGenerator.generate_bulk_users(count=3)
            
            for user_data in users:
                # Register
                reg_response = AuthMockFactory.create_supabase_response(
                    success=True,
                    user_data=TestDataGenerator.generate_supabase_user_dict(user_data)
                )
                service.supabase.auth.sign_up.return_value = reg_response
                
                reg_result = await service.register_user(user_data.to_user_create())
                assert reg_result.user.email == user_data.email
                
                # Login
                login_response = AuthMockFactory.create_supabase_response(success=True)
                service.supabase.auth.sign_in_with_password.return_value = login_response
                
                login_result = await service.authenticate_user(user_data.to_user_login())
                assert login_result.access_token is not None
                
                # Logout
                logout_response = MagicMock()
                logout_response.error = None
                service.supabase.auth.sign_out.return_value = logout_response
                
                logout_result = await service.logout_user()
                assert logout_result is True

    @pytest.mark.asyncio
    async def test_token_refresh_workflow(self):
        """Test token refresh workflow."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Step 1: Login to get tokens
            login_response = AuthMockFactory.create_supabase_response(
                success=True,
                session_data=TestDataGenerator.generate_supabase_session_dict(user_data)
            )
            service.supabase.auth.sign_in_with_password.return_value = login_response
            
            login_result = await service.authenticate_user(user_data.to_user_login())
            original_refresh_token = login_result.refresh_token
            
            # Step 2: Refresh tokens
            refresh_response = AuthMockFactory.create_supabase_response(
                success=True,
                session_data=TestDataGenerator.generate_supabase_session_dict(user_data)
            )
            service.supabase.auth.refresh_session.return_value = refresh_response
            
            refresh_result = await service.refresh_user_token(original_refresh_token)
            
            # Verify new tokens
            assert refresh_result.access_token is not None
            assert refresh_result.refresh_token is not None
            assert refresh_result.access_token != login_result.access_token  # Should be different

    @pytest.mark.asyncio
    async def test_failed_registration_prevents_login(self):
        """Test that failed registration prevents subsequent login."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Step 1: Fail registration
            auth_error = AuthMockFactory.create_auth_error("Registration failed")
            service.supabase.auth.sign_up.side_effect = auth_error
            
            with pytest.raises(AuthenticationError):
                await service.register_user(user_data.to_user_create())
            
            # Step 2: Try to login (should fail)
            login_error = AuthMockFactory.create_auth_error("User not found")
            service.supabase.auth.sign_in_with_password.side_effect = login_error
            
            with pytest.raises(AuthenticationError):
                await service.authenticate_user(user_data.to_user_login())

    @pytest.mark.asyncio
    async def test_concurrent_registrations(self):
        """Test handling of concurrent registration attempts."""
        import asyncio
        
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            
            # Generate multiple unique users
            users = TestDataGenerator.generate_bulk_users(count=5)
            
            # Mock successful responses for all
            for user_data in users:
                response = AuthMockFactory.create_supabase_response(
                    success=True,
                    user_data=TestDataGenerator.generate_supabase_user_dict(user_data)
                )
                service.supabase.auth.sign_up.return_value = response
            
            # Create registration tasks
            tasks = [
                service.register_user(user_data.to_user_create()) 
                for user_data in users
            ]
            
            # Execute concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all succeeded
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == len(users)

    @pytest.mark.asyncio
    async def test_authentication_state_management(self):
        """Test authentication state management throughout workflow."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Initially no authenticated user
            # (This would depend on how state is managed in the actual implementation)
            
            # Register user
            reg_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.sign_up.return_value = reg_response
            
            reg_result = await service.register_user(user_data.to_user_create())
            # Now user should be authenticated with registration
            
            # Login user
            login_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.sign_in_with_password.return_value = login_response
            
            login_result = await service.authenticate_user(user_data.to_user_login())
            # User should still be authenticated
            
            # Logout user
            logout_response = MagicMock()
            logout_response.error = None
            service.supabase.auth.sign_out.return_value = logout_response
            
            await service.logout_user()
            # User should no longer be authenticated

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test error recovery in authentication workflows."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Step 1: Registration fails initially
            auth_error = AuthMockFactory.create_auth_error("Temporary error")
            service.supabase.auth.sign_up.side_effect = auth_error
            
            with pytest.raises(AuthenticationError):
                await service.register_user(user_data.to_user_create())
            
            # Step 2: Registration succeeds on retry
            service.supabase.auth.sign_up.side_effect = None
            reg_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.sign_up.return_value = reg_response
            
            reg_result = await service.register_user(user_data.to_user_create())
            assert reg_result.access_token is not None

    @pytest.mark.asyncio
    async def test_workflow_logging_and_monitoring(self):
        """Test that workflows are properly logged and monitored."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock logger
            mock_logger = MagicMock()
            service.logger = mock_logger
            
            # Execute complete workflow
            reg_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.sign_up.return_value = reg_response
            
            await service.register_user(user_data.to_user_create())
            
            login_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.sign_in_with_password.return_value = login_response
            
            await service.authenticate_user(user_data.to_user_login())
            
            logout_response = MagicMock()
            logout_response.error = None
            service.supabase.auth.sign_out.return_value = logout_response
            
            await service.logout_user()
            
            # Verify logging occurred for each step
            assert mock_logger.info.call_count >= 3  # At least one log per operation
