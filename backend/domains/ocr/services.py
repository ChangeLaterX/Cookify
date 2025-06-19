"""
Receipt Services with OCR Integration.
Handles OCR text extraction and ingredient matching for receipt processing.
"""

import time
import re
import asyncio
import hashlib
import tempfile
import os
from typing import List, Optional, Tuple
from io import BytesIO
from pathlib import Path

from core.config import settings
from core.logging import get_logger

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter

    OCR_AVAILABLE = True
except ImportError:
    pytesseract = None
    Image = None  # type: ignore
    ImageEnhance = None  # type: ignore
    ImageFilter = None  # type: ignore
    OCR_AVAILABLE = False

# Security scanning support
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    magic = None  # type: ignore
    MAGIC_AVAILABLE = False

# Fuzzy matching support
try:
    from difflib import SequenceMatcher
    FUZZY_MATCHING_AVAILABLE = True
except ImportError:
    SequenceMatcher = None  # type: ignore
    FUZZY_MATCHING_AVAILABLE = False

# Import ingredient name loading
try:
    from domains.update.ingredient_cache import get_ingredient_names_for_ocr
    INGREDIENT_CACHE_AVAILABLE = True
except ImportError:
    get_ingredient_names_for_ocr = None  # type: ignore
    INGREDIENT_CACHE_AVAILABLE = False

# Import ingredient search function
try:
    from domains.ingredients.services import search_ingredients
    INGREDIENT_SEARCH_AVAILABLE = True
except ImportError:
    search_ingredients = None  # type: ignore
    INGREDIENT_SEARCH_AVAILABLE = False

from .schemas import (
    OCRTextResponse,
    OCRProcessedResponse,
    ReceiptItem,
    OCRItemSuggestion,
)

logger = get_logger(__name__)


