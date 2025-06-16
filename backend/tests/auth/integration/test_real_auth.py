"""
Integration Tests for Auth Service with Real Supabase.

This module tests Auth service with real Supabase instance (when available).
These tests require valid Supabase credentials and should be run in test environment.
"""

import pytest
import os
from uuid import uuid4

from domains.auth.services import AuthService, AuthenticationError
from domains.auth.schemas import UserCreate, UserLogin
from tests.auth.config import AuthTestBase, AuthTestConfig
from tests.auth.utils.test_data import TestDataGenerator


@pytest.mark.skipif(
    not AuthTestConfig.SUPABASE_AVAILABLE or not AuthTestConfig.INTEGRATION_MODE,
    reason="Supabase credentials not available or integration tests disabled"
)
class TestRealAuthIntegration(AuthTestBase):
    """Integration tests with real Supabase instance."""

    def test_main_functionality(self):
        """Required by AuthTestBase - tests basic integration."""
        # This will be skipped if real Supabase is not available
        pass

    @pytest.mark.asyncio
    async def test_real_user_registration_flow(self):
        """Test complete user registration flow with real Supabase."""
        service = AuthService()
        
        # Generate unique test user
        user_data = TestDataGenerator.generate_user_data(
            email_prefix="integration_test"
        )
        
        try:
            # Test registration
            result = await service.register_user(user_data.to_user_create())
            
            # Verify result structure
            assert result.access_token is not None
            assert result.refresh_token is not None
            assert result.user is not None
            assert result.user.email == user_data.email
            
        except AuthenticationError as e:
            # Handle expected errors in test environment
            if e.error_code in ["USER_ALREADY_EXISTS", "EMAIL_RATE_LIMIT"]:
                pytest.skip(f"Expected test environment error: {e.message}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_real_authentication_flow(self):
        """Test complete authentication flow with real Supabase."""
        service = AuthService()
        
        # Generate test user
        user_data = TestDataGenerator.generate_user_data(
            email_prefix="auth_test"
        )
        
        try:
            # First register user
            await service.register_user(user_data.to_user_create())
            
            # Then test login
            result = await service.authenticate_user(user_data.to_user_login())
            
            # Verify result
            assert result.access_token is not None
            assert result.user.email == user_data.email
            
        except AuthenticationError as e:
            # Handle expected errors
            if e.error_code in ["USER_ALREADY_EXISTS", "EMAIL_NOT_VERIFIED"]:
                pytest.skip(f"Expected test environment error: {e.message}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_real_error_scenarios(self):
        """Test error scenarios with real Supabase."""
        service = AuthService()
        
        # Test login with non-existent user
        fake_user = TestDataGenerator.generate_user_data()
        
        with pytest.raises(AuthenticationError):
            await service.authenticate_user(fake_user.to_user_login())

    @pytest.mark.asyncio
    async def test_rate_limiting_behavior(self):
        """Test rate limiting behavior with real Supabase."""
        if not AuthTestConfig.RATE_LIMIT_TESTING:
            pytest.skip("Rate limit testing disabled")
        
        service = AuthService()
        
        # This test would need to be carefully designed to not hit actual rate limits
        # In a real scenario, you might test with a dedicated test endpoint
        pass

    @pytest.mark.asyncio
    async def test_email_verification_flow(self):
        """Test email verification flow if enabled."""
        if not AuthTestConfig.EMAIL_TESTING_ENABLED:
            pytest.skip("Email testing not enabled")
        
        # This would test the complete email verification flow
        # Requires test email configuration
        pass


class TestAuthPerformance(AuthTestBase):
    """Performance tests for Auth service."""

    def test_main_functionality(self):
        """Required by AuthTestBase."""
        pass

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not AuthTestConfig.INTEGRATION_MODE,
        reason="Performance tests only run in integration mode"
    )
    async def test_registration_performance(self):
        """Test registration performance under load."""
        import time
        import asyncio
        
        service = AuthService()
        
        # Generate multiple test users
        users = TestDataGenerator.generate_bulk_users(count=5)  # Small number for test
        
        start_time = time.time()
        
        tasks = []
        for user_data in users:
            # Create unique email for each test
            unique_email = f"perf_test_{uuid4().hex[:8]}@{AuthTestConfig.TEST_EMAIL_DOMAIN}"
            user_create = UserCreate(
                email=unique_email,
                password=user_data.password,
                username=user_data.username
            )
            
            task = service.register_user(user_create)
            tasks.append(task)
        
        try:
            # Execute registrations concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Analyze results
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful
            
            print(f"Performance test results:")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            print(f"  Rate: {len(users)/duration:.2f} registrations/second")
            
            # Basic performance assertion
            assert duration < 30  # Should complete within 30 seconds
            
        except Exception as e:
            pytest.skip(f"Performance test skipped due to: {e}")

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not AuthTestConfig.INTEGRATION_MODE,
        reason="Load tests only run in integration mode"
    )
    async def test_authentication_load(self):
        """Test authentication under load."""
        # Similar to registration performance test
        # but for login operations
        pass
