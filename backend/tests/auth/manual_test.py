"""
Manual test script for auth endpoints.
Run this when rate limiting is not active.
"""

import asyncio
import httpx
import json
from typing import Dict, Any


async def test_endpoint(client: httpx.AsyncClient, method: str, endpoint: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Test a single endpoint and return result."""
    try:
        if method.upper() == "GET":
            response = await client.get(endpoint, headers=headers)
        elif method.upper() == "POST":
            response = await client.post(endpoint, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = await client.put(endpoint, json=data, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            "success": 200 <= response.status_code < 300
        }
    except Exception as e:
        return {"error": str(e)}


async def main():
    """Main test function."""
    base_url = "http://dev.krija.info:8000/api"
    test_credentials = {
        "email": "krijajannis@gmail.com",
        "password": "221224"
    }
    
    async with httpx.AsyncClient(base_url=base_url) as client:
        print("🧪 Starting Auth Endpoint Tests\n")
        
        # Test 1: Health Check
        print("1. Testing /auth/health...")
        result = await test_endpoint(client, "GET", "/auth/health")
        print(f"   Status: {result.get('status_code', 'Error')}")
        print(f"   Success: {result.get('success', False)}")
        if result.get('error'):
            print(f"   Error: {result['error']}")
        print()
        
        # Test 2: Login with valid credentials
        print("2. Testing /auth/login (valid credentials)...")
        result = await test_endpoint(client, "POST", "/auth/login", test_credentials)
        print(f"   Status: {result.get('status_code', 'Error')}")
        print(f"   Success: {result.get('success', False)}")
        
        access_token = None
        refresh_token = None
        if result.get('success') and result.get('response'):
            response_data = result['response']
            if isinstance(response_data, dict) and 'data' in response_data:
                access_token = response_data['data'].get('access_token')
                refresh_token = response_data['data'].get('refresh_token')
                print(f"   Access token obtained: {'Yes' if access_token else 'No'}")
        print()
        
        # Test 3: Login with invalid credentials
        print("3. Testing /auth/login (invalid credentials)...")
        invalid_creds = {"email": "test@example.com", "password": "wrongpassword"}
        result = await test_endpoint(client, "POST", "/auth/login", invalid_creds)
        print(f"   Status: {result.get('status_code', 'Error')}")
        print(f"   Expected 401: {result.get('status_code') == 401}")
        print()
        
        # Test 4: Get current user (if we have token)
        if access_token:
            print("4. Testing /auth/me...")
            headers = {"Authorization": f"Bearer {access_token}"}
            result = await test_endpoint(client, "GET", "/auth/me", headers=headers)
            print(f"   Status: {result.get('status_code', 'Error')}")
            print(f"   Success: {result.get('success', False)}")
            print()
        
        # Test 5: Token refresh (if we have refresh token)
        if refresh_token:
            print("5. Testing /auth/refresh...")
            refresh_data = {"refresh_token": refresh_token}
            result = await test_endpoint(client, "POST", "/auth/refresh", refresh_data)
            print(f"   Status: {result.get('status_code', 'Error')}")
            print(f"   Success: {result.get('success', False)}")
            print()
        
        # Test 6: Password strength check
        print("6. Testing /auth/check-password-strength...")
        password_data = {"password": "TestPassword123!"}
        result = await test_endpoint(client, "POST", "/auth/check-password-strength", password_data)
        print(f"   Status: {result.get('status_code', 'Error')}")
        print(f"   Success: {result.get('success', False)}")
        print()
        
        # Test 7: Forgot password
        print("7. Testing /auth/forgot-password...")
        forgot_data = {"email": "test@example.com"}
        result = await test_endpoint(client, "POST", "/auth/forgot-password", forgot_data)
        print(f"   Status: {result.get('status_code', 'Error')}")
        print(f"   Success: {result.get('success', False)}")
        print()
        
        print("✅ Manual tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
