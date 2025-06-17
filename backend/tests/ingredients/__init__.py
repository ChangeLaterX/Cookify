"""
Ingredients Test Suite Package.

This package contains comprehensive tests for the Ingredients functionality 
in the Cookify backend application.

The test suite is organized into:
- unit/: Unit tests for individual Ingredients components
- integration/: Integration tests with real dependencies (Supabase)
- fixtures/: Test data and sample ingredient data
- utils/: Testing utilities, mocks, and data generators

Usage:
    Run all Ingredients tests:
        pytest tests/ingredients/
    
    Run only unit tests:
        pytest tests/ingredients/unit/
    
    Run with test runner:
        python tests/ingredients/run_tests.py --unit
        python tests/ingredients/run_tests.py --integration
        python tests/ingredients/run_tests.py --all --coverage
"""

__version__ = "1.0.0"
__author__ = "Cookify Team"

# Make key test utilities available at package level
from .config import IngredientsTestConfig, IngredientsTestBase
from .utils.mocks import IngredientsMockFactory, MockContextManager
from .utils.test_data import TestDataGenerator

__all__ = [
    "IngredientsTestConfig",
    "IngredientsTestBase",
    "IngredientsMockFactory", 
    "MockContextManager",
    "TestDataGenerator",
]
