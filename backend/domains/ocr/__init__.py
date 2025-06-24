"""
Receipt Domain.

This domain handles receipt OCR processing and ingredient matching for the Cookify application.
"""

from .routes import router
from .schemas import (ErrorResponse, MessageResponse, OCRApiResponse,
                      OCRProcessedResponse, OCRTextResponse, ReceiptItem)
from .services import OCRError, extract_text_from_image, process_receipt_image

__all__ = [
    # Routes
    "router",
    # Schemas
    "OCRTextResponse",
    "OCRProcessedResponse",
    "ReceiptItem",
    "OCRApiResponse",
    "MessageResponse",
    "ErrorResponse",
    # Services
    "extract_text_from_image",
    "process_receipt_image",
    "OCRError",
]
