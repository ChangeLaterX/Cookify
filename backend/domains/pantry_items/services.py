"""
Business Logic for Pantry Items Domain.
Handles all pantry item operations and database interactions.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Tuple
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
        ingredient_id: UUID,
    ):
        self.id = item_id
        self.user_id = user_id
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.category = category
        self.expiry_date = expiry_date
        self.added_at = added_at
        self.ingredient_id = ingredient_id

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
    Create a new pantry item for a user or update quantity if item already exists.
    
    Args:
        user_id: ID of the user
        item_data: Pantry item creation data
        supabase: Supabase client
        
    Returns:
        Created or updated PantryItemData object
    """
    try:
        logger.info(f"Creating/updating pantry item '{item_data.name}' for user {user_id}")
        
        # Check if item already exists with same ingredient_id, unit and user_id
        existing_response = supabase.table("pantry_items").select("*").eq("user_id", str(user_id)).eq("ingredient_id", str(item_data.ingredient_id)).eq("unit", item_data.unit).execute()
        
        if existing_response.data:
            # Item exists - update quantity
            existing_item = existing_response.data[0]
            existing_quantity = float(existing_item["quantity"])
            new_quantity = existing_quantity + item_data.quantity
            
            logger.info(f"Item already exists - updating quantity from {existing_quantity} to {new_quantity} {item_data.unit}")
            
            update_data = {
                "quantity": new_quantity,
                "added_at": datetime.utcnow().isoformat(),  # Update timestamp
            }
            
            # Optionally update category and expiry_date if provided
            if item_data.category:
                update_data["category"] = item_data.category
            if item_data.expiry_date:
                update_data["expiry_date"] = item_data.expiry_date.isoformat()
            
            response = supabase.table("pantry_items").update(update_data).eq("id", existing_item["id"]).execute()
            
            if not response.data:
                logger.error(f"Failed to update existing pantry item for user {user_id}")
                raise PantryItemError("Failed to update existing pantry item")
            
            item = _dict_to_pantry_item_data(response.data[0])
            logger.info(f"Updated existing pantry item {item.id} - new quantity: {new_quantity} {item_data.unit}")
            return item
        
        else:
            # Item doesn't exist - create new
            logger.info(f"Item doesn't exist - creating new pantry item")
            
            # Prepare data for insertion
            insert_data = {
                "user_id": str(user_id),
                "name": item_data.name,
                "quantity": item_data.quantity,
                "unit": item_data.unit,
                "category": item_data.category,
                "expiry_date": item_data.expiry_date.isoformat() if item_data.expiry_date else None,
                "added_at": datetime.utcnow().isoformat(),
                "ingredient_id": str(item_data.ingredient_id),
            }
            
            response = supabase.table("pantry_items").insert(insert_data).execute()
            
            if not response.data:
                logger.error(f"Failed to create pantry item for user {user_id}")
                raise PantryItemError("Failed to create pantry item")
            
            item = _dict_to_pantry_item_data(response.data[0])
            logger.info(f"Created new pantry item {item.id} with quantity: {item_data.quantity} {item_data.unit}")
            return item
        
    except Exception as e:
        logger.error(f"Error creating/updating pantry item for user {user_id}: {str(e)}")
        raise PantryItemError(f"Failed to create/update pantry item: {str(e)}")


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
        if item_data.ingredient_id is not None:
            update_data["ingredient_id"] = str(item_data.ingredient_id)
        
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


# Bulk Operations
async def bulk_create_pantry_items(
    user_id: UUID,
    items_data: List[PantryItemCreate],
    supabase: SyncClient,
) -> Tuple[List[PantryItemData], List[Dict]]:
    """
    Create multiple pantry items in bulk.
    
    Args:
        user_id: ID of the user
        items_data: List of pantry item creation data
        supabase: Supabase client
        
    Returns:
        Tuple of (successful_items, failed_items)
    """
    logger.info(f"Bulk creating {len(items_data)} pantry items for user {user_id}")
    
    successful_items = []
    failed_items = []
    
    for idx, item_data in enumerate(items_data):
        try:
            item = await create_pantry_item(user_id, item_data, supabase)
            successful_items.append(item)
        except Exception as e:
            logger.error(f"Failed to create item {idx}: {str(e)}")
            failed_items.append({
                "index": idx,
                "item_data": item_data.model_dump(),
                "error": str(e)
            })
    
    logger.info(f"Bulk create completed: {len(successful_items)} successful, {len(failed_items)} failed")
    return successful_items, failed_items


