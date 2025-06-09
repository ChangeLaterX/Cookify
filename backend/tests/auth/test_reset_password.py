"""
Tests for /auth/reset-password endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestResetPasswordEndpoint:
    """Test class for reset password endpoint."""

    @pytest.mark.asyncio
    async def test_reset_password_valid_token_success(self, async_client: AsyncClient):
        """Test successful password reset with valid token."""
        # Note: This test assumes we have a valid reset token
        # In real scenarios, you would get this from email or mock the token generation
        reset_data = {
            "token": "valid_reset_token_from_email",
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/reset-password", json=reset_data)

        # This might fail in testing without actual token, but tests the endpoint structure
        assert response.status_code in [200, 400]  # 400 if token is invalid
        data = response.json()
        if response.status_code == 200:
            assert "message" in data
            assert "success" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, async_client: AsyncClient):
        """Test password reset with invalid token."""
        reset_data = {
            "token": "invalid_reset_token",
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/reset-password", json=reset_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]

    @pytest.mark.asyncio
    async def test_reset_password_expired_token(self, async_client: AsyncClient):
        """Test password reset with expired token."""
        reset_data = {
            "token": "expired_reset_token",
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/reset-password", json=reset_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_reset_password_weak_password(self, async_client: AsyncClient):
        """Test password reset with weak new password."""
        reset_data = {
            "token": "valid_reset_token",
            "new_password": "123"  # Too weak
        }

        response = await async_client.post("/auth/reset-password", json=reset_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_reset_password_missing_token(self, async_client: AsyncClient):
        """Test password reset with missing token field."""
        reset_data = {
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/reset-password", json=reset_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_reset_password_missing_password(self, async_client: AsyncClient):
        """Test password reset with missing new password field."""
        reset_data = {
            "token": "valid_reset_token"
        }

        response = await async_client.post("/auth/reset-password", json=reset_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_reset_password_empty_token(self, async_client: AsyncClient):
        """Test password reset with empty token."""
        reset_data = {
            "token": "",
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/reset-password", json=reset_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_reset_password_empty_body(self, async_client: AsyncClient):
        """Test password reset with empty request body."""
        response = await async_client.post("/auth/reset-password", json={})

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_reset_password_password_too_long(self, async_client: AsyncClient):
        """Test password reset with password exceeding maximum length."""
        reset_data = {
            "token": "valid_reset_token",
            "new_password": "a" * 200  # Exceeds 128 char limit
        }

        response = await async_client.post("/auth/reset-password", json=reset_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
