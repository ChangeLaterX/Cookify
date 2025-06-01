"""
Test script for rate limiting functionality.
This script tests the rate limiting middleware by making multiple requests to authentication endpoints.
"""
import asyncio
import aiohttp
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_ENDPOINTS = [
    "/api/auth/login",
    "/api/auth/register", 
    "/api/auth/forgot-password"
]

async def test_rate_limiting():
    """Test rate limiting for authentication endpoints."""
    print("🚀 Starting Rate Limiting Tests")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for endpoint in AUTH_ENDPOINTS:
            print(f"\n📍 Testing endpoint: {endpoint}")
            await test_endpoint_rate_limit(session, endpoint)
    
    print("\n✅ Rate limiting tests completed!")

async def test_endpoint_rate_limit(session: aiohttp.ClientSession, endpoint: str):
    """Test rate limiting for a specific endpoint."""
    url = f"{BASE_URL}{endpoint}"
    
    # Test data for different endpoints
    test_data = {
        "/api/auth/login": {"email": "test@example.com", "password": "testpassword"},
        "/api/auth/register": {"email": "test@example.com", "password": "testpassword"},
        "/api/auth/forgot-password": {"email": "test@example.com"}
    }
    
    data = test_data.get(endpoint, {"email": "test@example.com"})
    
    success_count = 0
    rate_limited_count = 0
    
    print(f"  Making rapid requests to test rate limiting...")
    
    # Make 10 rapid requests
    for i in range(10):
        try:
            async with session.post(url, json=data) as response:
                if response.status == 429:
                    rate_limited_count += 1
                    retry_after = response.headers.get("Retry-After", "unknown")
                    print(f"  ⚠️  Request {i+1}: Rate limited (HTTP 429) - Retry-After: {retry_after}s")
                    
                    # Parse the response to see rate limit details
                    try:
                        response_data = await response.json()
                        print(f"      Error: {response_data.get('error', 'Unknown')}")
                        print(f"      Details: {response_data.get('details', {})}")
                    except:
                        pass
                        
                elif response.status in [400, 401, 422]:
                    # Expected authentication/validation errors
                    success_count += 1
                    print(f"  ✅ Request {i+1}: Accepted (HTTP {response.status})")
                else:
                    success_count += 1
                    print(f"  ✅ Request {i+1}: Success (HTTP {response.status})")
                    
        except Exception as e:
            print(f"  ❌ Request {i+1}: Error - {str(e)}")
        
        # Small delay between requests
        await asyncio.sleep(0.1)
    
    print(f"  📊 Results: {success_count} successful, {rate_limited_count} rate limited")
    
    if rate_limited_count > 0:
        print(f"  ✅ Rate limiting is working! Blocked {rate_limited_count} requests")
    else:
        print(f"  ⚠️  No rate limiting detected - check configuration")

async def test_progressive_delay():
    """Test progressive delay functionality."""
    print(f"\n🔄 Testing Progressive Delay")
    print("-" * 30)
    
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/api/auth/login"
        data = {"email": "brute@force.test", "password": "wrong"}
        
        # Make several attempts to trigger progressive delay
        for attempt in range(8):
            try:
                start_time = time.time()
                async with session.post(url, json=data) as response:
                    end_time = time.time()
                    
                    if response.status == 429:
                        retry_after = response.headers.get("Retry-After", "0")
                        print(f"  Attempt {attempt+1}: Rate limited - Retry-After: {retry_after}s")
                        
                        # Wait for the retry after period to test progressive increase
                        if int(retry_after) > 0:
                            print(f"  Waiting {retry_after}s before next attempt...")
                            await asyncio.sleep(int(retry_after) + 1)
                    else:
                        print(f"  Attempt {attempt+1}: Request allowed (HTTP {response.status})")
                        
            except Exception as e:
                print(f"  Attempt {attempt+1}: Error - {str(e)}")
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    print("Rate Limiting Test Suite")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    try:
        asyncio.run(test_rate_limiting())
        asyncio.run(test_progressive_delay())
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
