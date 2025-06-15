"""
Pydantic Schemas for Receipt Domain.
Defines request/response models for receipt OCR and processing endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============================================================================
# Request Schemas
# ============================================================================


class OCRRequest(BaseModel):
    """Schema for OCR processing request."""
    
    # Image data will be sent as multipart form data
    # This schema is for documentation purposes
    pass


# ============================================================================
# Response Schemas
# ============================================================================


class OCRTextResponse(BaseModel):
    """Schema for OCR text extraction response."""
    
    extracted_text: str = Field(..., description="Raw text extracted from the image")
    confidence: Optional[float] = Field(None, description="OCR confidence score (0-100)")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class OCRItemSuggestion(BaseModel):
    """Schema for ingredient matching suggestions."""
    
    ingredient_id: UUID = Field(..., description="ID of the suggested ingredient")
    ingredient_name: str = Field(..., description="Name of the suggested ingredient")
    confidence_score: float = Field(..., description="Matching confidence score (0-100)")
    detected_text: str = Field(..., description="Original text that was matched")


class ReceiptItem(BaseModel):
    """Schema for a single receipt item."""
    
    detected_text: str = Field(..., description="Original text detected in receipt")
    quantity: Optional[float] = Field(None, description="Detected quantity if available")
    unit: Optional[str] = Field(None, description="Detected unit if available")
    price: Optional[float] = Field(None, description="Detected price if available")
    suggestions: List[OCRItemSuggestion] = Field(
        default_factory=list, 
        description="Suggested ingredient matches"
    )


class OCRProcessedResponse(BaseModel):
    """Schema for processed OCR response with ingredient suggestions."""
    
    raw_text: str = Field(..., description="Raw extracted text")
    detected_items: List[ReceiptItem] = Field(
        default_factory=list,
        description="Processed receipt items with ingredient suggestions"
    )
    processing_time_ms: Optional[int] = Field(None, description="Total processing time in milliseconds")
    total_items_detected: int = Field(0, description="Number of items detected in receipt")


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    
    message: str = Field(..., description="Response message")
    success: bool = Field(True, description="Operation success status")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    success: bool = Field(False, description="Operation success status")


# ============================================================================
# Generic API Response Wrappers
# ============================================================================


class ApiResponse(BaseModel):
    """Generic API response wrapper."""
    
    success: bool = Field(..., description="Operation success status")
    data: Optional[dict] = Field(None, description="Response data")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")


class OCRApiResponse(BaseModel):
    """Specialized API response wrapper for OCR operations."""
    
    success: bool = Field(..., description="Operation success status")
    data: Optional[OCRProcessedResponse] = Field(None, description="OCR processing results")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")