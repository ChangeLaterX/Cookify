"""
Test security headers in production mode to verify HSTS behavior.
"""
import os
import sys
import subprocess
import time
import requests

# Set environment variables for production mode
os.environ['ENVIRONMENT'] = 'production'
os.environ['DEBUG'] = 'false'

def test_production_headers():
    """Test security headers in production configuration."""
    print("🏭 Testing Security Headers in Production Mode")
    print("=" * 50)
    
    # Start server with production config
    cmd = [
        "python", "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8004"
    ]
    
    server_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/Users/jannis/Developer/Cookify/backend",
        env=os.environ.copy()
    )
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Test production headers
        response = requests.get("http://localhost:8004/", timeout=5)
        headers = response.headers
        
        print("📋 Production Security Headers:")
        
        # Basic headers
        basic_headers = ['x-content-type-options', 'x-frame-options', 'x-xss-protection', 'content-security-policy']
        for header in basic_headers:
            if header in headers:
                print(f"  ✅ {header}: {headers[header]}")
            else:
                print(f"  ❌ {header}: MISSING")
        
        # Check HSTS behavior
        if 'strict-transport-security' in headers:
            print(f"  ⚠️  strict-transport-security: {headers['strict-transport-security']}")
            print("      Note: HSTS should only be enabled over HTTPS in production")
        else:
            print("  ✅ strict-transport-security: Correctly not set (HTTP connection)")
        
        # Check CSP differences
        csp = headers.get('content-security-policy', '')
        print(f"\n🔒 Content Security Policy:")
        print(f"  Length: {len(csp)} characters")
        if 'unsafe-inline' in csp:
            print("  ⚠️  Contains 'unsafe-inline' (development-friendly CSP)")
        else:
            print("  ✅ No 'unsafe-inline' (production-strict CSP)")
        
    except Exception as e:
        print(f"❌ Error testing production headers: {e}")
    
    finally:
        server_process.terminate()
        server_process.wait()
        print("\n🛑 Production test server stopped")

if __name__ == "__main__":
    test_production_headers()
