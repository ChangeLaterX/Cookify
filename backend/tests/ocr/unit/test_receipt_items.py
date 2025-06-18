"""
Unit Tests for Receipt Item Extraction and Processing.

This module tests the extraction and processing of individual items from receipt text.
"""

import pytest
from unittest.mock import patch, MagicMock

from domains.ocr.services import OCRService
from tests.ocr.config import OCRTestBase
from tests.ocr.utils.mocks import MockContextManager
from tests.ocr.utils.test_data import get_test_data


class TestReceiptItemExtraction(OCRTestBase):
    """Test receipt item extraction from text."""

    def test_extract_receipt_items_basic(self):
        """Test basic extraction of food items from receipt text."""
        with MockContextManager():
            service = OCRService()
            
            receipt_text = self.create_sample_receipt_text()
            items = service._extract_receipt_items(receipt_text)
            
            # Verify food items are extracted
            assert len(items) > 0
            item_names = [item.lower() for item in items]
            
            # Check for expected food items
            expected_items = ['tomatoes', 'onions', 'garlic', 'bell peppers', 'milk']
            for expected in expected_items:
                assert any(expected in item for item in item_names), \
                    f"Expected '{expected}' not found in {item_names}"

    def test_extract_receipt_items_with_ocr_errors(self):
        """Test receipt item extraction with common OCR errors."""
        with MockContextManager():
            service = OCRService()
            
            # Receipt text with OCR errors
            receipt_text = """
            Tomatnes (2 Its)     $398
            Garlie (3 bults)     $225
            Mitk (1 gallon)      $329
            Fggs (12 cound)      $289
            """
            
            items = service._extract_receipt_items(receipt_text)
            
            # Verify OCR errors are corrected
            assert len(items) > 0
            item_names = [item.lower() for item in items]
            
            # Check that corrected names appear (the service corrects OCR errors)
            expected_corrections = ['tomatoes', 'garlic', 'milk', 'eggs']
            for expected in expected_corrections:
                assert any(expected in item for item in item_names), \
                    f"Expected corrected '{expected}' not found in {item_names}"

    def test_extract_receipt_items_filters_non_food_items(self):
        """Test that non-food items are filtered out."""
        with MockContextManager():
            service = OCRService()
            
            receipt_text = """
            FRESH MARKET GROCERY
            123 Main Street
            Receipt #: 001234567
            Date: 2024-12-15
            Cashier: John D.
            
            Tomatoes (2 lbs)      $3.98
            Onions (1 lb)         $1.49
            
            Subtotal:            $5.47
            Tax:                 $0.44
            Total:               $5.91
            Thank you for shopping!
            """
            
            items = service._extract_receipt_items(receipt_text)
            
            # Should only contain food items, not store info or totals
            item_names = [item.lower() for item in items]
            
            # Should have food items
            food_items = ['tomatoes', 'onions']
            for food_item in food_items:
                assert any(food_item in item for item in item_names)
            
            # Should not have non-food items
            non_food_items = ['fresh market', 'receipt', 'subtotal', 'total', 'thank you']
            for non_food in non_food_items:
                assert not any(non_food in item for item in item_names)

    def test_extract_receipt_items_empty_text(self):
        """Test receipt item extraction with empty or invalid text."""
        with MockContextManager():
            service = OCRService()
            
            # Test with empty text
            items = service._extract_receipt_items("")
            assert len(items) == 0
            
            # Test with whitespace only
            items = service._extract_receipt_items("   \n  \t  ")
            assert len(items) == 0
            
            # Test with non-food items only
            items = service._extract_receipt_items(
                "Receipt #123\nDate: 2024-01-01\nTotal: $10.00"
            )
            assert len(items) == 0

    def test_extract_receipt_items_with_variations(self):
        """Test receipt item extraction with different text variations."""
        with MockContextManager():
            service = OCRService()
            
            # Get test data variations
            variations = get_test_data("receipt_variations")
            
            for variation_name, variation_text in variations.items():
                items = service._extract_receipt_items(variation_text)
                
                # Each variation should extract some items (except very poor quality)
                if variation_name != "very_poor_quality":
                    assert len(items) > 0, f"No items extracted from {variation_name}"

    def test_extract_receipt_items_food_keyword_detection(self):
        """Test that food keywords are properly detected."""
        with MockContextManager():
            service = OCRService()
            
            # Text with various food items
            receipt_text = """
            Chicken Breast (2 lbs)    $8.98
            Ground Beef (1 lb)        $5.99
            Salmon Fillet (1 lb)      $12.99
            Cheddar Cheese (8oz)      $3.99
            Whole Wheat Bread         $2.99
            Jasmine Rice (2 lbs)      $3.49
            Olive Oil (500ml)         $6.99
            Fresh Basil               $1.99
            """
            
            items = service._extract_receipt_items(receipt_text)
            
            # Should extract all food items
            assert len(items) >= 6  # At least most items should be detected
            
            item_text = " ".join(items).lower()
            food_keywords = ['chicken', 'beef', 'salmon', 'cheese', 'bread', 'rice', 'oil', 'basil']
            
            for keyword in food_keywords:
                assert keyword in item_text, f"Food keyword '{keyword}' not found in extracted items"

    def test_extract_receipt_items_quantity_cleaning(self):
        """Test that quantity information is properly cleaned from item names."""
        with MockContextManager():
            service = OCRService()
            
            receipt_text = """
            Tomatoes (2 lbs)      $3.98
            Milk (1 gallon)       $3.29
            Eggs (12 count)       $2.89
            """
            
            items = service._extract_receipt_items(receipt_text)
            
            # Items should have quantity info removed
            for item in items:
                # Should not contain quantity patterns
                assert not any(pattern in item.lower() for pattern in ['(2 lbs)', '(1 gallon)', '(12 count)'])
                # But should contain the food names
                item_lower = item.lower()
                food_names = ['tomatoes', 'milk', 'eggs']
                assert any(food in item_lower for food in food_names)

    def test_extract_receipt_items_price_cleaning(self):
        """Test that price information is properly cleaned from item names."""
        with MockContextManager():
            service = OCRService()
            
            receipt_text = """
            Tomatoes $3.98
            Milk $3.29
            Bread $2.99
            """
            
            items = service._extract_receipt_items(receipt_text)
            
            # Items should have price info removed
            for item in items:
                # Should not contain price patterns
                assert not any(price in item for price in ['$3.98', '$3.29', '$2.99'])
                # But should contain the food names
                item_lower = item.lower()
                food_names = ['tomatoes', 'milk', 'bread']
                assert any(food in item_lower for food in food_names)


