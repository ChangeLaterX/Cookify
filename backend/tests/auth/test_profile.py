"""
Tests for /auth/profile endpoint (GET user profile).
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestProfileEndpoint:
    """Test class for get user profile endpoint."""

    async def get_valid_token(self, async_client: AsyncClient, test_user_credentials):
        """Helper method to get valid access token for testing."""
        login_response = await async_client.post("/auth/login", json=test_user_credentials)
        assert login_response.status_code == 200
        return login_response.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_get_profile_valid_token_success(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test successful retrieval of user profile with valid token."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        response = await async_client.get("/auth/profile", headers=headers)

        assert response.status_code == 200
        # Profile might be null if user hasn't set up profile yet
        data = response.json()
        if data is not None:
            # If profile exists, check structure
            assert "user_id" in data
            assert "first_name" in data
            assert "last_name" in data
            assert "display_name" in data
            assert "bio" in data
            assert "avatar_url" in data
            assert "created_at" in data
            assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_get_profile_invalid_token(self, async_client: AsyncClient, auth_headers):
        """Test get profile with invalid access token."""
        headers = auth_headers("invalid_token_string")

        response = await async_client.get("/auth/profile", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_profile_expired_token(self, async_client: AsyncClient, auth_headers):
        """Test get profile with expired access token."""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"
        headers = auth_headers(expired_token)

        response = await async_client.get("/auth/profile", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_profile_missing_authorization_header(self, async_client: AsyncClient):
        """Test get profile without authorization header."""
        response = await async_client.get("/auth/profile")

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_profile_malformed_authorization_header(self, async_client: AsyncClient):
        """Test get profile with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat token"}

        response = await async_client.get("/auth/profile", headers=headers)

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_profile_empty_token(self, async_client: AsyncClient):
        """Test get profile with empty bearer token."""
        headers = {"Authorization": "Bearer "}

        response = await async_client.get("/auth/profile", headers=headers)

        assert response.status_code in [401, 403, 422]
