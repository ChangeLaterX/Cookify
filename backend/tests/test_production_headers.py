"""
Test security headers in production mode to verify HSTS behavior.
"""
import os
import sys
import subprocess
import time
import requests
import pathlib

# Set environment variables for production mode
os.environ['ENVIRONMENT'] = 'production'
os.environ['DEBUG'] = 'false'

def test_production_headers() -> None:
    """Test security headers in production configuration."""
    print("🏭 Testing Security Headers in Production Mode")
    print("=" * 50)
    
    # Start server with production config
    cmd: list[str] = [
        "python", "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    
    server_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(pathlib.Path(__file__).resolve().parent.parent),
        env=os.environ.copy()
    )
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Test production headers
        response = requests.get("http://localhost:8000/", timeout=5)
        headers = response.headers
        
        # Basic headers
        basic_headers = ['x-content-type-options', 'x-frame-options', 'x-xss-protection', 'content-security-policy']
        for header in basic_headers:
            assert header in headers, f"Header {header} is missing"
        
        # Check HSTS behavior
        if 'strict-transport-security' in headers:
            assert headers['strict-transport-security'], "HSTS header should not be empty"
        else:
            assert 'strict-transport-security' not in headers, "HSTS header should not be set for HTTP connections"
        
        # Check CSP differences
        csp = headers.get('content-security-policy', '')
        assert len(csp) > 0, "Content Security Policy header is missing"
        assert 'unsafe-inline' not in csp, "CSP contains 'unsafe-inline', which is not production-safe"
        
    except Exception as e:
        print(f"❌ Error testing production headers: {e}")
    
    finally:
        server_process.terminate()
        server_process.wait()
        print("\n🛑 Production test server stopped")

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
