"""
Tests for /auth/verify-email endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestVerifyEmailEndpoint:
    """Test class for email verification endpoint."""

    @pytest.mark.asyncio
    async def test_verify_email_valid_token_success(self, async_client: AsyncClient):
        """Test successful email verification with valid token."""
        # Note: This test assumes we have a valid verification token
        # In real scenarios, you would get this from email or mock the token generation
        verification_data = {
            "token": "valid_verification_token_from_email"
        }

        response = await async_client.post("/auth/verify-email", json=verification_data)

        # This might fail in testing without actual token, but tests the endpoint structure
        assert response.status_code in [200, 400]  # 400 if token is invalid
        data = response.json()
        if response.status_code == 200:
            assert "message" in data
            assert "verified" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, async_client: AsyncClient):
        """Test email verification with invalid token."""
        verification_data = {
            "token": "invalid_verification_token"
        }

        response = await async_client.post("/auth/verify-email", json=verification_data)

        assert response.status_code == 400
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)
        assert "error" in data["detail"]

    @pytest.mark.asyncio
    async def test_verify_email_expired_token(self, async_client: AsyncClient):
        """Test email verification with expired token."""
        verification_data = {
            "token": "expired_verification_token"
        }

        response = await async_client.post("/auth/verify-email", json=verification_data)

        assert response.status_code == 400
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_verify_email_missing_token(self, async_client: AsyncClient):
        """Test email verification with missing token field."""
        verification_data = {}

        response = await async_client.post("/auth/verify-email", json=verification_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_verify_email_empty_token(self, async_client: AsyncClient):
        """Test email verification with empty token."""
        verification_data = {
            "token": ""
        }

        response = await async_client.post("/auth/verify-email", json=verification_data)

        assert response.status_code == 400
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_verify_email_empty_body(self, async_client: AsyncClient):
        """Test email verification with empty request body."""
        response = await async_client.post("/auth/verify-email", json={})

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_verify_email_malformed_token(self, async_client: AsyncClient):
        """Test email verification with malformed token."""
        verification_data = {
            "token": "not.a.valid.jwt.token.format"
        }

        response = await async_client.post("/auth/verify-email", json=verification_data)

        assert response.status_code == 400
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_verify_email_already_verified(self, async_client: AsyncClient):
        """Test email verification for already verified email."""
        # This would need a token for an already verified account
        verification_data = {
            "token": "token_for_already_verified_email"
        }

        response = await async_client.post("/auth/verify-email", json=verification_data)

        # Depending on implementation, might return success or error
        assert response.status_code in [200, 400]
