"""
Receipt Domain.

This domain handles receipt OCR processing and ingredient matching for the Cookify application.
"""

from .routes import router
from .schemas import (
    OCRTextResponse,
    OCRProcessedResponse,
    ReceiptItem,
    OCRApiResponse,
    MessageResponse,
    ErrorResponse,
)
from .services import (
    extract_text_from_image,
    process_receipt_image,
    OCRError,
)

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
