"""
Integration test for Security Headers Middleware.
Tests the actual working security headers implementation.
"""
import requests
import subprocess
import time
import signal
import os
from typing import Dict, Any

# Test configuration
TEST_HOST = "localhost"
TEST_PORT = 8003
BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"

class SecurityHeadersIntegrationTest:
    """Integration test for security headers using real HTTP requests."""
    
    def __init__(self):
        self.server_process = None
    
    def start_server(self):
        """Start the FastAPI server for testing."""
        cmd = [
            "python", "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", str(TEST_PORT)
        ]
        
        self.server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/Users/jannis/Developer/Cookify/backend"
        )
        
        # Wait for server to start
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{BASE_URL}/", timeout=1)
                if response.status_code == 200:
                    print(f"✅ Server started successfully on {BASE_URL}")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(1)
        
        print("❌ Failed to start server")
        return False
    
    def stop_server(self):
        """Stop the test server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")
    
    def test_basic_security_headers(self) -> Dict[str, Any]:
        """Test basic security headers from Issue 2."""
        response = requests.get(f"{BASE_URL}/")
        headers = response.headers
        
        required_headers = {
            'x-content-type-options': 'nosniff',
            'x-frame-options': 'DENY',
            'x-xss-protection': '1; mode=block',
            'content-security-policy': None,  # Check existence, not exact value
        }
        
        results = {}
        for header, expected_value in required_headers.items():
            if header in headers:
                actual_value = headers[header]
                if expected_value is None or actual_value == expected_value:
                    results[header] = {"status": "✅ PASS", "value": actual_value}
                else:
                    results[header] = {"status": "❌ FAIL", "expected": expected_value, "actual": actual_value}
            else:
                results[header] = {"status": "❌ MISSING"}
        
        return results
    
    def test_additional_security_headers(self) -> Dict[str, Any]:
        """Test additional security headers."""
        response = requests.get(f"{BASE_URL}/")
        headers = response.headers
        
        additional_headers = [
            'referrer-policy',
            'permissions-policy',
            'x-permitted-cross-domain-policies',
            'cross-origin-embedder-policy',
            'cross-origin-opener-policy',
            'cross-origin-resource-policy'
        ]
        
        results = {}
        for header in additional_headers:
            if header in headers:
                results[header] = {"status": "✅ PRESENT", "value": headers[header]}
            else:
                results[header] = {"status": "❌ MISSING"}
        
        return results
    
    def test_hsts_in_development(self) -> Dict[str, Any]:
        """Test that HSTS is not enabled in development."""
        response = requests.get(f"{BASE_URL}/")
        headers = response.headers
        
        if 'strict-transport-security' in headers:
            return {"hsts": {"status": "❌ FAIL", "reason": "HSTS should not be enabled in development"}}
        else:
            return {"hsts": {"status": "✅ PASS", "reason": "HSTS correctly disabled in development"}}
    
    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test security headers on different endpoints."""
        endpoints = ["/", "/docs"]
        results = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    has_security_headers = all(
                        header in response.headers 
                        for header in ['x-content-type-options', 'x-frame-options', 'x-xss-protection']
                    )
                    results[endpoint] = {
                        "status": "✅ PASS" if has_security_headers else "❌ FAIL",
                        "headers_count": len([h for h in response.headers if h.startswith('x-') or 'security' in h.lower() or 'origin' in h.lower()])
                    }
                else:
                    results[endpoint] = {"status": "❌ HTTP_ERROR", "code": response.status_code}
            except Exception as e:
                results[endpoint] = {"status": "❌ ERROR", "error": str(e)}
        
        return results

def run_integration_test():
    """Run the complete integration test suite."""
    print("🔒 Security Headers Integration Test")
    print("=" * 50)
    
    test = SecurityHeadersIntegrationTest()
    
    try:
        # Start server
        if not test.start_server():
            print("❌ Cannot start server, aborting tests")
            return
        
        print("\n📋 Testing Basic Security Headers (Issue 2 Requirements):")
        basic_results = test.test_basic_security_headers()
        for header, result in basic_results.items():
            print(f"  {header}: {result['status']}")
            if 'value' in result:
                print(f"    Value: {result['value']}")
        
        print("\n📋 Testing Additional Security Headers:")
        additional_results = test.test_additional_security_headers()
        for header, result in additional_results.items():
            print(f"  {header}: {result['status']}")
        
        print("\n📋 Testing HSTS Configuration:")
        hsts_results = test.test_hsts_in_development()
        for test_name, result in hsts_results.items():
            print(f"  {test_name}: {result['status']} - {result['reason']}")
        
        print("\n📋 Testing Multiple Endpoints:")
        endpoint_results = test.test_all_endpoints()
        for endpoint, result in endpoint_results.items():
            print(f"  {endpoint}: {result['status']}")
            if 'headers_count' in result:
                print(f"    Security headers: {result['headers_count']}")
        
        # Summary
        all_basic_passed = all(r['status'] == '✅ PASS' for r in basic_results.values())
        print(f"\n🎯 Issue 2 Requirements: {'✅ ALL PASSED' if all_basic_passed else '❌ SOME FAILED'}")
        
    finally:
        test.stop_server()

if __name__ == "__main__":
    run_integration_test()
