"""
Tests for /auth/resend-verification endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestResendVerificationEndpoint:
    """Test class for resend verification email endpoint."""

    @pytest.mark.asyncio
    async def test_resend_verification_valid_email_success(self, async_client: AsyncClient, test_user_credentials):
        """Test successful resend verification email with valid email."""
        resend_data = {
            "email": test_user_credentials["email"]
        }

        response = await async_client.post("/auth/resend-verification", json=resend_data)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "verification link" in data["message"].lower()
        assert data.get("success", True) is True

    @pytest.mark.asyncio
    async def test_resend_verification_nonexistent_email(self, async_client: AsyncClient):
        """Test resend verification with non-existent email."""
        resend_data = {
            "email": "nonexistent@example.com"
        }

        response = await async_client.post("/auth/resend-verification", json=resend_data)

        # For security reasons, should return success even for non-existent emails
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "verification link" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_resend_verification_invalid_email_format(self, async_client: AsyncClient):
        """Test resend verification with invalid email format."""
        resend_data = {
            "email": "not-an-email"
        }

        response = await async_client.post("/auth/resend-verification", json=resend_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_resend_verification_missing_email(self, async_client: AsyncClient):
        """Test resend verification with missing email field."""
        resend_data = {}

        response = await async_client.post("/auth/resend-verification", json=resend_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_resend_verification_empty_email(self, async_client: AsyncClient):
        """Test resend verification with empty email."""
        resend_data = {
            "email": ""
        }

        response = await async_client.post("/auth/resend-verification", json=resend_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_resend_verification_empty_body(self, async_client: AsyncClient):
        """Test resend verification with empty request body."""
        response = await async_client.post("/auth/resend-verification", json={})

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_resend_verification_multiple_requests(self, async_client: AsyncClient, test_user_credentials):
        """Test multiple resend verification requests for same email."""
        resend_data = {
            "email": test_user_credentials["email"]
        }

        # First request
        response1 = await async_client.post("/auth/resend-verification", json=resend_data)
        assert response1.status_code == 200

        # Second request immediately after
        response2 = await async_client.post("/auth/resend-verification", json=resend_data)
        assert response2.status_code == 200

        # Both should succeed (rate limiting might be handled elsewhere)

    @pytest.mark.asyncio
    async def test_resend_verification_already_verified_email(self, async_client: AsyncClient):
        """Test resend verification for already verified email."""
        # This would depend on your system - some systems might not send
        # verification emails for already verified accounts
        resend_data = {
            "email": "already.verified@example.com"
        }

        response = await async_client.post("/auth/resend-verification", json=resend_data)

        # Should still return success for security reasons
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