async def bulk_update_pantry_items(
    user_id: UUID,
    updates: Dict[UUID, PantryItemUpdate],
    supabase: SyncClient,
) -> Tuple[List[PantryItemData], List[Dict]]:
    """
    Update multiple pantry items in bulk.
    
    Args:
        user_id: ID of the user
        updates: Dictionary mapping item IDs to update data
        supabase: Supabase client
        
    Returns:
        Tuple of (successful_items, failed_items)
    """
    logger.info(f"Bulk updating {len(updates)} pantry items for user {user_id}")
    
    successful_items = []
    failed_items = []
    
    for item_id, update_data in updates.items():
        try:
            item = await update_pantry_item(item_id, user_id, update_data, supabase)
            successful_items.append(item)
        except Exception as e:
            logger.error(f"Failed to update item {item_id}: {str(e)}")
            failed_items.append({
                "item_id": str(item_id),
                "update_data": update_data.model_dump(exclude_none=True),
                "error": str(e)
            })
    
    logger.info(f"Bulk update completed: {len(successful_items)} successful, {len(failed_items)} failed")
    return successful_items, failed_items


async def bulk_delete_pantry_items(
    user_id: UUID,
    item_ids: List[UUID],
    supabase: SyncClient,
) -> Tuple[List[UUID], List[Dict]]:
    """
    Delete multiple pantry items in bulk.
    
    Args:
        user_id: ID of the user
        item_ids: List of item IDs to delete
        supabase: Supabase client
        
    Returns:
        Tuple of (successful_ids, failed_items)
    """
    logger.info(f"Bulk deleting {len(item_ids)} pantry items for user {user_id}")
    
    successful_ids = []
    failed_items = []
    
    for item_id in item_ids:
        try:
            await delete_pantry_item(item_id, user_id, supabase)
            successful_ids.append(item_id)
        except Exception as e:
            logger.error(f"Failed to delete item {item_id}: {str(e)}")
            failed_items.append({
                "item_id": str(item_id),
                "error": str(e)
            })
    
    logger.info(f"Bulk delete completed: {len(successful_ids)} successful, {len(failed_items)} failed")
    return successful_ids, failed_items


# Statistics and Analytics
async def get_pantry_stats_overview(
    user_id: UUID,
    supabase: SyncClient,
) -> Dict:
    """
    Get overview statistics for user's pantry.
    
    Args:
        user_id: ID of the user
        supabase: Supabase client
        
    Returns:
        Dictionary with pantry statistics
    """
    try:
        logger.info(f"Generating pantry stats overview for user {user_id}")
        
        # Get all pantry items for the user
        response = supabase.table("pantry_items").select("*").eq("user_id", str(user_id)).execute()
        
        if not response.data:
            return {
                "total_items": 0,
                "total_categories": 0,
                "items_expiring_soon": 0,
                "expired_items": 0,
                "low_stock_items": 0,
                "estimated_total_value": 0.0,
                "most_common_category": None,
            }
        
        items = [_dict_to_pantry_item_data(item) for item in response.data]
        today = date.today()
        three_days_later = today + timedelta(days=3)
        
        # Calculate statistics
        total_items = len(items)
        categories = [item.category for item in items if item.category]
        total_categories = len(set(categories))
        
        items_expiring_soon = sum(
            1 for item in items 
            if item.expiry_date and today < item.expiry_date <= three_days_later
        )
        
        expired_items = sum(
            1 for item in items 
            if item.expiry_date and item.expiry_date < today
        )
        
        low_stock_items = sum(1 for item in items if item.quantity <= 1.0)
        
        # Most common category
        most_common_category = None
        if categories:
            category_counts = {}
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            most_common_category = max(category_counts.keys(), key=lambda k: category_counts[k])
        
        # Estimated total value (placeholder - would need price data)
        estimated_total_value = 0.0  # Would calculate based on ingredient prices
        
        stats = {
            "total_items": total_items,
            "total_categories": total_categories,
            "items_expiring_soon": items_expiring_soon,
            "expired_items": expired_items,
            "low_stock_items": low_stock_items,
            "estimated_total_value": estimated_total_value,
            "most_common_category": most_common_category,
        }
        
        logger.info(f"Generated pantry stats for user {user_id}: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error generating pantry stats for user {user_id}: {str(e)}")
        raise PantryItemError(f"Failed to generate pantry statistics: {str(e)}")


