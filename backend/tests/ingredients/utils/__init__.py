"""Utilities package for Ingredients testing."""

# Test utilities (basic test data generation removed for simplicity)
# from .test_data import TestDataGenerator, TestIngredientData, TestScenarios

# Legacy mocks (deprecated - use Smart Mocks instead)
from .mocks import IngredientsMockFactory, MockContextManager, with_mocked_ingredients

# Smart Mocks (imported on demand to avoid circular imports)
# from .smart_mocks import SmartMockContextManager, smart_ingredients_mock

__all__ = [
    # Test Data (removed for simplicity)
    # "TestDataGenerator",
    # "TestIngredientData",
    # "TestScenarios",
    # Legacy (Deprecated)
    "IngredientsMockFactory",
    "MockContextManager",
    "with_mocked_ingredients",
    # Smart Mocks (import explicitly when needed)
    # "SmartMockContextManager",
    # "smart_ingredients_mock",
]
