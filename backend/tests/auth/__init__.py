"""
Auth Test Suite Package.

This package contains comprehensive tests for the Authentication functionality
in the Cookify backend application.

The test suite is organized into:
- unit/: Unit tests for individual Auth components
- integration/: Integration tests with real dependencies (Supabase)
- fixtures/: Test data and mock user data
- utils/: Testing utilities, mocks, and data generators

Usage:
    Run all Auth tests:
        pytest tests/auth/

    Run only unit tests:
        pytest tests/auth/unit/

    Run with test runner:
        python tests/auth/run_tests.py --unit
        python tests/auth/run_tests.py --integration
        python tests/auth/run_tests.py --all --coverage
"""

__version__ = "1.0.0"
__author__ = "Cookify Team"

# Make key test utilities available at package level
from .config import AuthTestBase, AuthTestConfig
from .utils.mocks import AuthMockFactory, MockContextManager

__all__ = [
    "AuthTestConfig",
    "AuthTestBase",
    "AuthMockFactory",
    "MockContextManager",
]
