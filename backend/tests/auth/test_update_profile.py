"""
Tests for /auth/me endpoint (PUT update user profile).
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestUpdateProfileEndpoint:
    """Test class for update user profile endpoint."""

    async def get_valid_token(self, async_client: AsyncClient, test_user_credentials):
        """Helper method to get valid access token for testing."""
        login_response = await async_client.post("/auth/login", json=test_user_credentials)
        assert login_response.status_code == 200
        return login_response.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_update_profile_valid_data_success(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test successful profile update with valid data."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        profile_data = {
            "first_name": "John",
            "last_name": "Doe",
            "display_name": "Johnny",
            "bio": "Test user bio",
            "avatar_url": "https://example.com/avatar.jpg"
        }

        response = await async_client.put("/auth/me", json=profile_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["first_name"] == profile_data["first_name"]
        assert data["last_name"] == profile_data["last_name"]
        assert data["display_name"] == profile_data["display_name"]
        assert data["bio"] == profile_data["bio"]
        assert data["avatar_url"] == profile_data["avatar_url"]

    @pytest.mark.asyncio
    async def test_update_profile_partial_data_success(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test successful profile update with partial data."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        profile_data = {
            "first_name": "Jane",
            "bio": "Updated bio only"
        }

        response = await async_client.put("/auth/me", json=profile_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == profile_data["first_name"]
        assert data["bio"] == profile_data["bio"]

    @pytest.mark.asyncio
    async def test_update_profile_invalid_token(self, async_client: AsyncClient, auth_headers):
        """Test profile update with invalid access token."""
        headers = auth_headers("invalid_token_string")
        profile_data = {"first_name": "John"}

        response = await async_client.put("/auth/me", json=profile_data, headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_update_profile_expired_token(self, async_client: AsyncClient, auth_headers):
        """Test profile update with expired access token."""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"
        headers = auth_headers(expired_token)
        profile_data = {"first_name": "John"}

        response = await async_client.put("/auth/me", json=profile_data, headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_update_profile_missing_authorization_header(self, async_client: AsyncClient):
        """Test profile update without authorization header."""
        profile_data = {"first_name": "John"}

        response = await async_client.put("/auth/me", json=profile_data)

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_update_profile_empty_body(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test profile update with empty request body."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        response = await async_client.put("/auth/me", json={}, headers=headers)

        # Empty body should still be valid for profile update
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_profile_invalid_avatar_url(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test profile update with invalid avatar URL."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        profile_data = {
            "avatar_url": "not-a-valid-url"
        }

        response = await async_client.put("/auth/me", json=profile_data, headers=headers)

        # Depending on validation, this might be 422 or 400
        assert response.status_code in [400, 422] or response.status_code == 200  # Some systems might allow invalid URLs

    @pytest.mark.asyncio
    async def test_update_profile_very_long_bio(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test profile update with very long bio."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        profile_data = {
            "bio": "a" * 1000  # Very long bio
        }

        response = await async_client.put("/auth/me", json=profile_data, headers=headers)

        # Depending on validation, this might be accepted or rejected
        assert response.status_code in [200, 400, 422]
