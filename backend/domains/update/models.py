"""
Update domain models.
"""

from enum import Enum
from typing import Optional
from datetime import datetime


class UpdateOperation(str, Enum):
    """Enumeration of available update operations."""

    INGREDIENT_CACHE = "ingredient_cache"
    ALL_CACHES = "all_caches"
    # Add more operations as needed


class UpdateStatusEnum(str, Enum):
    """Enumeration of update status values."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CacheType(str, Enum):
    """Enumeration of cache types."""

    INGREDIENT_NAMES = "ingredient_names"
    # Add more cache types as needed
