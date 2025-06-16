"""
OCR Integration Tests Package.

This package contains integration tests that use real OCR dependencies and sample images.
These tests are automatically skipped if tesseract is not available or if running in mock mode.

To run integration tests:
    export OCR_TEST_INTEGRATION=true
    pytest tests/ocr/integration/

These tests require:
- tesseract-ocr installed and available in PATH
- Sample images in the data/ directory
- Real dependencies (PIL, pytesseract)
"""
