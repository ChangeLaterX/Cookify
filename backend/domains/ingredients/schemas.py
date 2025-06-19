"""
Pydantic Schemas for Ingredients Domain.
Defines request/response models for ingredient master data API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from core.config import settings


# ============================================================================
# Request Schemas
# ============================================================================


class IngredientMasterCreate(BaseModel):
    """Schema for creating a new master ingredient."""

    name: str = Field(..., min_length=1, max_length=255, description="Ingredient name")
    calories_per_100g: float = Field(..., ge=0, description="Calories per 100g")
    proteins_per_100g: float = Field(
        ..., ge=0, description="Proteins per 100g in grams"
    )
    fat_per_100g: float = Field(..., ge=0, description="Fat per 100g in grams")
    carbs_per_100g: float = Field(
        ..., ge=0, description="Carbohydrates per 100g in grams"
    )
    category: Optional[str] = Field(None, description="Ingredient category")

    @validator("name")
    def validate_name(cls, v):
        """Validate ingredient name is not empty after stripping."""
        if not v.strip():
            raise ValueError("Ingredient name cannot be empty")
        return v.strip()


class IngredientMasterUpdate(BaseModel):
    """Schema for updating an existing master ingredient."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Ingredient name"
    )
    calories_per_100g: Optional[float] = Field(
        None, ge=0, description="Calories per 100g"
    )
    proteins_per_100g: Optional[float] = Field(
        None, ge=0, description="Proteins per 100g in grams"
    )
    fat_per_100g: Optional[float] = Field(
        None, ge=0, description="Fat per 100g in grams"
    )
    carbs_per_100g: Optional[float] = Field(
        None, ge=0, description="Carbohydrates per 100g in grams"
    )
    category: Optional[str] = Field(None, description="Ingredient category")

    @validator("name")
    def validate_name(cls, v):
        """Validate ingredient name is not empty after stripping."""
        if v is not None and not v.strip():
            raise ValueError("Ingredient name cannot be empty")
        return v.strip() if v else None


class IngredientSearch(BaseModel):
    """Schema for ingredient search parameters."""

    q: str = Field(..., min_length=1, max_length=255, description="Search query")
    limit: Optional[int] = Field(
        default=settings.INGREDIENTS_SEARCH_DEFAULT_LIMIT, 
        ge=1, 
        le=settings.INGREDIENTS_SEARCH_MAX_LIMIT, 
        description="Maximum number of results"
    )
    offset: Optional[int] = Field(0, ge=0, description="Number of results to skip")


# ============================================================================
# Response Schemas
# ============================================================================


class IngredientMasterResponse(BaseModel):
    """Schema for ingredient master data in responses."""

    ingredient_id: UUID = Field(..., description="Ingredient unique identifier")
    name: str = Field(..., description="Ingredient name")
    calories_per_100g: float = Field(..., description="Calories per 100g")
    proteins_per_100g: float = Field(..., description="Proteins per 100g in grams")
    fat_per_100g: float = Field(..., description="Fat per 100g in grams")
    carbs_per_100g: float = Field(..., description="Carbohydrates per 100g in grams")
    category: Optional[str] = Field(None, description="Ingredient category")

    class Config:
        from_attributes = True


class IngredientListResponse(BaseModel):
    """Schema for paginated ingredient list responses."""

    ingredients: List[IngredientMasterResponse] = Field(
        ..., description="List of ingredients"
    )
    total: int = Field(..., description="Total number of ingredients")
    limit: int = Field(..., description="Maximum number of results per page")
    offset: int = Field(..., description="Number of results skipped")


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
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")


class IngredientResponse(ApiResponse):
    """API response for single ingredient operations."""

    data: Optional[IngredientMasterResponse] = Field(
        None, description="Ingredient data"
    )
    error: Optional[str] = Field(None, description="Error message if any")


class IngredientListApiResponse(ApiResponse):
    """API response for ingredient list operations."""

    data: Optional[IngredientListResponse] = Field(
        None, description="Ingredient list data"
    )
    error: Optional[str] = Field(None, description="Error message if any")
