"""
Debug test to check rate limiting behavior.
"""

import pytest
import asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_debug_rate_limiting():
    """Debug test to check if rate limiting is working."""
    base_url = "http://dev.krija.info:8000/api"
    
    async with AsyncClient(base_url=base_url) as client:
        # Test health endpoint first
        health_response = await client.get("/auth/health")
        print(f"Health status: {health_response.status_code}")
        print(f"Health response: {health_response.json()}")
        
        # Test login with wrong credentials (should not be rate limited)
        credentials = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        for i in range(3):
            response = await client.post("/auth/login", json=credentials)
            print(f"Request {i+1}: Status {response.status_code}")
            if response.status_code == 429:
                print(f"Rate limited! Response: {response.text}")
            else:
                data = response.json()
                print(f"Response: {data}")
            
            # Small delay between requests
            await asyncio.sleep(0.5)
