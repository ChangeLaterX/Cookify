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
        
        # Configure tesseract path - try standard Docker/system locations
        if pytesseract:
            import os
            import shutil
            
            # Try to find tesseract in standard locations (Docker-friendly)
            tesseract_paths = [
                shutil.which('tesseract'),  # PATH lookup (should work in Docker)
                '/usr/bin/tesseract',  # Standard system installation
                '/usr/local/bin/tesseract',  # Local installation
                os.environ.get('TESSERACT_CMD'),  # Environment variable override
            ]
            
            for path in tesseract_paths:
                if path and os.path.isfile(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Configured tesseract path: {path}")
                    break
            else:
                logger.warning("Could not find tesseract executable. Install tesseract-ocr package.")
    
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
            
            # Preprocess image for better OCR accuracy
            image = self._preprocess_image_for_ocr(image)
            
            # Run OCR in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Extract text with confidence data using optimized config
            if not pytesseract:
                raise OCRError("pytesseract not available", "OCR_DEPENDENCIES_MISSING")
            
            # Try different OCR configurations for best results
            configs = [
                '--psm 6 -c tesseract_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$()- ',
                '--psm 6',  # Assume uniform block of text
                '--psm 4',  # Assume single column of text
                '--psm 3',  # Default, fully automatic page segmentation
            ]
            
            best_result = None
            best_confidence = 0
            
            for config in configs:
                try:
                    # Extract confidence data
                    ocr_data = await loop.run_in_executor(
                        None, 
                        lambda c=config: pytesseract.image_to_data(  # type: ignore
                            image, 
                            output_type=pytesseract.Output.DICT,  # type: ignore
                            config=c
                        )
                    )
                    
                    # Extract text
                    extracted_text = await loop.run_in_executor(
                        None,
                        lambda c=config: pytesseract.image_to_string(  # type: ignore
                            image,
                            config=c
                        )
                    )
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Keep the best result
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_result = extracted_text
                        
                except Exception as e:
                    logger.warning(f"OCR config '{config}' failed: {e}")
                    continue
            
            # Fallback if all configs failed
            if best_result is None:
                ocr_data = await loop.run_in_executor(
                    None, 
                    lambda: pytesseract.image_to_data(  # type: ignore
                        image, 
                        output_type=pytesseract.Output.DICT,  # type: ignore
                        config='--psm 6'
                    )
                )
                
                best_result = await loop.run_in_executor(
                    None,
                    lambda: pytesseract.image_to_string(  # type: ignore
                        image,
                        config='--psm 6'
                    )
                )
                
                confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                best_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"OCR completed in {processing_time_ms}ms with {best_confidence:.1f}% confidence")
            
            return OCRTextResponse(
                extracted_text=best_result.strip() if best_result else "",
                confidence=best_confidence,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            raise OCRError(f"Failed to process image: {str(e)}", "OCR_PROCESSING_FAILED")
    
    def _extract_receipt_items(self, text: str) -> List[str]:
        """
        Extract potential food items from receipt text with advanced recognition.
        
        Args:
            text: Raw OCR text
            
        Returns:
            List of potential food item strings
        """
        lines = text.split('\n')
        items = []
        
        # Enhanced patterns to identify product lines
        skip_patterns = [
            # Store info patterns
            r'^(fresh|market|grocery|store|shop|supermarket)',
            r'^\d{1,3}\s+(main|street|ave|avenue|road|rd|st|drive|dr)',
            r'^(anytown|city|town)',
            r'^tel[:\s]*\(?[\d\s\-\)]+',
            r'^phone[:\s]*\(?[\d\s\-\)]+',
            
            # Receipt metadata patterns
            r'^receipt\s*[#:]',
            r'^date[:\s]*\d',
            r'^time[:\s]*\d',
            r'^cashier[:\s]*',
            r'^clerk[:\s]*',
            r'^register[:\s]*',
            
            # Total/summary patterns - improved
            r'^(sub)?total[:\s]*',
            r'^tax[:\s]*\(?[\d\.%]+',
            r'^change[:\s]*\$',
            r'^payment[:\s]*',
            r'^card[:\s]*',
            r'^cash[:\s]*',
            r'^subtott',  # OCR error for "subtotal"
            r'^tot[:\s]*',  # OCR error for "total"
            r'^tout[:\s]*',  # OCR error for "total"
            
            # Footer patterns
            r'^thank\s+you',
            r'^have\s+a',
            r'^visit\s+us',
            r'^www\.',
            r'^[\*\-=]{3,}',  # separators
            
            # Standalone prices or numbers
            r'^\$?\d+[.,]\d{2}$',
            r'^\d{1,2}[:/]\d{1,2}[:/]\d{2,4}',  # dates
        ]
        
        # Enhanced patterns that indicate a product line
        product_indicators = [
            # Quantity patterns - more flexible for OCR errors
            r'\(\d+\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|ct|pcs?|pieces?|gallon|l|ml)\)',  
            r'\(\d+\s*(its|ibs|ib|be|bs|1b|11b|2b|ts|bults|butte|goz|cound|container|tresh|fresh)\)',  # OCR errors
            r'\d+\s*x\s*',  # quantity multiplier
            r'@\s*\$\d+[.,]\d{2}',  # unit price
            r'\$\d+[.,]\d{2}\s*$',  # price at end of line
            r'\$\d+[.,]\d{1,2}[.,]?\s*$',  # price with OCR errors
            # Common quantity indicators without parentheses
            r'\d+\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|gallon|l|ml)\s',
            r'\d+\s*(its|ibs|ib|be|bs|1b|11b|2b|ts|container)\s',  # OCR errors
        ]
        
        # Pre-process lines to fix common OCR errors
        corrected_lines = []
        for line in lines:
            # Fix common OCR errors in units
            corrected_line = line
            corrected_line = re.sub(r'\b(its|ibs)\b', 'lbs', corrected_line, flags=re.IGNORECASE)
            corrected_line = re.sub(r'\b(ib|1b|11b)\b', 'lb', corrected_line, flags=re.IGNORECASE)
            corrected_line = re.sub(r'\b(be|bs)\b', 'lbs', corrected_line, flags=re.IGNORECASE)
            corrected_line = re.sub(r'\b(ts)\b', 'lbs', corrected_line, flags=re.IGNORECASE)
            corrected_line = re.sub(r'\b(goz)\b', '8oz', corrected_line, flags=re.IGNORECASE)
            corrected_line = re.sub(r'\b(cound)\b', 'count', corrected_line, flags=re.IGNORECASE)
            corrected_line = re.sub(r'\b(bults|butte)\b', 'bulbs', corrected_line, flags=re.IGNORECASE)
            corrected_line = re.sub(r'\b(tresh)\b', 'fresh', corrected_line, flags=re.IGNORECASE)
            
            # Fix price formatting OCR errors
            corrected_line = re.sub(r'\$(\d+)(\d{2})([,.]?)', r'$\1.\2', corrected_line)  # $398 -> $3.98
            corrected_line = re.sub(r'\$(\d+)[.,](\d{1})(\d{1})([,.]?)', r'$\1.\2\3', corrected_line)  # $1.2.9 -> $1.29
            
            corrected_lines.append(corrected_line)
        
        for line in corrected_lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Skip lines matching skip patterns
            if any(re.search(pattern, line.lower()) for pattern in skip_patterns):
                continue
            
            # Look for lines that contain alphabetic characters (potential product names)
            if not re.search(r'[a-zA-Z]{2,}', line):
                continue
                
            # Check if line has product indicators or looks like a product line
            has_product_indicator = any(re.search(pattern, line, re.IGNORECASE) for pattern in product_indicators)
            has_letters_and_price = re.search(r'[a-zA-Z].*\$\d+[.,]\d{1,2}', line)
            
            # Additional check: line starts with a food-related word
            food_start_words = [
                'tomato', 'onion', 'garlic', 'pepper', 'carrot', 'potato', 'spinach',
                'banana', 'apple', 'orange', 'lemon', 'lime', 'berry', 'grape',
                'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey',
                'milk', 'cheese', 'egg', 'butter', 'yogurt', 'cream',
                'bread', 'rice', 'pasta', 'flour', 'cereal', 'oat',
                'oil', 'salt', 'pepper', 'spice', 'herb', 'basil', 'oregano',
                'bean', 'lentil', 'nut', 'almond', 'walnut',
                'lettuce', 'cabbage', 'broccoli', 'cauliflower', 'mushroom',
                # Common variations and OCR errors
                'tomatnes', 'onions', 'garlie', 'bellpeppers', 'cancts', 'bananas',
                'apples', 'ground', 'salmon', 'fillet', 'mitk', 'imtik', 'eggs', 'fggs',
                'cheddar', 'chesidar', 'pasa', 'otiweoit', 'otiveoil', 'basilfresh'
            ]
            
            starts_with_food = any(line.lower().startswith(word) for word in food_start_words)
            
            if has_product_indicator or has_letters_and_price or starts_with_food:
                # Advanced cleaning pipeline
                cleaned_line = line
                
                # Remove trailing prices (more flexible patterns)
                cleaned_line = re.sub(r'\s*\$\d+[.,]\d{1,2}[.,]?\s*$', '', cleaned_line)
                cleaned_line = re.sub(r'\s*\$\d+[.,]\d{1,2}\s*,?\s*$', '', cleaned_line)
                
                # Remove trailing quantities and unit prices
                cleaned_line = re.sub(r'\s*\d+\s*x\s*$', '', cleaned_line)
                cleaned_line = re.sub(r'\s*@\s*\$\d+[.,]\d{1,2}\s*$', '', cleaned_line)
                
                # Remove quantity indicators in parentheses but keep the text before
                cleaned_line = re.sub(r'\s*\(\d+\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|ct|pcs?|pieces?|gallon|l|ml)\)\s*', ' ', cleaned_line)
                
                # Remove trailing quantity without parentheses
                cleaned_line = re.sub(r'\s*\(\d+\s*(its|ibs|ib|be|bs|1b|11b|2b|ts|bults|butte|goz|cound|container|tresh|fresh)\)\s*', ' ', cleaned_line)
                cleaned_line = re.sub(r'\s+\d+\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|gallon|l|ml)\s*$', '', cleaned_line)
                
                # Clean up extra whitespace and OCR artifacts
                cleaned_line = re.sub(r'\s+', ' ', cleaned_line)  # normalize whitespace
                cleaned_line = re.sub(r'[^\w\s\-\']', ' ', cleaned_line)  # remove special chars except useful ones
                cleaned_line = cleaned_line.strip()
                
                # Fix common product name OCR errors
                cleaned_line = re.sub(r'\btomatnes\b', 'tomatoes', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\bgarlie\b', 'garlic', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\bbellpeppers\b', 'bell peppers', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\bcancts\b', 'carrots', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\bmitk|imtik\b', 'milk', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\bfggs\b', 'eggs', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\bchesidar\b', 'cheddar', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\bpasa\b', 'pasta', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\botiweoit|otiveoil\b', 'olive oil', cleaned_line, flags=re.IGNORECASE)
                cleaned_line = re.sub(r'\bbasilfresh\b', 'basil fresh', cleaned_line, flags=re.IGNORECASE)
                
                if cleaned_line and len(cleaned_line) >= 3:
                    # Enhanced food keywords list with common variations
                    food_keywords = [
                        # Vegetables
                        'tomato', 'onion', 'garlic', 'pepper', 'carrot', 'potato', 'spinach',
                        'lettuce', 'cabbage', 'broccoli', 'cauliflower', 'mushroom', 'celery',
                        'cucumber', 'zucchini', 'eggplant', 'bell', 'green', 'red',
                        
                        # Fruits
                        'banana', 'apple', 'orange', 'lemon', 'lime', 'berry', 'grape',
                        'strawberry', 'blueberry', 'raspberry', 'pear', 'peach', 'plum',
                        
                        # Proteins
                        'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey',
                        'ground', 'breast', 'fillet', 'steak', 'chop', 'wing', 'thigh',
                        
                        # Dairy
                        'milk', 'cheese', 'egg', 'butter', 'yogurt', 'cream', 'cheddar',
                        'mozzarella', 'swiss', 'american', 'cottage',
                        
                        # Pantry staples
                        'bread', 'rice', 'pasta', 'flour', 'cereal', 'oat', 'wheat',
                        'quinoa', 'barley', 'noodle', 'spaghetti', 'penne',
                        
                        # Seasonings & oils
                        'oil', 'salt', 'pepper', 'spice', 'herb', 'basil', 'oregano',
                        'olive', 'vegetable', 'canola', 'coconut', 'sesame',
                        
                        # Legumes & nuts
                        'bean', 'lentil', 'nut', 'almond', 'walnut', 'peanut',
                        'cashew', 'pecan', 'pistachio', 'chickpea', 'kidney'
                    ]
                    
                    # Check if the item contains food-related keywords
                    contains_food_keyword = any(keyword in cleaned_line.lower() for keyword in food_keywords)
                    
                    # More lenient acceptance criteria
                    is_likely_product = (
                        contains_food_keyword or 
                        len(cleaned_line.split()) <= 5 or  # Slightly longer items allowed
                        starts_with_food or
                        re.search(r'^[A-Z][a-z]+', cleaned_line)  # Capitalized words often products
                    )
                    
                    if is_likely_product:
                        # Final cleanup
                        cleaned_line = cleaned_line.title()  # Proper case for better readability
                        items.append(cleaned_line)
        
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
                # Extract quantity, unit, and price
                quantity, unit, price = self._extract_quantity_and_price(item_text)
                
                # Find ingredient suggestions
                suggestions = await self._find_ingredient_suggestions(item_text)
                
                # Clean product name for better matching
                clean_name = re.sub(r'\s*\$\d+[.,]\d{2}\s*$', '', item_text)  # remove price
                clean_name = re.sub(r'\s*\(\d+.*?\)\s*', ' ', clean_name)  # remove quantity info
                clean_name = re.sub(r'\s+', ' ', clean_name).strip()  # normalize whitespace
                
                receipt_item = ReceiptItem(
                    detected_text=clean_name,
                    quantity=quantity,
                    unit=unit,
                    price=price,
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
    
    def _preprocess_image_for_ocr(self, image):
        """
        Preprocess image to improve OCR accuracy with balanced techniques.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to grayscale for better OCR performance
            gray_image = image.convert('L')
            
            # Balanced image enhancement pipeline
            from PIL import ImageEnhance, ImageFilter
            
            # Step 1: Moderate contrast enhancement
            contrast_enhancer = ImageEnhance.Contrast(gray_image)
            enhanced_image = contrast_enhancer.enhance(1.3)  # Moderate contrast boost
            
            # Step 2: Moderate sharpening
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
            sharpened_image = sharpness_enhancer.enhance(1.5)  # Light sharpening
            
            # Step 3: Noise reduction with very light blur
            denoised = sharpened_image.filter(ImageFilter.GaussianBlur(radius=0.3))
            
            # Step 4: Final light sharpening
            final_sharp = denoised.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Step 5: Scale image if it's too small (tesseract works better with larger images)
            width, height = final_sharp.size
            min_dimension = 800  # Reasonable minimum for good OCR
            
            if width < min_dimension or height < min_dimension:
                # Calculate scale factor
                scale_factor = max(min_dimension / width, min_dimension / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                # Use LANCZOS for high quality upscaling
                if hasattr(Image, 'Resampling'):
                    final_sharp = final_sharp.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    # Fallback for older PIL versions
                    final_sharp = final_sharp.resize((new_width, new_height), Image.LANCZOS)
                logger.info(f"Upscaled image from {width}x{height} to {new_width}x{new_height}")
            
            # Convert back to RGB for tesseract compatibility
            processed_image = final_sharp.convert('RGB')
            
            logger.info("Image preprocessing completed successfully")
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using basic preprocessing: {str(e)}")
            # Fallback to basic preprocessing
            try:
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Very basic enhancement
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(image)
                enhanced = enhancer.enhance(1.2)
                
                return enhanced
            except Exception as e2:
                logger.warning(f"Basic preprocessing also failed, using original: {str(e2)}")
                return image.convert('RGB') if image.mode != 'RGB' else image
    
    def _extract_quantity_and_price(self, item_text: str) -> Tuple[Optional[float], Optional[str], Optional[float]]:
        """
        Extract quantity, unit, and price from receipt item text.
        
        Args:
            item_text: Raw receipt item text
            
        Returns:
            Tuple of (quantity, unit, price)
        """
        quantity = None
        unit = None
        price = None
        
        try:
            # Extract price (at the end of line)
            price_match = re.search(r'\$(\d+[.,]\d{2})', item_text)
            if price_match:
                price_str = price_match.group(1).replace(',', '.')
                price = float(price_str)
            
            # Extract quantity and unit patterns
            quantity_patterns = [
                r'\((\d+(?:[.,]\d+)?)\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|ct|pcs?|pieces?|gallon|l|ml|liters?)\)',
                r'(\d+(?:[.,]\d+)?)\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|ct|pcs?|pieces?|gallon|l|ml|liters?)',
                r'\((\d+)\)',  # just number in parentheses
            ]
            
            for pattern in quantity_patterns:
                match = re.search(pattern, item_text, re.IGNORECASE)
                if match:
                    quantity_str = match.group(1).replace(',', '.')
                    quantity = float(quantity_str)
                    if len(match.groups()) > 1:
                        unit = match.group(2).lower()
                    break
            
            # Normalize units
            if unit:
                unit_mapping = {
                    'lbs': 'lb', 'pounds': 'lb', 'pound': 'lb',
                    'ounces': 'oz', 'ounce': 'oz',
                    'pieces': 'pcs', 'piece': 'pcs',
                    'bags': 'bag', 'counts': 'count',
                    'liters': 'l', 'liter': 'l'
                }
                unit = unit_mapping.get(unit, unit)
            
        except (ValueError, AttributeError) as e:
            logger.debug(f"Error extracting quantity/price from '{item_text}': {e}")
        
        return quantity, unit, price


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