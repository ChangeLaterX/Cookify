"""
Tests for /auth/refresh endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestRefreshEndpoint:
    """Test class for token refresh endpoint."""

    async def get_valid_token(self, async_client: AsyncClient, test_user_credentials):
        """Helper method to get valid tokens for testing."""
        login_response = await async_client.post("/auth/login", json=test_user_credentials)
        assert login_response.status_code == 200
        return login_response.json()["data"]

    @pytest.mark.asyncio
    async def test_refresh_valid_token_success(self, async_client: AsyncClient, test_user_credentials):
        """Test successful token refresh with valid refresh token."""
        # First login to get tokens
        tokens = await self.get_valid_token(async_client, test_user_credentials)
        
        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }

        response = await async_client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "expires_at" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        """Test token refresh with invalid refresh token."""
        refresh_data = {
            "refresh_token": "invalid_token_string"
        }

        response = await async_client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]

    @pytest.mark.asyncio
    async def test_refresh_expired_token(self, async_client: AsyncClient):
        """Test token refresh with expired refresh token."""
        # Use a known expired token format
        refresh_data = {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"
        }

        response = await async_client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]

    @pytest.mark.asyncio
    async def test_refresh_missing_token(self, async_client: AsyncClient):
        """Test token refresh with missing refresh token field."""
        refresh_data = {}

        response = await async_client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_refresh_empty_token(self, async_client: AsyncClient):
        """Test token refresh with empty refresh token."""
        refresh_data = {
            "refresh_token": ""
        }

        response = await async_client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_refresh_malformed_token(self, async_client: AsyncClient):
        """Test token refresh with malformed JWT token."""
        refresh_data = {
            "refresh_token": "not.a.jwt.token"
        }

        response = await async_client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_refresh_empty_body(self, async_client: AsyncClient):
        """Test token refresh with empty request body."""
        response = await async_client.post("/auth/refresh", json={})

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
