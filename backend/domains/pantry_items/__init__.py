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
    # Bulk operations
    PantryItemBulkCreate,
    PantryItemBulkUpdate,
    PantryItemBulkDelete,
    PantryItemBulkApiResponse,
    # Statistics
    PantryStatsApiResponse,
    PantryCategoryStatsApiResponse,
    PantryExpiryApiResponse,
    PantryLowStockApiResponse,
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
    # Bulk operations
    bulk_create_pantry_items,
    bulk_update_pantry_items,
    bulk_delete_pantry_items,
    # Statistics
    get_pantry_stats_overview,
    get_pantry_category_stats,
    get_pantry_expiry_report,
    get_pantry_low_stock_report,
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
    # Bulk schemas
    "PantryItemBulkCreate",
    "PantryItemBulkUpdate", 
    "PantryItemBulkDelete",
    "PantryItemBulkApiResponse",
    # Statistics schemas
    "PantryStatsApiResponse",
    "PantryCategoryStatsApiResponse",
    "PantryExpiryApiResponse",
    "PantryLowStockApiResponse",
    # Services
    "get_user_pantry_items",
    "get_pantry_item_by_id",
    "create_pantry_item",
    "update_pantry_item",
    "delete_pantry_item",
    # Bulk services
    "bulk_create_pantry_items",
    "bulk_update_pantry_items",
    "bulk_delete_pantry_items",
    # Statistics services
    "get_pantry_stats_overview",
    "get_pantry_category_stats",
    "get_pantry_expiry_report",
    "get_pantry_low_stock_report",
    # Exceptions
    "PantryItemError",
    "PantryItemNotFoundError",
    "PantryItemValidationError",
]
