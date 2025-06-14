#!/usr/bin/env python3
"""
Debug script to check rate limiting configuration values.
"""
import sys
import os
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from core.config import settings

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("=== Rate Limiting Debug Information ===")
    logger.debug(f"Debug mode: {settings.DEBUG}")
    logger.debug(f"Environment: {settings.ENVIRONMENT}")
    logger.debug(f"Rate limiting enabled (base): {settings.RATE_LIMITING_ENABLED}")
    logger.debug(f"Rate limiting enabled (safe): {settings.rate_limiting_enabled_safe}")
    logger.debug(f"Is production: {settings.is_production}")
    logger.debug(f"Is development: {settings.is_development}")
    logger.info("=== Expected Behavior ===")
    logger.info("When debug=True, rate_limiting_enabled_safe should be False")
    logger.info("This should disable rate limiting completely")
    
    # Test the property logic manually
    logger.info("=== Manual Property Test ===")
    if settings.DEBUG:
        expected_rate_limiting = False
    else:
        expected_rate_limiting = settings.RATE_LIMITING_ENABLED
    
    logger.debug(f"Expected rate_limiting_enabled_safe: {expected_rate_limiting}")
    logger.debug(f"Actual rate_limiting_enabled_safe: {settings.rate_limiting_enabled_safe}")
    logger.info(f"Match: {expected_rate_limiting == settings.rate_limiting_enabled_safe}")

if __name__ == "__main__":
    main()
