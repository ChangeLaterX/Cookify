"""
Unit Tests for OCR Service Initialization and Dependencies.

This module tests the basic setup and configuration of the OCR service.
"""

import pytest
from unittest.mock import patch, MagicMock
import shutil
import os

from domains.ocr.services import OCRService, OCRError
from tests.ocr.config import OCRTestBase
from tests.ocr.utils.mocks import MockContextManager, with_mocked_ocr


class TestOCRServiceInitialization(OCRTestBase):
    """Test OCR service initialization and dependency management."""

    def test_ocr_service_initialization_with_dependencies(self):
        """Test OCR service initializes correctly when dependencies are available."""
        with MockContextManager() as mock_ctx:
            # Mock tesseract path detection
            with patch('shutil.which', return_value='/usr/bin/tesseract'), \
                 patch('os.path.isfile', return_value=True):
                
                service = OCRService()
                
                # Verify service has expected configuration
                assert hasattr(service, 'optimal_config')
                assert 'primary' in service.optimal_config
                assert 'fallback_psm_4' in service.optimal_config
                assert 'fallback_psm_11' in service.optimal_config
                assert 'default' in service.optimal_config

    def test_ocr_service_initialization_without_dependencies(self):
        """Test OCR service raises error when dependencies are missing."""
        with patch('domains.ocr.services.OCR_AVAILABLE', False):
            with pytest.raises(OCRError) as exc_info:
                OCRService()
            
            assert exc_info.value.error_code == "OCR_DEPENDENCIES_MISSING"
            assert "OCR dependencies not available" in exc_info.value.message

    def test_tesseract_path_configuration(self):
        """Test tesseract path configuration logic."""
        with MockContextManager():
            # Test with tesseract found in PATH
            with patch('shutil.which', return_value='/usr/bin/tesseract'), \
                 patch('os.path.isfile', return_value=True):
                
                service = OCRService()
                # Should not raise an error
                assert service is not None

    def test_tesseract_path_not_found(self):
        """Test behavior when tesseract executable is not found."""
        with MockContextManager():
            # Mock all tesseract paths as not found
            with patch('shutil.which', return_value=None), \
                 patch('os.path.isfile', return_value=False), \
                 patch.dict('os.environ', {}, clear=True):
                
                # Should still create service but with warnings
                service = OCRService()
                assert service is not None

    def test_optimal_config_structure(self):
        """Test that optimal configuration has correct structure."""
        with MockContextManager():
            service = OCRService()
            
            # Check that all expected configs exist
            expected_configs = ['primary', 'fallback_psm_4', 'fallback_psm_11', 'default']
            for config_name in expected_configs:
                assert config_name in service.optimal_config
                assert isinstance(service.optimal_config[config_name], str)
                
            # Check that primary config contains expected parameters
            primary_config = service.optimal_config['primary']
            assert '--psm' in primary_config
            assert '--oem' in primary_config
            assert 'tesseract_char_whitelist' in primary_config


class TestOCRServiceDependencyChecks(OCRTestBase):
    """Test dependency checking and availability."""

    def test_ocr_available_flag_with_dependencies(self):
        """Test OCR_AVAILABLE flag when dependencies are present."""
        with patch('domains.ocr.services.pytesseract', MagicMock()), \
             patch('domains.ocr.services.Image', MagicMock()):
            
            # Re-import to trigger availability check
            import importlib
            from domains.ocr import services
            importlib.reload(services)
            
            # OCR should be available
            assert services.OCR_AVAILABLE is True

    def test_ocr_available_flag_without_pytesseract(self):
        """Test OCR_AVAILABLE flag when pytesseract is missing."""
        with patch.dict('sys.modules', {'pytesseract': None}):
            # Re-import to trigger availability check
            import importlib
            from domains.ocr import services
            importlib.reload(services)
            
            # OCR should not be available
            assert services.OCR_AVAILABLE is False

    def test_ocr_available_flag_without_pil(self):
        """Test OCR_AVAILABLE flag when PIL is missing."""
        with patch.dict('sys.modules', {'PIL': None, 'PIL.Image': None}):
            # Re-import to trigger availability check
            import importlib
            from domains.ocr import services
            importlib.reload(services)
            
            # OCR should not be available
            assert services.OCR_AVAILABLE is False

    def test_global_service_instance_creation(self):
        """Test that global service instance is created correctly."""
        with MockContextManager():
            from domains.ocr.services import ocr_service
            
            # Service should be created when dependencies are available
            assert ocr_service is not None
            assert hasattr(ocr_service, 'extract_text_from_image')
            assert hasattr(ocr_service, 'process_receipt_with_suggestions')

    def test_global_service_instance_none_when_unavailable(self):
        """Test that global service instance is None when dependencies unavailable."""
        with patch('domains.ocr.services.OCR_AVAILABLE', False):
            # Re-import to trigger service creation
            import importlib
            from domains.ocr import services
            importlib.reload(services)
            
            # Service should be None
            assert services.ocr_service is None
