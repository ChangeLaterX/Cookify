"""
Business Logic for Pantry Items Domain.
Handles all pantry item operations and database interactions.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from supabase._sync.client import SyncClient

from core.logging import get_logger

from .schemas import PantryItemCreate, PantryItemUpdate


class PantryItemData:
    """Simple data class for pantry item data transfer."""
    
    def __init__(
        self,
        item_id: UUID,
        user_id: UUID,
        name: str,
        quantity: float,
        unit: str,
        category: Optional[str],
        expiry_date: Optional[date],
        added_at: datetime,
    ):
        self.id = item_id
        self.user_id = user_id
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.category = category
        self.expiry_date = expiry_date
        self.added_at = added_at

logger = get_logger(__name__)


class PantryItemError(Exception):
    """Base exception for pantry item operations."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PantryItemNotFoundError(PantryItemError):
    """Raised when a pantry item is not found."""
    
    def __init__(self, message: str = "Pantry item not found"):
        super().__init__(message)


class PantryItemValidationError(PantryItemError):
    """Raised when pantry item validation fails."""
    
    def __init__(self, message: str = "Validation error"):
        super().__init__(message)


async def get_user_pantry_items(
    user_id: UUID,
    supabase: SyncClient,
    page: int = 1,
    per_page: int = 50,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[List[PantryItemData], int]:
    """
    Get all pantry items for a specific user with pagination and filtering.
    
    Args:
        user_id: ID of the user
        supabase: Supabase client
        page: Page number (1-based)
        per_page: Items per page
        category: Filter by category (optional)
        search: Search in item names (optional)
        
    Returns:
        Tuple of (items_list, total_count)
    """
    try:
        logger.info(f"Fetching pantry items for user {user_id}, page {page}, per_page {per_page}")
        
        # Build query
        query = supabase.table("pantry_items").select("*").eq("user_id", str(user_id))
        
        # Add filters
        if category:
            query = query.eq("category", category)
        
        if search:
            query = query.ilike("name", f"%{search}%")
        
        # Get total count first
        count_response = query.execute()
        total_count = len(count_response.data) if count_response.data else 0
        
        # Apply pagination and ordering
        offset = (page - 1) * per_page
        query = query.order("added_at", desc=True).range(offset, offset + per_page - 1)
        
        response = query.execute()
        
        if not response.data:
            logger.info(f"No pantry items found for user {user_id}")
            return [], 0
        
        # Convert to PantryItemData objects
        items = []
        for item_data in response.data:
            items.append(_dict_to_pantry_item_data(item_data))
        
        logger.info(f"Retrieved {len(items)} pantry items for user {user_id}")
        return items, total_count
        
    except Exception as e:
        logger.error(f"Error fetching pantry items for user {user_id}: {str(e)}")
        raise PantryItemError(f"Failed to fetch pantry items: {str(e)}")


async def get_pantry_item_by_id(
    item_id: UUID,
    user_id: UUID,
    supabase: SyncClient,
) -> PantryItemData:
    """
    Get a specific pantry item by ID (user can only access their own items).
    
    Args:
        item_id: ID of the pantry item
        user_id: ID of the user (for authorization)
        supabase: Supabase client
        
    Returns:
        PantryItemData object
    """
    try:
        logger.info(f"Fetching pantry item {item_id} for user {user_id}")
        
        response = supabase.table("pantry_items").select("*").eq("id", str(item_id)).eq("user_id", str(user_id)).execute()
        
        if not response.data:
            logger.warning(f"Pantry item {item_id} not found for user {user_id}")
            raise PantryItemNotFoundError(f"Pantry item with ID {item_id} not found")
        
        item = _dict_to_pantry_item_data(response.data[0])
        logger.info(f"Retrieved pantry item {item_id} for user {user_id}")
        return item
        
    except PantryItemNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching pantry item {item_id}: {str(e)}")
        raise PantryItemError(f"Failed to fetch pantry item: {str(e)}")


async def create_pantry_item(
    user_id: UUID,
    item_data: PantryItemCreate,
    supabase: SyncClient,
) -> PantryItemData:
    """
    Create a new pantry item for a user.
    
    Args:
        user_id: ID of the user
        item_data: Pantry item creation data
        supabase: Supabase client
        
    Returns:
        Created PantryItemData object
    """
    try:
        logger.info(f"Creating pantry item '{item_data.name}' for user {user_id}")
        
        # Prepare data for insertion
        insert_data = {
            "user_id": str(user_id),
            "name": item_data.name,
            "quantity": item_data.quantity,
            "unit": item_data.unit,
            "category": item_data.category,
            "expiry_date": item_data.expiry_date.isoformat() if item_data.expiry_date else None,
            "added_at": datetime.utcnow().isoformat(),
        }
        
        response = supabase.table("pantry_items").insert(insert_data).execute()
        
        if not response.data:
            logger.error(f"Failed to create pantry item for user {user_id}")
            raise PantryItemError("Failed to create pantry item")
        
        item = _dict_to_pantry_item_data(response.data[0])
        logger.info(f"Created pantry item {item.id} for user {user_id}")
        return item
        
    except Exception as e:
        logger.error(f"Error creating pantry item for user {user_id}: {str(e)}")
        raise PantryItemError(f"Failed to create pantry item: {str(e)}")


async def update_pantry_item(
    item_id: UUID,
    user_id: UUID,
    item_data: PantryItemUpdate,
    supabase: SyncClient,
) -> PantryItemData:
    """
    Update a pantry item (user can only update their own items).
    
    Args:
        item_id: ID of the pantry item
        user_id: ID of the user (for authorization)
        item_data: Updated pantry item data
        supabase: Supabase client
        
    Returns:
        Updated PantryItemData object
    """
    try:
        logger.info(f"Updating pantry item {item_id} for user {user_id}")
        
        # First check if item exists and belongs to user
        await get_pantry_item_by_id(item_id, user_id, supabase)
        
        # Prepare update data (only include fields that are not None)
        update_data = {}
        if item_data.name is not None:
            update_data["name"] = item_data.name
        if item_data.quantity is not None:
            update_data["quantity"] = float(item_data.quantity)
        if item_data.unit is not None:
            update_data["unit"] = item_data.unit
        if item_data.category is not None:
            update_data["category"] = item_data.category
        if item_data.expiry_date is not None:
            update_data["expiry_date"] = item_data.expiry_date.isoformat()
        
        if not update_data:
            logger.warning(f"No update data provided for pantry item {item_id}")
            raise PantryItemValidationError("No update data provided")
        
        response = supabase.table("pantry_items").update(update_data).eq("id", str(item_id)).eq("user_id", str(user_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to update pantry item {item_id}")
            raise PantryItemError("Failed to update pantry item")
        
        item = _dict_to_pantry_item_data(response.data[0])
        logger.info(f"Updated pantry item {item_id} for user {user_id}")
        return item
        
    except (PantryItemNotFoundError, PantryItemValidationError):
        raise
    except Exception as e:
        logger.error(f"Error updating pantry item {item_id}: {str(e)}")
        raise PantryItemError(f"Failed to update pantry item: {str(e)}")


async def delete_pantry_item(
    item_id: UUID,
    user_id: UUID,
    supabase: SyncClient,
) -> bool:
    """
    Delete a pantry item (user can only delete their own items).
    
    Args:
        item_id: ID of the pantry item
        user_id: ID of the user (for authorization)
        supabase: Supabase client
        
    Returns:
        True if deletion was successful
    """
    try:
        logger.info(f"Deleting pantry item {item_id} for user {user_id}")
        
        # First check if item exists and belongs to user
        await get_pantry_item_by_id(item_id, user_id, supabase)
        
        response = supabase.table("pantry_items").delete().eq("id", str(item_id)).eq("user_id", str(user_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to delete pantry item {item_id}")
            raise PantryItemError("Failed to delete pantry item")
        
        logger.info(f"Deleted pantry item {item_id} for user {user_id}")
        return True
        
    except PantryItemNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting pantry item {item_id}: {str(e)}")
        raise PantryItemError(f"Failed to delete pantry item: {str(e)}")


def _dict_to_pantry_item_data(data: dict) -> PantryItemData:
    """Convert dictionary data to PantryItemData object."""
    
    # Handle date parsing
    expiry_date = None
    if data.get("expiry_date"):
        if isinstance(data["expiry_date"], str):
            expiry_date = datetime.fromisoformat(data["expiry_date"]).date()
        else:
            expiry_date = data["expiry_date"]
    
    # Handle datetime parsing
    added_at = data["added_at"]
    if isinstance(added_at, str):
        added_at = datetime.fromisoformat(added_at.replace("Z", "+00:00"))
    
    return PantryItemData(
        item_id=UUID(data["id"]) if isinstance(data["id"], str) else data["id"],
        user_id=UUID(data["user_id"]) if isinstance(data["user_id"], str) else data["user_id"],
        name=data["name"],
        quantity=float(data["quantity"]),
        unit=data["unit"],
        category=data["category"],
        expiry_date=expiry_date,
        added_at=added_at,
    )
