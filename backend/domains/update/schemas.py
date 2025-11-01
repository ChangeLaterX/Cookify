"""
Update schemas for cache refresh operations.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class UpdateResponse(BaseModel):
    """Base response for update operations."""

    success: bool = Field(..., description="Whether the update was successful")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the update was performed"
    )
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional details about the update"
    )


class IngredientCacheUpdateResponse(UpdateResponse):
    """Response for ingredient cache updates."""

    ingredient_count: Optional[int] = Field(
        None, description="Number of ingredients in the updated cache"
    )
    cache_file_path: Optional[str] = Field(None, description="Path to the updated cache file")
    last_database_update: Optional[datetime] = Field(
        None, description="Last database update timestamp"
    )


class UpdateStatus(BaseModel):
    """Status information for update operations."""

    operation: str = Field(..., description="Name of the operation")
    status: str = Field(..., description="Current status (pending, running, completed, failed)")
    started_at: Optional[datetime] = Field(None, description="When the operation started")
    completed_at: Optional[datetime] = Field(None, description="When the operation completed")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")
