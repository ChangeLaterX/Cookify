"""
Tests for /auth/forgot-password endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestForgotPasswordEndpoint:
    """Test class for forgot password endpoint."""

    @pytest.mark.asyncio
    async def test_forgot_password_valid_email_success(self, async_client: AsyncClient, test_user_credentials):
        """Test successful password reset request with valid email."""
        reset_data = {
            "email": test_user_credentials["email"]
        }

        response = await async_client.post("/auth/forgot-password", json=reset_data)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "password reset link" in data["message"].lower()
        assert data.get("success", True) is True

    @pytest.mark.asyncio
    async def test_forgot_password_nonexistent_email(self, async_client: AsyncClient):
        """Test password reset request with non-existent email."""
        reset_data = {
            "email": "nonexistent@example.com"
        }

        response = await async_client.post("/auth/forgot-password", json=reset_data)

        # For security reasons, should return success even for non-existent emails
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "password reset link" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_forgot_password_invalid_email_format(self, async_client: AsyncClient):
        """Test password reset request with invalid email format."""
        reset_data = {
            "email": "not-an-email"
        }

        response = await async_client.post("/auth/forgot-password", json=reset_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_forgot_password_missing_email(self, async_client: AsyncClient):
        """Test password reset request with missing email field."""
        reset_data = {}

        response = await async_client.post("/auth/forgot-password", json=reset_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_forgot_password_empty_email(self, async_client: AsyncClient):
        """Test password reset request with empty email."""
        reset_data = {
            "email": ""
        }

        response = await async_client.post("/auth/forgot-password", json=reset_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_forgot_password_empty_body(self, async_client: AsyncClient):
        """Test password reset request with empty request body."""
        response = await async_client.post("/auth/forgot-password", json={})

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_forgot_password_multiple_requests(self, async_client: AsyncClient, test_user_credentials):
        """Test multiple password reset requests for same email."""
        reset_data = {
            "email": test_user_credentials["email"]
        }

        # First request
        response1 = await async_client.post("/auth/forgot-password", json=reset_data)
        assert response1.status_code == 200

        # Second request immediately after
        response2 = await async_client.post("/auth/forgot-password", json=reset_data)
        assert response2.status_code == 200

        # Both should succeed (rate limiting might be handled elsewhere)
