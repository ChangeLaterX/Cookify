#!/usr/bin/env python3
"""
Debug script to check rate limiting configuration values.
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, '/Users/jannis/Developer/Cookify/backend')

from core.config import settings

def main():
    print("=== Rate Limiting Debug Information ===")
    print(f"Debug mode: {settings.debug}")
    print(f"Environment: {settings.environment}")
    print(f"Rate limiting enabled (base): {settings.rate_limiting_enabled}")
    print(f"Rate limiting enabled (safe): {settings.rate_limiting_enabled_safe}")
    print(f"Is production: {settings.is_production}")
    print(f"Is development: {settings.is_development}")
    print()
    print("=== Expected Behavior ===")
    print("When debug=True, rate_limiting_enabled_safe should be False")
    print("This should disable rate limiting completely")
    print()
    
    # Test the property logic manually
    print("=== Manual Property Test ===")
    if settings.debug:
        expected_rate_limiting = False
    else:
        expected_rate_limiting = settings.rate_limiting_enabled
    
    print(f"Expected rate_limiting_enabled_safe: {expected_rate_limiting}")
    print(f"Actual rate_limiting_enabled_safe: {settings.rate_limiting_enabled_safe}")
    print(f"Match: {expected_rate_limiting == settings.rate_limiting_enabled_safe}")

if __name__ == "__main__":
    main()
