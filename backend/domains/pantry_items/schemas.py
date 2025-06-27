"""
Pydantic Schemas for Pantry Items Domain.
Defines request/response models for the pantry items API.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PantryItemBase(BaseModel):
    """Base schema for pantry item data."""
    
    name: str = Field(..., description="Name of the pantry item", min_length=1, max_length=255)
    quantity: float = Field(..., description="Quantity of the item", gt=0)
    unit: str = Field(..., description="Unit of measurement", min_length=1, max_length=50)
    category: Optional[str] = Field(None, description="Category of the item", max_length=100)
    expiry_date: Optional[date] = Field(None, description="Expiry date of the item")

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("name", "unit")
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class PantryItemCreate(PantryItemBase):
    """Schema for creating a new pantry item."""
    pass


class PantryItemUpdate(BaseModel):
    """Schema for updating a pantry item."""
    
    name: Optional[str] = Field(None, description="Name of the pantry item", min_length=1, max_length=255)
    quantity: Optional[float] = Field(None, description="Quantity of the item", gt=0)
    unit: Optional[str] = Field(None, description="Unit of measurement", min_length=1, max_length=50)
    category: Optional[str] = Field(None, description="Category of the item", max_length=100)
    expiry_date: Optional[date] = Field(None, description="Expiry date of the item")

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("name", "unit")
    @classmethod
    def validate_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Field cannot be empty")
        return v.strip() if v else v


class PantryItemResponse(PantryItemBase):
    """Schema for pantry item response."""
    
    id: UUID = Field(..., description="Unique identifier of the pantry item")
    user_id: UUID = Field(..., description="ID of the user who owns this item")
    added_at: datetime = Field(..., description="When the item was added to pantry")

    class Config:
        from_attributes = True


class PantryItemListResponse(BaseModel):
    """Schema for pantry item list response."""
    
    items: List[PantryItemResponse] = Field(..., description="List of pantry items")
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PantryItemApiResponse(BaseModel):
    """API response wrapper for pantry item operations."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[PantryItemResponse] = Field(None, description="Pantry item data")


class PantryItemListApiResponse(BaseModel):
    """API response wrapper for pantry item list operations."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[PantryItemListResponse] = Field(None, description="Pantry items data")


class MessageResponse(BaseModel):
    """Generic message response."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    success: bool = Field(False, description="Operation success status")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")
    details: Optional[dict] = Field(None, description="Additional error details")