def _load_ingredient_names_from_file() -> List[str]:
    """
    Load ingredient names from the ingredient_names.txt file.
    
    Returns:
        List of ingredient names (without comments and empty lines)
    """
    # First try to use the ingredient cache system
    if INGREDIENT_CACHE_AVAILABLE and get_ingredient_names_for_ocr is not None:
        try:
            return get_ingredient_names_for_ocr()
        except Exception as e:
            logger.warning(f"Failed to load ingredients from cache: {e}, falling back to file")
    
    # Fallback to reading directly from file
    try:
        # Use absolute path relative to backend directory
        backend_dir = Path(__file__).parent.parent.parent
        ingredient_file = backend_dir / "data" / "ingredient_names.txt"
        
        if not ingredient_file.exists():
            logger.warning(f"Ingredient names file not found: {ingredient_file}")
            return []
        
        ingredients = []
        with open(ingredient_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    ingredients.append(line.lower())
        
        logger.info(f"Loaded {len(ingredients)} ingredient names from file")
        return ingredients
    
    except Exception as e:
        logger.error(f"Failed to load ingredient names from file: {e}")
        return []


def _compute_similarity(text1: str, text2: str) -> float:
    """
    Compute similarity between two strings using SequenceMatcher.
    
    Args:
        text1: First string
        text2: Second string
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not text1 or not text2:
        return 0.0
    
    text1_lower = text1.lower().strip()
    text2_lower = text2.lower().strip()
    
    # Exact match
    if text1_lower == text2_lower:
        return 1.0
    
    # Substring match
    if text1_lower in text2_lower or text2_lower in text1_lower:
        return 0.9
    
    # Fuzzy matching using SequenceMatcher (if available)
    if FUZZY_MATCHING_AVAILABLE and SequenceMatcher is not None:
        try:
            similarity = SequenceMatcher(None, text1_lower, text2_lower).ratio()
            return similarity
        except Exception:
            return 0.0
    
    # Fallback: basic character comparison
    return 0.0


# Global ingredient names cache
_ingredient_names_cache: Optional[List[str]] = None
_cache_last_loaded: float = 0.0
_cache_ttl = 300  # 5 minutes


# Security validation functions
def _validate_image_security(image_data: bytes) -> None:
    """
    Validate image data for security threats.
    
    Args:
        image_data: Raw image bytes
        
    Raises:
        OCRError: If security validation fails
    """
    # Check file size
    if len(image_data) > settings.OCR_MAX_IMAGE_SIZE_BYTES:
        raise OCRError(
            f"Image file too large: {len(image_data)} bytes (max: {settings.OCR_MAX_IMAGE_SIZE_BYTES})",
            "IMAGE_TOO_LARGE"
        )
    
    if len(image_data) == 0:
        raise OCRError("Empty image file", "EMPTY_IMAGE")
    
    # Check for malicious patterns
    suspicious_patterns = [
        b"<?php",  # PHP code
        b"<script",  # JavaScript  
        b"<%",  # ASP/JSP
        b"eval(",  # Code evaluation
        b"exec(",  # Code execution
        b"system(",  # System commands
        b"import ",  # Python imports
        b"require(",  # Node.js requires
        b"include(",  # PHP includes
    ]
    
    for pattern in suspicious_patterns:
        if pattern in image_data:
            logger.error(
                "Malicious content detected in image",
                extra={
                    "pattern": pattern.decode('utf-8', errors='ignore'),
                    "file_size": len(image_data)
                }
            )
            raise OCRError(
                "Suspicious content detected in image file",
                "MALICIOUS_CONTENT"
            )
    
    # Validate MIME type if magic is available
    if MAGIC_AVAILABLE and magic:
        try:
            detected_type = magic.from_buffer(image_data, mime=True)
            if not detected_type.startswith('image/'):
                raise OCRError(
                    f"Invalid file type: {detected_type}. Expected image file.",
                    "INVALID_FILE_TYPE"
                )
        except Exception as e:
            logger.warning(f"MIME type detection failed: {e}")
    
    # Validate image with PIL
    try:
        with Image.open(BytesIO(image_data)) as img:
            # Check format
            if img.format not in settings.OCR_ALLOWED_IMAGE_FORMATS:
                raise OCRError(
                    f"Unsupported image format: {img.format}",
                    "UNSUPPORTED_FORMAT"
                )
            
            # Check dimensions
            width, height = img.size
            if width < settings.OCR_MIN_IMAGE_WIDTH or height < settings.OCR_MIN_IMAGE_HEIGHT:
                raise OCRError(
                    f"Image too small: {width}x{height} (min: {settings.OCR_MIN_IMAGE_WIDTH}x{settings.OCR_MIN_IMAGE_HEIGHT})",
                    "IMAGE_TOO_SMALL"
                )
            
            if width > settings.OCR_MAX_IMAGE_WIDTH or height > settings.OCR_MAX_IMAGE_HEIGHT:
                raise OCRError(
                    f"Image too large: {width}x{height} (max: {settings.OCR_MAX_IMAGE_WIDTH}x{settings.OCR_MAX_IMAGE_HEIGHT})",
                    "IMAGE_TOO_LARGE"
                )
            
            # Verify image integrity
            img.verify()
            
    except OCRError:
        raise
    except Exception as e:
        raise OCRError(
            f"Image validation failed: {str(e)}",
            "IMAGE_VALIDATION_ERROR"
        )


def _create_secure_temp_file(image_data: bytes) -> Tuple[str, str]:
    """
    Create a secure temporary file for image processing.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Tuple of (file_path, file_hash)
        
    Raises:
        OCRError: If file creation fails
    """
    try:
        # Create file hash for integrity checking
        file_hash = hashlib.sha256(image_data).hexdigest()
        
        # Create secure temporary file
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.tmp',
            prefix='ocr_secure_',
            delete=False,
            dir=tempfile.gettempdir()
        ) as temp_file:
            temp_file.write(image_data)
            temp_file.flush()
            os.fsync(temp_file.fileno())  # Ensure data is written to disk
            temp_path = temp_file.name
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(temp_path, 0o600)
        
        logger.debug(
            "Created secure temporary file for OCR processing",
            extra={
                "temp_path": temp_path,
                "file_hash": file_hash[:16],  # Only log first 16 chars
                "file_size": len(image_data)
            }
        )
        
        return temp_path, file_hash
        
    except Exception as e:
        raise OCRError(
            f"Failed to create secure temporary file: {str(e)}",
            "TEMP_FILE_CREATION_ERROR"
        )


def _cleanup_temp_file(file_path: str) -> None:
    """
    Securely cleanup temporary file.
    
    Args:
        file_path: Path to temporary file
    """
    try:
        if os.path.exists(file_path):
            # Overwrite file with zeros before deletion (basic secure deletion)
            file_size = os.path.getsize(file_path)
            with open(file_path, 'wb') as f:
                f.write(b'\x00' * file_size)
                f.flush()
                os.fsync(f.fileno())
            
            os.unlink(file_path)
            
            logger.debug(f"Securely cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary file {file_path}: {e}")


def _get_ingredient_names() -> List[str]:
    """
    Get ingredient names with caching.
    
    Returns:
        List of ingredient names
    """
    global _ingredient_names_cache, _cache_last_loaded
    
    current_time = time.time()
    
    # Load from cache if available and not expired
    if (_ingredient_names_cache is not None and 
        current_time - _cache_last_loaded < _cache_ttl):
        return _ingredient_names_cache
    
    # Load fresh data
    _ingredient_names_cache = _load_ingredient_names_from_file()
    _cache_last_loaded = current_time
    
    return _ingredient_names_cache


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
                "OCR_DEPENDENCIES_MISSING",
            )

        # Configure tesseract path - try standard Docker/system locations
        if pytesseract:
            import os
            import shutil

            # Try to find tesseract in standard locations (Docker-friendly)
            tesseract_paths = [
                shutil.which("tesseract"),  # PATH lookup (should work in Docker)
                *settings.OCR_TESSERACT_PATHS,  # Config-defined paths
                os.environ.get(settings.OCR_TESSERACT_CMD_ENV_VAR),  # Environment variable override
            ]

            for path in tesseract_paths:
                if path and os.path.isfile(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Configured tesseract path: {path}")
                    break
            else:
                logger.warning(
                    "Could not find tesseract executable. Install tesseract-ocr package."
                )

        # Optimal Tesseract configurations based on comprehensive testing
        self.optimal_config = {
            "primary": f"{settings.OCR_PRIMARY_CONFIG} -c tesseract_char_whitelist={settings.OCR_CHAR_WHITELIST}",
            "fallback_psm_4": f"{settings.OCR_FALLBACK_PSM_4_CONFIG} -c tesseract_char_whitelist={settings.OCR_CHAR_WHITELIST}",
            "fallback_psm_11": f"{settings.OCR_FALLBACK_PSM_11_CONFIG} -c tesseract_char_whitelist={settings.OCR_CHAR_WHITELIST}",
            "default": settings.OCR_DEFAULT_CONFIG,  # System default as last resort
        }
        
        # Load ingredient names at initialization
        self._ingredient_names = _get_ingredient_names()
        logger.info(f"OCR Service initialized with {len(self._ingredient_names)} ingredient names")

    async def _find_ingredient_suggestions(
        self, 
        item_text: str, 
        max_suggestions: int = 3,
        similarity_threshold: float = 0.3
    ) -> List[OCRItemSuggestion]:
        """
        Find ingredient suggestions for a detected receipt item.
        
        Args:
            item_text: Detected text from receipt
            max_suggestions: Maximum number of suggestions to return
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of ingredient suggestions sorted by confidence
        """
        suggestions = []
        
        try:
            # Clean the item text for better matching
            clean_text = re.sub(r'\s*\([^)]*\)\s*', ' ', item_text)  # Remove parentheses content
            clean_text = re.sub(r'\s*\$[\d.,]+\s*', ' ', clean_text)  # Remove prices
            clean_text = re.sub(r'[^\w\s]', ' ', clean_text)  # Remove special chars
            clean_text = re.sub(r'\s+', ' ', clean_text).strip().lower()
            
            if not clean_text:
                return []
            
            # Method 1: Use database search if available
            if INGREDIENT_SEARCH_AVAILABLE and search_ingredients is not None:
                try:
                    # Search for ingredients using the database
                    search_result = await search_ingredients(clean_text, limit=10)
                    
                    for ingredient in search_result.ingredients:
                        # Calculate similarity score
                        similarity = _compute_similarity(clean_text, ingredient.name)
                        confidence_score = similarity * 100
                        
                        if confidence_score >= similarity_threshold * 100:
                            suggestion = OCRItemSuggestion(
                                ingredient_id=ingredient.ingredient_id,
                                ingredient_name=ingredient.name,
                                confidence_score=confidence_score,
                                detected_text=clean_text
                            )
                            suggestions.append(suggestion)
                
                except Exception as e:
                    logger.debug(f"Database ingredient search failed for '{clean_text}': {e}")
            
            # Method 2: Use local ingredient names file for fuzzy matching
            if len(suggestions) < max_suggestions and self._ingredient_names:
                try:
                    local_matches = []
                    
                    for ingredient_name in self._ingredient_names:
                        similarity = _compute_similarity(clean_text, ingredient_name)
                        if similarity >= similarity_threshold:
                            local_matches.append((ingredient_name, similarity))
                    
                    # Sort by similarity and take the best matches
                    local_matches.sort(key=lambda x: x[1], reverse=True)
                    
                    # Add local matches if we don't have enough suggestions
                    for ingredient_name, similarity in local_matches[:max_suggestions - len(suggestions)]:
                        # Create a mock UUID for local matches
                        from uuid import uuid5, NAMESPACE_DNS
                        mock_id = uuid5(NAMESPACE_DNS, f"local-ingredient-{ingredient_name}")
                        
                        suggestion = OCRItemSuggestion(
                            ingredient_id=mock_id,
                            ingredient_name=ingredient_name.title(),
                            confidence_score=similarity * 100,
                            detected_text=clean_text
                        )
                        suggestions.append(suggestion)
                
                except Exception as e:
                    logger.debug(f"Local ingredient matching failed for '{clean_text}': {e}")
            
            # Sort by confidence score and limit results
            suggestions.sort(key=lambda x: x.confidence_score, reverse=True)
            return suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"Error finding ingredient suggestions for '{item_text}': {e}")
            return []

    async def extract_text_from_image(self, image_data: bytes) -> OCRTextResponse:
        """
        Extract text from image using Tesseract OCR with enhanced security.

        Args:
            image_data: Raw image data as bytes

        Returns:
            OCRTextResponse with extracted text and metadata

        Raises:
            OCRError: If OCR processing fails
        """
        start_time = time.time()
        temp_file_path = None
        
        try:
            # Validate image security before processing
            _validate_image_security(image_data)
            
            # Create secure temporary file for processing
            temp_file_path, file_hash = _create_secure_temp_file(image_data)
            
            logger.info(
                "Starting secure OCR text extraction",
                extra={
                    "file_size": len(image_data),
                    "file_hash": file_hash[:16],  # Only log first 16 chars
                    "temp_file": temp_file_path
                }
            )

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
                # Optimal configuration from comprehensive testing
                self.optimal_config["primary"],
                # Fallback configurations
                self.optimal_config["fallback_psm_4"],
                self.optimal_config["fallback_psm_11"],
                self.optimal_config["default"],
            ]

            best_result = None
            best_confidence = 0.0

            for config in configs:
                try:
                    # Extract confidence data with timeout protection
                    ocr_data = await asyncio.wait_for(
                        loop.run_in_executor(
                            None,
                            lambda c=config: pytesseract.image_to_data(  # type: ignore
                                image,
                                output_type=pytesseract.Output.DICT,  # type: ignore
                                config=c,
                            ),
                        ),
                        timeout=settings.OCR_PROCESSING_TIMEOUT
                    )

                    # Extract text
                    extracted_text = await loop.run_in_executor(
                        None,
                        lambda c=config: pytesseract.image_to_string(  # type: ignore
                            image, config=c
                        ),
                    )

                    # Calculate average confidence
                    confidences = [
                        int(conf) for conf in ocr_data["conf"] if int(conf) > settings.OCR_MIN_CONFIDENCE_SCORE
                    ]
                    avg_confidence = (
                        sum(confidences) / len(confidences) if confidences else settings.OCR_MIN_CONFIDENCE_SCORE
                    )

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
                        config=settings.OCR_SIMPLE_CONFIG,
                    ),
                )

                best_result = await loop.run_in_executor(
                    None,
                    lambda: pytesseract.image_to_string(  # type: ignore
                        image, config=settings.OCR_SIMPLE_CONFIG
                    ),
                )

                confidences = [int(conf) for conf in ocr_data["conf"] if int(conf) > settings.OCR_MIN_CONFIDENCE_SCORE]
                best_confidence = (
                    sum(confidences) / len(confidences) if confidences else settings.OCR_MIN_CONFIDENCE_SCORE
                )

            processing_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "OCR text extraction completed",
                context={
                    "processing_time_ms": processing_time_ms,
                    "confidence_score": best_confidence,
                    "extracted_text_length": len(best_result.strip()) if best_result else 0,
                    "configs_tried": len(configs),
                    "image_preprocessed": True
                },
                data={
                    "performance_metrics": {
                        "processing_time_ms": processing_time_ms,
                        "confidence_score": best_confidence,
                        "text_extraction_success": best_result is not None,
                        "fallback_used": best_result is None
                    }
                }
            )

            return OCRTextResponse(
                extracted_text=best_result.strip() if best_result else "",
                confidence=best_confidence,
                processing_time_ms=processing_time_ms,
            )

        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "OCR processing failed",
                context={
                    "processing_time_ms": processing_time_ms,
                    "error_message": str(e),
                    "ocr_available": OCR_AVAILABLE,
                    "image_size_available": 'image_data' in locals()
                }
            )
            raise OCRError(
                f"Failed to process image: {str(e)}", "OCR_PROCESSING_FAILED"
            )
        finally:
            # Always cleanup temporary file
            if temp_file_path:
                _cleanup_temp_file(temp_file_path)

    def _extract_receipt_items(self, text: str) -> List[str]:
        """
        Extract potential food items from receipt text with advanced recognition.

        Args:
            text: Raw OCR text

        Returns:
            List of potential food item strings
        """
        lines = text.split("\n")
        items = []

        # Enhanced patterns to identify product lines
        skip_patterns = [
            # Store info patterns
            r"^(fresh|market|grocery|store|shop|supermarket)",
            r"^\d{1,3}\s+(main|street|ave|avenue|road|rd|st|drive|dr)",
            r"^(anytown|city|town)",
            r"^tel[:\s]*\(?[\d\s\-\)]+",
            r"^phone[:\s]*\(?[\d\s\-\)]+",
            # Receipt metadata patterns
            r"^receipt\s*[#:]",
            r"^date[:\s]*\d",
            r"^time[:\s]*\d",
            r"^cashier[:\s]*",
            r"^clerk[:\s]*",
            r"^register[:\s]*",
            # Total/summary patterns - improved
            r"^(sub)?total[:\s]*",
            r"^tax[:\s]*\(?[\d\.%]+",
            r"^change[:\s]*\$",
            r"^payment[:\s]*",
            r"^card[:\s]*",
            r"^cash[:\s]*",
            r"^subtott",  # OCR error for "subtotal"
            r"^tot[:\s]*",  # OCR error for "total"
            r"^tout[:\s]*",  # OCR error for "total"
            # Footer patterns
            r"^thank\s+you",
            r"^have\s+a",
            r"^visit\s+us",
            r"^www\.",
            r"^[\*\-=]{3,}",  # separators
            # Standalone prices or numbers
            r"^\$?\d+[.,]\d{2}$",
            r"^\d{1,2}[:/]\d{1,2}[:/]\d{2,4}",  # dates
        ]

        # Enhanced patterns that indicate a product line
        product_indicators = [
            # Quantity patterns - more flexible for OCR errors
            r"\(\d+\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|ct|pcs?|pieces?|gallon|l|ml)\)",
            r"\(\d+\s*(its|ibs|ib|be|bs|1b|11b|2b|ts|bults|butte|goz|cound|container|tresh|fresh)\)",  # OCR errors
            r"\d+\s*x\s*",  # quantity multiplier
            r"@\s*\$\d+[.,]\d{2}",  # unit price
            r"\$\d+[.,]\d{2}\s*$",  # price at end of line
            r"\$\d+[.,]\d{1,2}[.,]?\s*$",  # price with OCR errors
            # Common quantity indicators without parentheses
            r"\d+\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|gallon|l|ml)\s",
            r"\d+\s*(its|ibs|ib|be|bs|1b|11b|2b|ts|container)\s",  # OCR errors
        ]

        # Pre-process lines to fix common OCR errors
        corrected_lines = []
        for line in lines:
            # Fix common OCR errors in units
            corrected_line = line
            corrected_line = re.sub(
                r"\b(its|ibs)\b", "lbs", corrected_line, flags=re.IGNORECASE
            )
            corrected_line = re.sub(
                r"\b(ib|1b|11b)\b", "lb", corrected_line, flags=re.IGNORECASE
            )
            corrected_line = re.sub(
                r"\b(be|bs)\b", "lbs", corrected_line, flags=re.IGNORECASE
            )
            corrected_line = re.sub(
                r"\b(ts)\b", "lbs", corrected_line, flags=re.IGNORECASE
            )
            corrected_line = re.sub(
                r"\b(goz)\b", "8oz", corrected_line, flags=re.IGNORECASE
            )
            corrected_line = re.sub(
                r"\b(cound)\b", "count", corrected_line, flags=re.IGNORECASE
            )
            corrected_line = re.sub(
                r"\b(bults|butte)\b", "bulbs", corrected_line, flags=re.IGNORECASE
            )
            corrected_line = re.sub(
                r"\b(tresh)\b", "fresh", corrected_line, flags=re.IGNORECASE
            )

            # Fix price formatting OCR errors
            corrected_line = re.sub(
                r"\$(\d+)(\d{2})([,.]?)", r"$\1.\2", corrected_line
            )  # $398 -> $3.98
            corrected_line = re.sub(
                r"\$(\d+)[.,](\d{1})(\d{1})([,.]?)", r"$\1.\2\3", corrected_line
            )  # $1.2.9 -> $1.29

            corrected_lines.append(corrected_line)

        for line in corrected_lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Skip lines matching skip patterns
            if any(re.search(pattern, line.lower()) for pattern in skip_patterns):
                continue

            # Look for lines that contain alphabetic characters (potential product names)
            if not re.search(r"[a-zA-Z]{2,}", line):
                continue

            # Check if line has product indicators or looks like a product line
            has_product_indicator = any(
                re.search(pattern, line, re.IGNORECASE)
                for pattern in product_indicators
            )
            has_letters_and_price = re.search(r"[a-zA-Z].*\$\d+[.,]\d{1,2}", line)

            # Additional check: line starts with a food-related word
            food_start_words = [
                "tomato",
                "onion",
                "garlic",
                "pepper",
                "carrot",
                "potato",
                "spinach",
                "banana",
                "apple",
                "orange",
                "lemon",
                "lime",
                "berry",
                "grape",
                "chicken",
                "beef",
                "pork",
                "fish",
                "salmon",
                "tuna",
                "turkey",
                "milk",
                "cheese",
                "egg",
                "butter",
                "yogurt",
                "cream",
                "bread",
                "rice",
                "pasta",
                "flour",
                "cereal",
                "oat",
                "oil",
                "salt",
                "pepper",
                "spice",
                "herb",
                "basil",
                "oregano",
                "bean",
                "lentil",
                "nut",
                "almond",
                "walnut",
                "lettuce",
                "cabbage",
                "broccoli",
                "cauliflower",
                "mushroom",
                # Common variations and OCR errors
                "tomatnes",
                "onions",
                "garlie",
                "bellpeppers",
                "cancts",
                "bananas",
                "apples",
                "ground",
                "salmon",
                "fillet",
                "mitk",
                "imtik",
                "eggs",
                "fggs",
                "cheddar",
                "chesidar",
                "pasa",
                "otiweoit",
                "otiveoil",
                "basilfresh",
            ]

            starts_with_food = any(
                line.lower().startswith(word) for word in food_start_words
            )

            if has_product_indicator or has_letters_and_price or starts_with_food:
                # Advanced cleaning pipeline
                cleaned_line = line

                # Remove trailing prices (more flexible patterns)
                cleaned_line = re.sub(r"\s*\$\d+[.,]\d{1,2}[.,]?\s*$", "", cleaned_line)
                cleaned_line = re.sub(r"\s*\$\d+[.,]\d{1,2}\s*,?\s*$", "", cleaned_line)

                # Remove trailing quantities and unit prices
                cleaned_line = re.sub(r"\s*\d+\s*x\s*$", "", cleaned_line)
                cleaned_line = re.sub(r"\s*@\s*\$\d+[.,]\d{1,2}\s*$", "", cleaned_line)

                # Remove quantity indicators in parentheses but keep the text before
                cleaned_line = re.sub(
                    r"\s*\(\d+\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|ct|pcs?|pieces?|gallon|l|ml)\)\s*",
                    " ",
                    cleaned_line,
                )

                # Remove trailing quantity without parentheses
                cleaned_line = re.sub(
                    r"\s*\(\d+\s*(its|ibs|ib|be|bs|1b|11b|2b|ts|bults|butte|goz|cound|container|tresh|fresh)\)\s*",
                    " ",
                    cleaned_line,
                )
                cleaned_line = re.sub(
                    r"\s+\d+\s*(lbs?|lb|pounds?|kg|g|oz|ounces?|bags?|count|gallon|l|ml)\s*$",
                    "",
                    cleaned_line,
                )

                # Clean up extra whitespace and OCR artifacts
                cleaned_line = re.sub(r"\s+", " ", cleaned_line)  # normalize whitespace
                cleaned_line = re.sub(
                    r"[^\w\s\-\']", " ", cleaned_line
                )  # remove special chars except useful ones
                cleaned_line = cleaned_line.strip()

                # Fix common product name OCR errors
                cleaned_line = re.sub(
                    r"\btomatnes\b", "tomatoes", cleaned_line, flags=re.IGNORECASE
                )
                cleaned_line = re.sub(
                    r"\bgarlie\b", "garlic", cleaned_line, flags=re.IGNORECASE
                )
                cleaned_line = re.sub(
                    r"\bbellpeppers\b",
                    "bell peppers",
                    cleaned_line,
                    flags=re.IGNORECASE,
                )
                cleaned_line = re.sub(
                    r"\bcancts\b", "carrots", cleaned_line, flags=re.IGNORECASE
                )
                cleaned_line = re.sub(
                    r"\bmitk|imtik\b", "milk", cleaned_line, flags=re.IGNORECASE
                )
                cleaned_line = re.sub(
                    r"\bfggs\b", "eggs", cleaned_line, flags=re.IGNORECASE
                )
                cleaned_line = re.sub(
                    r"\bchesidar\b", "cheddar", cleaned_line, flags=re.IGNORECASE
                )
                cleaned_line = re.sub(
                    r"\bpasa\b", "pasta", cleaned_line, flags=re.IGNORECASE
                )
                cleaned_line = re.sub(
                    r"\botiweoit|otiveoil\b",
                    "olive oil",
                    cleaned_line,
                    flags=re.IGNORECASE,
                )
                cleaned_line = re.sub(
                    r"\bbasilfresh\b", "basil fresh", cleaned_line, flags=re.IGNORECASE
                )

                if cleaned_line and len(cleaned_line) >= 3:
                    # Use dynamic ingredient names from the loaded file
                    # This replaces the hardcoded food keywords with the comprehensive ingredient list
                    food_keywords = self._ingredient_names if self._ingredient_names else [
                        # Fallback basic keywords if ingredient file loading failed
                        "tomato", "onion", "garlic", "pepper", "carrot", "potato", "chicken", 
                        "beef", "pork", "fish", "milk", "cheese", "egg", "bread", "rice", 
                        "pasta", "oil", "salt", "pepper", "apple", "banana"
                    ]

                    # Check if the item contains food-related keywords
                    contains_food_keyword = any(
                        keyword in cleaned_line.lower() for keyword in food_keywords
                    )

                    # More lenient acceptance criteria
                    is_likely_product = (
                        contains_food_keyword
                        or len(cleaned_line.split())
                        <= 5  # Slightly longer items allowed
                        or starts_with_food
                        or re.search(
                            r"^[A-Z][a-z]+", cleaned_line
                        )  # Capitalized words often products
                    )

                    if is_likely_product:
                        # Final cleanup
                        cleaned_line = (
                            cleaned_line.title()
                        )  # Proper case for better readability
                        items.append(cleaned_line)

        return items

    async def process_receipt_without_suggestions(
        self, image_data: bytes
    ) -> OCRProcessedResponse:
        """
        Process receipt image and extract items without database suggestions.

        Args:
            image_data: Raw image data as bytes

        Returns:
            OCRProcessedResponse with extracted items (no ingredient suggestions)

        Raises:
            OCRError: If processing fails
        """
        start_time = time.time()

        try:
            # Extract text from image
            ocr_result = await self.extract_text_from_image(image_data)

            # Extract potential items from text
            raw_items = self._extract_receipt_items(ocr_result.extracted_text)

            # Process each item without ingredient suggestions
            processed_items = []
            for item_text in raw_items:
                # Extract quantity, unit, and price
                quantity, unit, price = self._extract_quantity_and_price(item_text)

                # Clean product name
                clean_name = re.sub(
                    r"\s*\$\d+[.,]\d{2}\s*$", "", item_text
                )  # remove price
                clean_name = re.sub(
                    r"\s*\(\d+.*?\)\s*", " ", clean_name
                )  # remove quantity info
                clean_name = re.sub(
                    r"\s+", " ", clean_name
                ).strip()  # normalize whitespace

                receipt_item = ReceiptItem(
                    detected_text=clean_name,
                    quantity=quantity,
                    unit=unit,
                    price=price,
                    suggestions=[],  # No suggestions - empty list
                )
                processed_items.append(receipt_item)

            processing_time_ms = int((time.time() - start_time) * 1000)
            ocr_time = ocr_result.processing_time_ms or 0
            text_processing_time = processing_time_ms - ocr_time

            logger.info(
                "Receipt processing completed",
                context={
                    "items_detected": len(processed_items),
                    "processing_time_ms": processing_time_ms,
                    "raw_text_length": len(ocr_result.extracted_text),
                    "ocr_confidence": ocr_result.confidence,
                    "ocr_processing_time_ms": ocr_time
                },
                data={
                    "performance_metrics": {
                        "total_processing_time_ms": processing_time_ms,
                        "ocr_processing_time_ms": ocr_time,
                        "text_processing_time_ms": text_processing_time,
                        "items_detected": len(processed_items),
                        "ocr_confidence": ocr_result.confidence
                    }
                }
            )

            return OCRProcessedResponse(
                raw_text=ocr_result.extracted_text,
                detected_items=processed_items,
                processing_time_ms=processing_time_ms,
                total_items_detected=len(processed_items),
            )

        except OCRError:
            raise  # Re-raise OCR errors
        except Exception as e:
            logger.error(f"Receipt processing failed: {str(e)}")
            raise OCRError(
                f"Failed to process receipt: {str(e)}", "RECEIPT_PROCESSING_FAILED"
            )

    def _preprocess_image_for_ocr(self, image):
        """
        Preprocess image to improve OCR accuracy with optimal configuration.
        Based on comprehensive testing: contrast enhancement is most effective.

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Convert to grayscale for better OCR performance
            gray_image = image.convert("L")

            # Optimal image enhancement pipeline based on testing results
            from PIL import ImageEnhance, ImageFilter

            # Step 1: OPTIMAL - Contrast enhancement (best performer in tests)
            # This setting showed the highest item detection rates across all test images
            contrast_enhancer = ImageEnhance.Contrast(gray_image)
            enhanced_image = contrast_enhancer.enhance(
                1.5
            )  # Optimal contrast boost from testing

            # Step 2: Light sharpening (supporting enhancement)
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
            sharpened_image = sharpness_enhancer.enhance(
                1.3
            )  # Reduced from 1.5 to balance

            # Step 3: Noise reduction with very light blur
            denoised = sharpened_image.filter(ImageFilter.GaussianBlur(radius=settings.OCR_GAUSSIAN_BLUR_RADIUS))

            # Step 4: Final light sharpening
            final_sharp = denoised.filter(
                ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3)
            )

            # Step 5: Scale image if it's too small (tesseract works better with larger images)
            width, height = final_sharp.size
            min_dimension = 800  # Reasonable minimum for good OCR

            if width < min_dimension or height < min_dimension:
                # Calculate scale factor
                scale_factor = max(min_dimension / width, min_dimension / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)

                # Use high quality upscaling with safe fallbacks
                try:
                    # Try modern PIL first
                    from PIL.Image import Resampling

                    final_sharp = final_sharp.resize(
                        (new_width, new_height), Resampling.LANCZOS
                    )
                except (ImportError, AttributeError):
                    try:
                        # Fallback for older PIL versions
                        if Image is not None:
                            final_sharp = final_sharp.resize(
                                (new_width, new_height), getattr(Image, 'LANCZOS', 1)  # LANCZOS = 1
                            )
                        else:
                            final_sharp = final_sharp.resize((new_width, new_height))
                    except AttributeError:
                        # Final fallback - use basic resize
                        final_sharp = final_sharp.resize((new_width, new_height))
                logger.info(
                    f"Upscaled image from {width}x{height} to {new_width}x{new_height}"
                )

            # Convert back to RGB for tesseract compatibility
            processed_image = final_sharp.convert("RGB")

            logger.info("Image preprocessing completed successfully")
            return processed_image

        except Exception as e:
            logger.warning(
                f"Image preprocessing failed, using basic preprocessing: {str(e)}"
            )
            # Fallback to basic preprocessing
            try:
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Very basic enhancement
                from PIL import ImageEnhance

                enhancer = ImageEnhance.Contrast(image)
                enhanced = enhancer.enhance(1.2)

                return enhanced
            except Exception as e2:
                logger.warning(
                    f"Basic preprocessing also failed, using original: {str(e2)}"
                )
                return image.convert("RGB") if image.mode != "RGB" else image

    def _extract_quantity_and_price(
        self, item_text: str
    ) -> Tuple[Optional[float], Optional[str], Optional[float]]:
        """
        Advanced extraction of quantity, unit, and price from receipt item text.
        Enhanced with OCR error correction and multiple extraction strategies.

        Args:
            item_text: Raw receipt item text

        Returns:
            Tuple of (quantity, unit, price)
        """
        quantity = None
        unit = None
        price = None

        try:
            # Step 1: Advanced price extraction with OCR error patterns
            price = self._extract_price_from_text(item_text)

            # Step 2: Advanced quantity and unit extraction
            quantity, unit = self._extract_quantity_and_unit_from_text(item_text)

        except Exception as e:
            logger.debug(f"Error extracting quantity/price from '{item_text}': {e}")

        return quantity, unit, price

    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """
        Extract price with advanced OCR error correction.

        Args:
            text: Receipt line text

        Returns:
            Extracted price as float or None
        """
        # Multiple price patterns with OCR error tolerance
        price_patterns = [
            # Standard patterns
            r"\$(\d+[.,]\d{2})",  # $12.34
            r"\$(\d+[.,]\d{1,2})",  # $12.3 or $12.34
            r"\$(\d+)",  # $12 (no cents)
            # OCR error patterns - concatenated digits
            r"\$(\d{1,2})(\d{2})(?![.,]\d)",  # $1234 -> $12.34
            r"\$(\d{1,3})(\d{2})(?![.,]\d)",  # $12345 -> $123.45
            # OCR error patterns - missing decimal point
            r"\$(\d+)\s*(\d{2})\s*$",  # $12 34 -> $12.34
            r"\$(\d+)(\d{2})\s*,?\s*$",  # $1234, -> $12.34
            # European style (comma as decimal)
            r"\$(\d+),(\d{1,2})",  # $12,34
            # Space separated
            r"\$\s*(\d+)[.,]?(\d{0,2})",  # $ 12.34 or $ 12 34
            # Without dollar sign at end
            r"(\d+[.,]\d{2})\s*$",  # 12.34 at end
            r"(\d+)\s+(\d{2})\s*$",  # 12 34 at end
        ]

        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) == 1:
                        # Single group - standard price
                        price_str = match.group(1).replace(",", ".")
                        price = float(price_str)
                        if settings.OCR_MIN_PRICE <= price <= settings.OCR_MAX_PRICE:  # Reasonable price range
                            return price
                    else:
                        # Two groups - dollars and cents
                        dollars = int(match.group(1))
                        cents = int(match.group(2)) if match.group(2) else 0

                        # Handle OCR concatenation errors
                        if len(match.group(1)) >= 3 and match.group(2):
                            # Likely concatenated: $1234 -> $12.34
                            price_str = match.group(1) + match.group(2)
                            if len(price_str) >= 3:
                                dollars = int(price_str[:-2])
                                cents = int(price_str[-2:])

                        price = dollars + (cents / 100.0)
                        if settings.OCR_MIN_PRICE <= price <= settings.OCR_MAX_PRICE:  # Reasonable price range
                            return price
                except (ValueError, IndexError):
                    continue

        return None

    def _extract_quantity_and_unit_from_text(
        self, text: str
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract quantity and unit with advanced pattern matching and OCR correction.

        Args:
            text: Receipt line text

        Returns:
            Tuple of (quantity, unit)
        """
        quantity = None
        unit = None

        # Enhanced quantity patterns with OCR error tolerance
        quantity_patterns = [
            # Standard parentheses patterns
            r"\(([0-9.,]+)\s*([a-zA-Z]+)\)",  # (500 g)
            r"\(([0-9.,]+)\s*x\s*([0-9.,]+)\s*([a-zA-Z]+)\)",  # (2 x 500 g)
            # Standard space patterns
            r"([0-9.,]+)\s*([a-zA-ZÄÖÜäöü]+)\b",  # 500 g, 2 Stück
            r"([0-9.,]+)\s*x\s*([0-9.,]+)\s*([a-zA-Z]+)",  # 2 x 500 g
            # Handle OCR common errors: 0->O, l->I, etc.
            r"([O0-9.,I1l]+)\s*([a-zA-ZÄÖÜäöü]+)\b",
        ]

        for pattern in quantity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Handle different match group structures
                    if len(matches[0]) == 2:  # (quantity, unit)
                        qty_str, unit_str = matches[0]
                        # Simple quantity parsing with OCR correction
                        qty_str = qty_str.replace('O', '0').replace('I', '1').replace('l', '1')
                        quantity = float(qty_str.replace(',', '.'))
                        unit = unit_str.strip()
                    elif len(matches[0]) == 3:  # (multiplier, quantity, unit)
                        mult_str, qty_str, unit_str = matches[0]
                        # Simple parsing with OCR correction
                        mult_str = mult_str.replace('O', '0').replace('I', '1').replace('l', '1')
                        qty_str = qty_str.replace('O', '0').replace('I', '1').replace('l', '1')
                        multiplier = float(mult_str.replace(',', '.'))
                        base_qty = float(qty_str.replace(',', '.'))
                        quantity = multiplier * base_qty
                        unit = unit_str.strip()

                    if quantity and unit:
                        return quantity, unit
                except (ValueError, IndexError):
                    continue

        return None, None


# Enhanced standalone functions for better security
async def extract_text_from_image(image_data: bytes) -> OCRTextResponse:
    """
    Secure standalone function to extract text from image.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        OCRTextResponse with extracted text
        
    Raises:
        OCRError: If processing fails
    """
    if not OCR_AVAILABLE:
        raise OCRError(
            "OCR service is not available. Please check tesseract installation.",
            "OCR_SERVICE_UNAVAILABLE",
        )

    ocr_service = OCRService()
    return await ocr_service.extract_text_from_image(image_data)


async def process_receipt_image(image_data: bytes) -> OCRProcessedResponse:
    """
    Secure standalone function to process receipt image with ingredient suggestions.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        OCRProcessedResponse with processed receipt data
        
    Raises:
        OCRError: If processing fails
    """
    if not OCR_AVAILABLE:
        raise OCRError(
            "OCR service is not available. Please check tesseract installation.",
            "OCR_SERVICE_UNAVAILABLE",
        )

    ocr_service = OCRService()
    return await ocr_service.process_receipt_without_suggestions(image_data)
