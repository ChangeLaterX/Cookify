"""
Pydantic Schemas for Pantry Items Domain.
Defines request/response models for the pantry items API.
"""

from datetime import date, datetime
from typing import List, Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PantryItemBase(BaseModel):
    """Base schema for pantry item data."""
    
    name: str = Field(..., description="Name of the pantry item", min_length=1, max_length=255)
    quantity: float = Field(..., description="Quantity of the item", gt=0)
    unit: str = Field(..., description="Unit of measurement", min_length=1, max_length=50)
    category: Optional[str] = Field(None, description="Category of the item", max_length=100)
    expiry_date: Optional[date] = Field(None, description="Expiry date of the item")
    ingredient_id: UUID = Field(..., description="ID of the ingredient from master table")

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


class PantryItemBulkCreate(BaseModel):
    """Schema for creating multiple pantry items."""
    
    items: List[PantryItemCreate] = Field(..., description="List of pantry items to create", min_length=1, max_length=50)
    
    @field_validator("items")
    @classmethod
    def validate_items_limit(cls, v):
        if len(v) > 50:
            raise ValueError("Cannot create more than 50 items at once")
        return v


class PantryItemUpdate(BaseModel):
    """Schema for updating a pantry item."""
    
    name: Optional[str] = Field(None, description="Name of the pantry item", min_length=1, max_length=255)
    quantity: Optional[float] = Field(None, description="Quantity of the item", gt=0)
    unit: Optional[str] = Field(None, description="Unit of measurement", min_length=1, max_length=50)
    category: Optional[str] = Field(None, description="Category of the item", max_length=100)
    expiry_date: Optional[date] = Field(None, description="Expiry date of the item")
    ingredient_id: Optional[UUID] = Field(None, description="ID of the ingredient from master table")

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


class PantryItemBulkUpdate(BaseModel):
    """Schema for updating multiple pantry items."""
    
    updates: Dict[UUID, PantryItemUpdate] = Field(..., description="Dictionary mapping item IDs to update data", min_length=1, max_length=50)
    
    @field_validator("updates")
    @classmethod
    def validate_updates_limit(cls, v):
        if len(v) > 50:
            raise ValueError("Cannot update more than 50 items at once")
        return v


class PantryItemBulkDelete(BaseModel):
    """Schema for deleting multiple pantry items."""
    
    item_ids: List[UUID] = Field(..., description="List of pantry item IDs to delete", min_length=1, max_length=50)
    
    @field_validator("item_ids")
    @classmethod
    def validate_ids_limit(cls, v):
        if len(v) > 50:
            raise ValueError("Cannot delete more than 50 items at once")
        return v


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


class PantryItemBulkResponse(BaseModel):
    """Response schema for bulk operations."""
    
    successful: List[PantryItemResponse] = Field(..., description="Successfully processed items")
    failed: List[Dict] = Field(..., description="Failed items with error details")
    total_processed: int = Field(..., description="Total number of items processed")
    success_count: int = Field(..., description="Number of successful operations")
    failure_count: int = Field(..., description="Number of failed operations")


class PantryItemBulkApiResponse(BaseModel):
    """API response wrapper for bulk operations."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[PantryItemBulkResponse] = Field(None, description="Bulk operation results")


# Statistics Schemas
class PantryStatsOverview(BaseModel):
    """Overview statistics for user's pantry."""
    
    total_items: int = Field(..., description="Total number of items in pantry")
    total_categories: int = Field(..., description="Number of different categories")
    items_expiring_soon: int = Field(..., description="Items expiring within 3 days")
    expired_items: int = Field(..., description="Items that have already expired")
    low_stock_items: int = Field(..., description="Items with quantity <= 1")
    estimated_total_value: float = Field(..., description="Estimated total value in cents")
    most_common_category: Optional[str] = Field(None, description="Category with most items")


class CategoryStats(BaseModel):
    """Statistics for a single category."""
    
    category: str = Field(..., description="Category name")
    item_count: int = Field(..., description="Number of items in category")
    percentage: float = Field(..., description="Percentage of total items")


class PantryCategoryStats(BaseModel):
    """Category breakdown statistics."""
    
    categories: List[CategoryStats] = Field(..., description="Statistics for each category")
    uncategorized_count: int = Field(..., description="Number of items without category")


class ExpiryItem(BaseModel):
    """Item with expiry information."""
    
    id: UUID = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    quantity: float = Field(..., description="Item quantity")
    unit: str = Field(..., description="Item unit")
    expiry_date: date = Field(..., description="Expiry date")
    days_until_expiry: int = Field(..., description="Days until expiry (negative if expired)")


class PantryExpiryReport(BaseModel):
    """Report of items by expiry status."""
    
    expiring_soon: List[ExpiryItem] = Field(..., description="Items expiring within 3 days")
    expired: List[ExpiryItem] = Field(..., description="Items that have already expired")
    fresh: List[ExpiryItem] = Field(..., description="Items with more than 7 days until expiry")


class LowStockItem(BaseModel):
    """Item with low stock."""
    
    id: UUID = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    quantity: float = Field(..., description="Current quantity")
    unit: str = Field(..., description="Item unit")
    category: Optional[str] = Field(None, description="Item category")
    suggested_restock_quantity: float = Field(..., description="Suggested quantity to restock")


class PantryLowStockReport(BaseModel):
    """Report of low stock items."""
    
    low_stock_items: List[LowStockItem] = Field(..., description="Items with low stock")
    threshold_used: float = Field(..., description="Threshold used for low stock detection")


class PantryStatsApiResponse(BaseModel):
    """API response wrapper for pantry statistics."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[PantryStatsOverview] = Field(None, description="Statistics data")


class PantryCategoryStatsApiResponse(BaseModel):
    """API response wrapper for category statistics."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[PantryCategoryStats] = Field(None, description="Category statistics")


class PantryExpiryApiResponse(BaseModel):
    """API response wrapper for expiry report."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[PantryExpiryReport] = Field(None, description="Expiry report data")


class PantryLowStockApiResponse(BaseModel):
    """API response wrapper for low stock report."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[PantryLowStockReport] = Field(None, description="Low stock report data")
