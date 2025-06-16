"""
OCR Test Configuration and Base Classes.

This module provides the base configuration and shared utilities for all OCR tests.
"""

import os
import shutil
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OCRTestConfig:
    """Configuration for OCR tests."""
    
    # Test modes
    MOCK_MODE: bool = os.getenv('OCR_TEST_MOCK_MODE', 'true').lower() == 'true'
    INTEGRATION_MODE: bool = os.getenv('OCR_TEST_INTEGRATION', 'false').lower() == 'true'
    
    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    TEST_ROOT: Path = PROJECT_ROOT / 'tests' / 'ocr'
    FIXTURES_PATH: Path = TEST_ROOT / 'fixtures'
    SAMPLE_IMAGES_PATH: Path = PROJECT_ROOT.parent / 'data'
    
    # Dependencies
    TESSERACT_AVAILABLE: bool = shutil.which('tesseract') is not None
    
    # Test data
    DEFAULT_CONFIDENCE: float = 85.0
    DEFAULT_PROCESSING_TIME: int = 100
    
    @classmethod
    def should_run_integration_tests(cls) -> bool:
        """Determine if integration tests should run."""
        config = cls()
        return config.TESSERACT_AVAILABLE and config.INTEGRATION_MODE
    
    @classmethod
    def get_sample_image_path(cls, filename: str) -> Optional[Path]:
        """Get path to sample image if it exists."""
        config = cls()
        image_path = config.SAMPLE_IMAGES_PATH / filename
        return image_path if image_path.exists() else None


class OCRTestBase(ABC):
    """Base class for all OCR tests with common utilities."""
    
    @classmethod
    def setup_class(cls):
        """Setup for test class."""
        cls.config = OCRTestConfig()
    
    def setup_method(self):
        """Setup for individual test method."""
        pass
    
    def teardown_method(self):
        """Teardown for individual test method."""
        pass
    
    @staticmethod
    def create_mock_image_data() -> bytes:
        """Create mock image data for testing."""
        return b"fake_image_data_for_testing"
    
    @staticmethod
    def create_sample_receipt_text() -> str:
        """Create sample receipt text for testing."""
        return """
        FRESH MARKET GROCERY
        123 Main Street
        
        Tomatoes (2 lbs)      $3.98
        Onions (1 lb)         $1.49
        Garlic (3 bulbs)      $2.25
        Bell Peppers (4)      $4.76
        Milk (1 gallon)       $3.29
        
        Subtotal:            $15.77
        Tax:                 $1.26
        Total:               $17.03
        """


# Test data constants
RECEIPT_TEXT_VARIATIONS = {
    "clean": {
        "text": "Tomatoes (2 lbs) $3.98\nMilk (1 gallon) $3.29",
        "expected_items": ["Tomatoes", "Milk"],
        "expected_quantities": [2.0, 1.0],
        "expected_units": ["lb", "gal"],
        "expected_prices": [3.98, 3.29]
    },
    "with_ocr_errors": {
        "text": "Tomatnes (2 its) $398\nMitk (1 gallon) $329",
        "expected_items": ["Tomatoes", "Milk"],
        "expected_corrections": {
            "Tomatnes": "Tomatoes",
            "its": "lb",
            "Mitk": "Milk"
        }
    },
    "complex_receipt": {
        "text": """
        FRESH MARKET GROCERY
        Receipt #: 001234567
        
        Tomatoes (2 lbs)      $3.98
        Onions (1 lb)         $1.49
        Bell Peppers (4)      $4.76
        
        Subtotal:            $10.23
        Tax:                 $0.82
        Total:               $11.05
        """,
        "expected_items": ["Tomatoes", "Onions", "Bell Peppers"]
    }
}

OCR_ERROR_PATTERNS = {
    "unit_errors": {
        "its": "lb",
        "ibs": "lb", 
        "ib": "lb",
        "be": "lb",
        "bs": "lb",
        "ts": "lb",
        "goz": "oz",
        "bults": "bulbs",
        "cound": "count"
    },
    "product_errors": {
        "Tomatnes": "Tomatoes",
        "Garlie": "Garlic",
        "Mitk": "Milk",
        "Fggs": "Eggs",
        "Chesidar": "Cheddar",
        "Bellpeppers": "Bell Peppers"
    },
    "price_errors": {
        # Format: (input, expected_output)
        "$398": 398.0,  # Actual behavior - no automatic conversion
        "$149": 149.0,  # Actual behavior 
        "$1299": 12.99,  # 4+ digits get split
        "$2345": 23.45   # 4+ digits get split
    }
}