async def get_pantry_category_stats(
    user_id: UUID,
    supabase: SyncClient,
) -> Dict:
    """
    Get category breakdown statistics for user's pantry.
    
    Args:
        user_id: ID of the user
        supabase: Supabase client
        
    Returns:
        Dictionary with category statistics
    """
    try:
        logger.info(f"Generating pantry category stats for user {user_id}")
        
        response = supabase.table("pantry_items").select("category").eq("user_id", str(user_id)).execute()
        
        if not response.data:
            return {
                "categories": [],
                "uncategorized_count": 0,
            }
        
        total_items = len(response.data)
        category_counts = {}
        uncategorized_count = 0
        
        for item in response.data:
            category = item.get("category")
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1
            else:
                uncategorized_count += 1
        
        # Calculate percentages and create category stats
        categories = []
        for category, count in category_counts.items():
            percentage = (count / total_items) * 100 if total_items > 0 else 0
            categories.append({
                "category": category,
                "item_count": count,
                "percentage": round(percentage, 2)
            })
        
        # Sort by count descending
        categories.sort(key=lambda x: x["item_count"], reverse=True)
        
        stats = {
            "categories": categories,
            "uncategorized_count": uncategorized_count,
        }
        
        logger.info(f"Generated category stats for user {user_id}")
        return stats
        
    except Exception as e:
        logger.error(f"Error generating category stats for user {user_id}: {str(e)}")
        raise PantryItemError(f"Failed to generate category statistics: {str(e)}")


async def get_pantry_expiry_report(
    user_id: UUID,
    supabase: SyncClient,
) -> Dict:
    """
    Get expiry report for user's pantry items.
    
    Args:
        user_id: ID of the user
        supabase: Supabase client
        
    Returns:
        Dictionary with expiry report
    """
    try:
        logger.info(f"Generating pantry expiry report for user {user_id}")
        
        response = supabase.table("pantry_items").select("*").eq("user_id", str(user_id)).is_("expiry_date", "not.null").execute()
        
        if not response.data:
            return {
                "expiring_soon": [],
                "expired": [],
                "fresh": [],
            }
        
        items = [_dict_to_pantry_item_data(item) for item in response.data]
        today = date.today()
        three_days_later = today + timedelta(days=3)
        seven_days_later = today + timedelta(days=7)
        
        expiring_soon = []
        expired = []
        fresh = []
        
        for item in items:
            if not item.expiry_date:
                continue
                
            days_until_expiry = (item.expiry_date - today).days
            
            expiry_item = {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "expiry_date": item.expiry_date,
                "days_until_expiry": days_until_expiry
            }
            
            if item.expiry_date < today:
                expired.append(expiry_item)
            elif item.expiry_date <= three_days_later:
                expiring_soon.append(expiry_item)
            elif item.expiry_date > seven_days_later:
                fresh.append(expiry_item)
        
        # Sort by expiry date
        expiring_soon.sort(key=lambda x: x["expiry_date"])
        expired.sort(key=lambda x: x["expiry_date"])
        fresh.sort(key=lambda x: x["expiry_date"])
        
        report = {
            "expiring_soon": expiring_soon,
            "expired": expired,
            "fresh": fresh,
        }
        
        logger.info(f"Generated expiry report for user {user_id}: {len(expiring_soon)} expiring, {len(expired)} expired")
        return report
        
    except Exception as e:
        logger.error(f"Error generating expiry report for user {user_id}: {str(e)}")
        raise PantryItemError(f"Failed to generate expiry report: {str(e)}")


async def get_pantry_low_stock_report(
    user_id: UUID,
    supabase: SyncClient,
    threshold: float = 1.0,
) -> Dict:
    """
    Get low stock report for user's pantry items.
    
    Args:
        user_id: ID of the user
        supabase: Supabase client
        threshold: Quantity threshold for considering item as low stock
        
    Returns:
        Dictionary with low stock report
    """
    try:
        logger.info(f"Generating pantry low stock report for user {user_id} with threshold {threshold}")
        
        response = supabase.table("pantry_items").select("*").eq("user_id", str(user_id)).lte("quantity", threshold).execute()
        
        if not response.data:
            return {
                "low_stock_items": [],
                "threshold_used": threshold,
            }
        
        items = [_dict_to_pantry_item_data(item) for item in response.data]
        
        low_stock_items = []
        for item in items:
            # Suggest restocking to 3x the current amount or minimum 2 units
            suggested_restock = max(item.quantity * 3, 2.0)
            
            low_stock_items.append({
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category,
                "suggested_restock_quantity": suggested_restock
            })
        
        # Sort by quantity ascending (lowest stock first)
        low_stock_items.sort(key=lambda x: x["quantity"])
        
        report = {
            "low_stock_items": low_stock_items,
            "threshold_used": threshold,
        }
        
        logger.info(f"Generated low stock report for user {user_id}: {len(low_stock_items)} items")
        return report
        
    except Exception as e:
        logger.error(f"Error generating low stock report for user {user_id}: {str(e)}")
        raise PantryItemError(f"Failed to generate low stock report: {str(e)}")


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
        ingredient_id=UUID(data["ingredient_id"]) if isinstance(data["ingredient_id"], str) else data["ingredient_id"],
    )
