"""
Tests for /auth/login endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestLoginEndpoint:
    """Test class for user login endpoint."""

    @pytest.mark.asyncio
    async def test_login_valid_credentials_success(self, async_client: AsyncClient, test_user_credentials):
        """Test successful login with valid credentials."""
        response = await async_client.post("/auth/login", json=test_user_credentials)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Login successful"
        assert "data" in data
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "expires_in" in data["data"]
        assert "expires_at" in data["data"]

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, async_client: AsyncClient):
        """Test login with non-existent email."""
        credentials = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }

        response = await async_client.post("/auth/login", json=credentials)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, async_client: AsyncClient, test_user_credentials):
        """Test login with correct email but wrong password."""
        credentials = {
            "email": test_user_credentials["email"],
            "password": "wrong_password"
        }

        response = await async_client.post("/auth/login", json=credentials)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]

    @pytest.mark.asyncio
    async def test_login_malformed_email(self, async_client: AsyncClient):
        """Test login with malformed email address."""
        credentials = {
            "email": "not-an-email",
            "password": "SomePassword123!"
        }

        response = await async_client.post("/auth/login", json=credentials)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_missing_email(self, async_client: AsyncClient):
        """Test login with missing email field."""
        credentials = {
            "password": "SomePassword123!"
        }

        response = await async_client.post("/auth/login", json=credentials)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_missing_password(self, async_client: AsyncClient):
        """Test login with missing password field."""
        credentials = {
            "email": "test@example.com"
        }

        response = await async_client.post("/auth/login", json=credentials)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_empty_body(self, async_client: AsyncClient):
        """Test login with empty request body."""
        response = await async_client.post("/auth/login", json={})

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_password_too_short(self, async_client: AsyncClient):
        """Test login with password below minimum length."""
        credentials = {
            "email": "test@example.com",
            "password": "123"  # Below minimum 6 characters
        }

        response = await async_client.post("/auth/login", json=credentials)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_password_too_long(self, async_client: AsyncClient):
        """Test login with password exceeding maximum length."""
        credentials = {
            "email": "test@example.com",
            "password": "a" * 200  # Exceeds 128 char limit
        }

        response = await async_client.post("/auth/login", json=credentials)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
