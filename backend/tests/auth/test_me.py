"""
Tests for /auth/me endpoint (GET current user info).
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestMeEndpoint:
    """Test class for get current user endpoint."""

    async def get_valid_token(self, async_client: AsyncClient, test_user_credentials):
        """Helper method to get valid access token for testing."""
        login_response = await async_client.post("/auth/login", json=test_user_credentials)
        assert login_response.status_code == 200
        return login_response.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_get_me_valid_token_success(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test successful retrieval of current user info with valid token."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        response = await async_client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "id" in data["user"]
        assert "email" in data["user"]
        assert data["user"]["email"] == test_user_credentials["email"]
        assert "is_active" in data["user"]
        assert "is_verified" in data["user"]
        assert "created_at" in data["user"]
        assert "updated_at" in data["user"]

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, async_client: AsyncClient, auth_headers):
        """Test get current user with invalid access token."""
        headers = auth_headers("invalid_token_string")

        response = await async_client.get("/auth/me", headers=headers)

        assert response.status_code in [401, 403]
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_me_expired_token(self, async_client: AsyncClient, auth_headers):
        """Test get current user with expired access token."""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"
        headers = auth_headers(expired_token)

        response = await async_client.get("/auth/me", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_me_missing_authorization_header(self, async_client: AsyncClient):
        """Test get current user without authorization header."""
        response = await async_client.get("/auth/me")

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_me_malformed_authorization_header(self, async_client: AsyncClient):
        """Test get current user with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat token"}

        response = await async_client.get("/auth/me", headers=headers)

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_me_empty_token(self, async_client: AsyncClient):
        """Test get current user with empty bearer token."""
        headers = {"Authorization": "Bearer "}

        response = await async_client.get("/auth/me", headers=headers)

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_me_profile_data(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test that user profile data is included if available."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        response = await async_client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        # Profile might be None if not set up yet
        assert "profile" in data
