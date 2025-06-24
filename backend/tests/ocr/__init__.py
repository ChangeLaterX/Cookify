"""
OCR Test Suite Package.

This package contains comprehensive tests for the OCR (Optical Character Recognition)
functionality in the Cookify backend application.

The test suite is organized into:
- unit/: Unit tests for individual OCR components
- integration/: Integration tests with real dependencies
- fixtures/: Test data and sample images
- utils/: Testing utilities, mocks, and data generators

Usage:
    Run all OCR tests:
        pytest tests/ocr/

    Run only unit tests:
        pytest tests/ocr/unit/

    Run with test runner:
        python tests/ocr/run_tests.py --unit
        python tests/ocr/run_tests.py --integration
        python tests/ocr/run_tests.py --all --coverage
"""

__version__ = "1.0.0"
__author__ = "Cookify Team"

# Make key test utilities available at package level
from .config import OCRTestConfig, OCRTestBase

# from .utils.mocks import OCRMockFactory, MockContextManager
# from .utils.test_data import TestDataGenerator

__all__ = [
    "OCRTestConfig",
    "OCRTestBase",
    # "OCRMockFactory",
    # "MockContextManager",
    # "TestDataGenerator",
]