class TestReceiptItemCleaning(OCRTestBase):
    """Test receipt item cleaning and normalization."""

    def test_item_name_normalization(self):
        """Test that item names are properly normalized."""
        with MockContextManager():
            service = OCRService()
            
            # Text with various formatting issues
            receipt_text = """
            TOMATOES       $3.98
            onions         $1.49
            Bell_Peppers   $4.76
            """
            
            items = service._extract_receipt_items(receipt_text)
            
            # Items should be properly formatted (title case)
            for item in items:
                # Should be title case
                assert item.istitle() or item.isupper(), f"Item '{item}' not properly formatted"

    def test_ocr_error_correction(self):
        """Test that OCR errors are corrected in item extraction."""
        with MockContextManager():
            service = OCRService()
            
            # Get OCR error test cases
            error_cases = get_test_data("ocr_error_cases")
            
            for error_text, expected_correction in error_cases[:5]:  # Test first 5 cases
                items = service._extract_receipt_items(error_text)
                
                if items:  # If items were extracted
                    item_text = " ".join(items).lower()
                    # The correction should appear in the extracted text
                    assert expected_correction.lower() in item_text, \
                        f"Expected correction '{expected_correction}' not found in '{item_text}'"

    def test_special_character_handling(self):
        """Test handling of special characters in receipt text."""
        with MockContextManager():
            service = OCRService()
            
            receipt_text = """
            Tom@toes (2 lbs)      $3.98
            Oni#ns (1 lb)         $1.49
            G*rlic (3 bulbs)      $2.25
            """
            
            items = service._extract_receipt_items(receipt_text)
            
            # Should extract items despite special characters
            assert len(items) > 0
            
            # Special characters should be cleaned
            for item in items:
                assert not any(char in item for char in ['@', '#', '*'])

    def test_multiple_line_item_handling(self):
        """Test handling of items that span multiple lines."""
        with MockContextManager():
            service = OCRService()
            
            receipt_text = """
            Organic Free Range
            Chicken Breast (2 lbs)    $8.98
            Extra Virgin
            Olive Oil (500ml)         $6.99
            """
            
            items = service._extract_receipt_items(receipt_text)
            
            # Should extract meaningful item names
            assert len(items) > 0
            
            item_text = " ".join(items).lower()
            # Should contain key food terms
            food_terms = ['chicken', 'olive']
            for term in food_terms:
                assert term in item_text, f"Expected term '{term}' not found in extracted items"
