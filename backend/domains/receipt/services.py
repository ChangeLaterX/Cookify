"""
Receipt Services with OCR Integration.
Handles OCR text extraction and ingredient matching for receipt processing.
"""

import logging
import time
import re
import asyncio
from typing import List, Optional, Tuple
from io import BytesIO
from difflib import SequenceMatcher

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    pytesseract = None
    Image = None
    OCR_AVAILABLE = False

from domains.ingredients.services import search_ingredients, IngredientError
from .schemas import (
    OCRTextResponse,
    OCRProcessedResponse,
    ReceiptItem,
    OCRItemSuggestion,
)

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Custom exception for OCR-related errors."""
    
    def __init__(self, message: str, error_code: str = "OCR_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class OCRService:
    """Service class for OCR operations."""
    
    def __init__(self):
        if not OCR_AVAILABLE:
            raise OCRError(
                "OCR dependencies not available. Please install pytesseract and Pillow.",
                "OCR_DEPENDENCIES_MISSING"
            )
    
    async def extract_text_from_image(self, image_data: bytes) -> OCRTextResponse:
        """
        Extract text from image using Tesseract OCR.
        
        Args:
            image_data: Raw image data as bytes
            
        Returns:
            OCRTextResponse with extracted text and metadata
            
        Raises:
            OCRError: If OCR processing fails
        """
        start_time = time.time()
        
        try:
            # Convert bytes to PIL Image
            if not Image:
                raise OCRError("PIL not available", "OCR_DEPENDENCIES_MISSING")
            
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed (handles RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Run OCR in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Extract text with confidence data
            if not pytesseract:
                raise OCRError("pytesseract not available", "OCR_DEPENDENCIES_MISSING")
                
            ocr_data = await loop.run_in_executor(
                None, 
                lambda: pytesseract.image_to_data(  # type: ignore
                    image, 
                    output_type=pytesseract.Output.DICT,  # type: ignore
                    config='--psm 6'  # Assume uniform block of text
                )
            )
            
            # Extract text
            extracted_text = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_string(  # type: ignore
                    image,
                    config='--psm 6'
                )
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"OCR completed in {processing_time_ms}ms with {avg_confidence:.1f}% confidence")
            
            return OCRTextResponse(
                extracted_text=extracted_text.strip(),
                confidence=avg_confidence,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            raise OCRError(f"Failed to process image: {str(e)}", "OCR_PROCESSING_FAILED")
    
    def _extract_receipt_items(self, text: str) -> List[str]:
        """
        Extract potential food items from receipt text.
        
        Args:
            text: Raw OCR text
            
        Returns:
            List of potential food item strings
        """
        lines = text.split('\n')
        items = []
        
        # Patterns to identify product lines (basic heuristics)
        # Skip lines that look like headers, totals, or store info
        skip_patterns = [
            r'^(total|subtotal|tax|change|receipt|store|address|phone)',
            r'^\d{1,2}[:/]\d{1,2}[:/]\d{2,4}',  # dates
            r'^\d+\.\d{2}$',  # standalone prices
            r'^[*-]{3,}',  # separators
            r'^(cashier|clerk|thank you)',
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Skip lines matching skip patterns
            if any(re.search(pattern, line.lower()) for pattern in skip_patterns):
                continue
            
            # Look for lines that might contain product names
            # Usually have letters and might have numbers/prices
            if re.search(r'[a-zA-Z]{3,}', line):
                # Clean up the line - remove prices and quantities at the end
                cleaned_line = re.sub(r'\s*\d+[.,]\d{2}\s*$', '', line)  # remove trailing prices
                cleaned_line = re.sub(r'\s*\d+\s*x\s*$', '', cleaned_line)  # remove quantities
                cleaned_line = re.sub(r'\s*@\s*\d+[.,]\d{2}\s*$', '', cleaned_line)  # remove unit prices
                
                if cleaned_line.strip() and len(cleaned_line.strip()) >= 3:
                    items.append(cleaned_line.strip())
        
        return items
    
    async def _find_ingredient_suggestions(
        self, 
        item_text: str, 
        max_suggestions: int = 3
    ) -> List[OCRItemSuggestion]:
        """
        Find ingredient suggestions for a receipt item.
        
        Args:
            item_text: Text of the receipt item
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of ingredient suggestions
        """
        suggestions = []
        
        try:
            # Search for similar ingredients
            search_result = await search_ingredients(
                query=item_text,
                limit=10,  # Get more results for better matching
                offset=0
            )
            
            for ingredient in search_result.ingredients:
                # Calculate similarity score
                similarity = SequenceMatcher(
                    None, 
                    item_text.lower(), 
                    ingredient.name.lower()
                ).ratio()
                
                # Only include if similarity is above threshold
                if similarity > 0.3:  # 30% similarity threshold
                    suggestions.append(OCRItemSuggestion(
                        ingredient_id=ingredient.ingredient_id,
                        ingredient_name=ingredient.name,
                        confidence_score=similarity * 100,
                        detected_text=item_text
                    ))
            
            # Sort by confidence and limit results
            suggestions.sort(key=lambda x: x.confidence_score, reverse=True)
            return suggestions[:max_suggestions]
            
        except IngredientError as e:
            logger.warning(f"Failed to search ingredients for '{item_text}': {e.message}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching ingredients for '{item_text}': {str(e)}")
            return []
    
    async def process_receipt_with_suggestions(
        self, 
        image_data: bytes
    ) -> OCRProcessedResponse:
        """
        Process receipt image and provide ingredient suggestions.
        
        Args:
            image_data: Raw image data as bytes
            
        Returns:
            OCRProcessedResponse with extracted items and ingredient suggestions
            
        Raises:
            OCRError: If processing fails
        """
        start_time = time.time()
        
        try:
            # Extract text from image
            ocr_result = await self.extract_text_from_image(image_data)
            
            # Extract potential items from text
            raw_items = self._extract_receipt_items(ocr_result.extracted_text)
            
            # Process each item and find ingredient suggestions
            processed_items = []
            for item_text in raw_items:
                suggestions = await self._find_ingredient_suggestions(item_text)
                
                receipt_item = ReceiptItem(
                    detected_text=item_text,
                    quantity=None,
                    unit=None,
                    price=None,
                    suggestions=suggestions
                )
                processed_items.append(receipt_item)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Receipt processing completed: {len(processed_items)} items found in {processing_time_ms}ms")
            
            return OCRProcessedResponse(
                raw_text=ocr_result.extracted_text,
                detected_items=processed_items,
                processing_time_ms=processing_time_ms,
                total_items_detected=len(processed_items)
            )
            
        except OCRError:
            raise  # Re-raise OCR errors
        except Exception as e:
            logger.error(f"Receipt processing failed: {str(e)}")
            raise OCRError(f"Failed to process receipt: {str(e)}", "RECEIPT_PROCESSING_FAILED")


# Create global service instance
ocr_service = OCRService() if OCR_AVAILABLE else None


# Public API functions
async def extract_text_from_image(image_data: bytes) -> OCRTextResponse:
    """Extract text from image using OCR."""
    if not ocr_service:
        raise OCRError(
            "OCR service not available. Please install required dependencies.",
            "OCR_SERVICE_UNAVAILABLE"
        )
    
    return await ocr_service.extract_text_from_image(image_data)


async def process_receipt_image(image_data: bytes) -> OCRProcessedResponse:
    """Process receipt image and provide ingredient suggestions."""
    if not ocr_service:
        raise OCRError(
            "OCR service not available. Please install required dependencies.",
            "OCR_SERVICE_UNAVAILABLE"
        )
    
    return await ocr_service.process_receipt_with_suggestions(image_data)