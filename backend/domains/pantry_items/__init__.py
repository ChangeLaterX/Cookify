"""
Pantry Items Domain Package.
Provides functionality for managing user pantry items.
"""

# Avoid circular imports by not importing router by default
from .models import PantryItem
from .schemas import (
    PantryItemApiResponse,
    PantryItemCreate,
    PantryItemListApiResponse,
    PantryItemResponse,
    PantryItemUpdate,
)
from .services import (
    PantryItemError,
    PantryItemNotFoundError,
    PantryItemValidationError,
    create_pantry_item,
    delete_pantry_item,
    get_pantry_item_by_id,
    get_user_pantry_items,
    update_pantry_item,
)

# Router is available but not imported by default to avoid circular imports
# Use: from domains.pantry_items.routes import router

__all__ = [
    # Models
    "PantryItem",
    # Schemas
    "PantryItemCreate",
    "PantryItemUpdate",
    "PantryItemResponse",
    "PantryItemApiResponse",
    "PantryItemListApiResponse",
    # Services
    "get_user_pantry_items",
    "get_pantry_item_by_id",
    "create_pantry_item",
    "update_pantry_item",
    "delete_pantry_item",
    # Exceptions
    "PantryItemError",
    "PantryItemNotFoundError",
    "PantryItemValidationError",
]
