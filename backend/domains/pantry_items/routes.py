"""
FastAPI Routes for Pantry Items Domain.
Provides HTTP endpoints for user pantry management.
"""

import math
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase._sync.client import SyncClient

from core.dependencies import get_db
from core.logging import get_logger
from middleware.security import get_current_user

from .schemas import (
    MessageResponse,
    PantryItemApiResponse,
    PantryItemCreate,
    PantryItemListApiResponse,
    PantryItemListResponse,
    PantryItemResponse,
    PantryItemUpdate,
    # Bulk operation schemas
    PantryItemBulkCreate,
    PantryItemBulkUpdate,
    PantryItemBulkDelete,
    PantryItemBulkApiResponse,
    PantryItemBulkResponse,
    # Statistics schemas
    PantryStatsApiResponse,
    PantryStatsOverview,
    PantryCategoryStatsApiResponse,
    PantryCategoryStats,
    PantryExpiryApiResponse,
    PantryExpiryReport,
    PantryLowStockApiResponse,
    PantryLowStockReport,
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

logger = get_logger(__name__)

# Create router for pantry item endpoints
router = APIRouter(prefix="/pantry", tags=["Pantry Items"])


@router.get(
    "/items",
    response_model=PantryItemListApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's pantry items",
    description="Retrieve all pantry items for the authenticated user with pagination and filtering options",
)
async def list_user_pantry_items(
    page: int = Query(1, description="Page number (1-based)", ge=1),
    per_page: int = Query(50, description="Items per page", ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in item names"),
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Get all pantry items for the authenticated user."""
    try:
        logger.info(f"User {current_user.id} requesting pantry items list")

        items, total_count = await get_user_pantry_items(
            user_id=current_user.id,
            supabase=supabase,
            page=page,
            per_page=per_page,
            category=category,
            search=search,
        )

        # Convert to response objects
        item_responses = [
            PantryItemResponse(
                id=item.id,
                user_id=item.user_id,
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                category=item.category,
                expiry_date=item.expiry_date,
                added_at=item.added_at,
                ingredient_id=item.ingredient_id,
            )
            for item in items
        ]

        total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1

        list_response = PantryItemListResponse(
            items=item_responses,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

        return PantryItemListApiResponse(
            success=True,
            message=f"Retrieved {len(items)} pantry items",
            data=list_response,
        )

    except PantryItemError as e:
        logger.error(f"Error listing pantry items for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error listing pantry items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/items/{item_id}",
    response_model=PantryItemApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pantry item by ID",
    description="Retrieve a specific pantry item by its ID (user can only access their own items)",
)
async def get_pantry_item(
    item_id: UUID,
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Get a specific pantry item by ID."""
    try:
        logger.info(f"User {current_user.id} requesting pantry item {item_id}")

        item = await get_pantry_item_by_id(
            item_id=item_id,
            user_id=current_user.id,
            supabase=supabase,
        )

        item_response = PantryItemResponse(
            id=item.id,
            user_id=item.user_id,
            name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            category=item.category,
            expiry_date=item.expiry_date,
            added_at=item.added_at,
            ingredient_id=item.ingredient_id,
        )

        return PantryItemApiResponse(
            success=True,
            message="Pantry item retrieved successfully",
            data=item_response,
        )

    except PantryItemNotFoundError as e:
        logger.warning(f"Pantry item {item_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PantryItemError as e:
        logger.error(f"Error getting pantry item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting pantry item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/items",
    response_model=PantryItemApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new pantry item",
    description="Add a new item to the user's pantry",
)
async def create_new_pantry_item(
    item_data: PantryItemCreate,
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Create a new pantry item for the authenticated user."""
    try:
        logger.info(f"User {current_user.id} creating pantry item '{item_data.name}'")

        item = await create_pantry_item(
            user_id=current_user.id,
            item_data=item_data,
            supabase=supabase,
        )

        item_response = PantryItemResponse(
            id=item.id,
            user_id=item.user_id,
            name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            category=item.category,
            expiry_date=item.expiry_date,
            added_at=item.added_at,
            ingredient_id=item.ingredient_id,
        )

        return PantryItemApiResponse(
            success=True,
            message="Pantry item created successfully",
            data=item_response,
        )

    except PantryItemValidationError as e:
        logger.warning(f"Validation error creating pantry item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except PantryItemError as e:
        logger.error(f"Error creating pantry item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error creating pantry item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/items/{item_id}",
    response_model=PantryItemApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Update pantry item",
    description="Update an existing pantry item (user can only update their own items)",
)
async def update_existing_pantry_item(
    item_id: UUID,
    item_data: PantryItemUpdate,
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Update an existing pantry item."""
    try:
        logger.info(f"User {current_user.id} updating pantry item {item_id}")

        item = await update_pantry_item(
            item_id=item_id,
            user_id=current_user.id,
            item_data=item_data,
            supabase=supabase,
        )

        item_response = PantryItemResponse(
            id=item.id,
            user_id=item.user_id,
            name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            category=item.category,
            expiry_date=item.expiry_date,
            added_at=item.added_at,
            ingredient_id=item.ingredient_id,
        )

        return PantryItemApiResponse(
            success=True,
            message="Pantry item updated successfully",
            data=item_response,
        )

    except PantryItemNotFoundError as e:
        logger.warning(f"Pantry item {item_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PantryItemValidationError as e:
        logger.warning(f"Validation error updating pantry item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except PantryItemError as e:
        logger.error(f"Error updating pantry item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error updating pantry item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "/items/{item_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete pantry item",
    description="Remove an item from the user's pantry (user can only delete their own items)",
)
async def delete_existing_pantry_item(
    item_id: UUID,
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Delete a pantry item."""
    try:
        logger.info(f"User {current_user.id} deleting pantry item {item_id}")

        await delete_pantry_item(
            item_id=item_id,
            user_id=current_user.id,
            supabase=supabase,
        )

        return MessageResponse(
            success=True,
            message="Pantry item deleted successfully",
        )

    except PantryItemNotFoundError as e:
        logger.warning(f"Pantry item {item_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PantryItemError as e:
        logger.error(f"Error deleting pantry item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting pantry item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Bulk Operations Routes
@router.post(
    "/items/bulk",
    response_model=PantryItemBulkApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple pantry items",
    description="Add multiple items to the user's pantry in bulk (max 50 items)",
)
async def bulk_create_pantry_items_endpoint(
    bulk_data: PantryItemBulkCreate,
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Create multiple pantry items in bulk."""
    try:
        logger.info(f"User {current_user.id} bulk creating {len(bulk_data.items)} pantry items")

        successful_items, failed_items = await bulk_create_pantry_items(
            user_id=current_user.id,
            items_data=bulk_data.items,
            supabase=supabase,
        )

        # Convert successful items to response format
        successful_responses = [
            PantryItemResponse(
                id=item.id,
                user_id=item.user_id,
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                category=item.category,
                expiry_date=item.expiry_date,
                added_at=item.added_at,
                ingredient_id=item.ingredient_id,
            )
            for item in successful_items
        ]

        bulk_response = PantryItemBulkResponse(
            successful=successful_responses,
            failed=failed_items,
            total_processed=len(bulk_data.items),
            success_count=len(successful_items),
            failure_count=len(failed_items),
        )

        return PantryItemBulkApiResponse(
            success=True,
            message=f"Bulk create completed: {len(successful_items)} successful, {len(failed_items)} failed",
            data=bulk_response,
        )

    except Exception as e:
        logger.error(f"Error in bulk create pantry items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/items/bulk",
    response_model=PantryItemBulkApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Update multiple pantry items",
    description="Update multiple pantry items in bulk (max 50 items)",
)
async def bulk_update_pantry_items_endpoint(
    bulk_data: PantryItemBulkUpdate,
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Update multiple pantry items in bulk."""
    try:
        logger.info(f"User {current_user.id} bulk updating {len(bulk_data.updates)} pantry items")

        successful_items, failed_items = await bulk_update_pantry_items(
            user_id=current_user.id,
            updates=bulk_data.updates,
            supabase=supabase,
        )

        # Convert successful items to response format
        successful_responses = [
            PantryItemResponse(
                id=item.id,
                user_id=item.user_id,
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                category=item.category,
                expiry_date=item.expiry_date,
                added_at=item.added_at,
                ingredient_id=item.ingredient_id,
            )
            for item in successful_items
        ]

        bulk_response = PantryItemBulkResponse(
            successful=successful_responses,
            failed=failed_items,
            total_processed=len(bulk_data.updates),
            success_count=len(successful_items),
            failure_count=len(failed_items),
        )

        return PantryItemBulkApiResponse(
            success=True,
            message=f"Bulk update completed: {len(successful_items)} successful, {len(failed_items)} failed",
            data=bulk_response,
        )

    except Exception as e:
        logger.error(f"Error in bulk update pantry items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "/items/bulk",
    response_model=PantryItemBulkApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete multiple pantry items",
    description="Delete multiple pantry items in bulk (max 50 items)",
)
async def bulk_delete_pantry_items_endpoint(
    bulk_data: PantryItemBulkDelete,
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Delete multiple pantry items in bulk."""
    try:
        logger.info(f"User {current_user.id} bulk deleting {len(bulk_data.item_ids)} pantry items")

        successful_ids, failed_items = await bulk_delete_pantry_items(
            user_id=current_user.id,
            item_ids=bulk_data.item_ids,
            supabase=supabase,
        )

        # Create mock successful responses for deleted items
        successful_responses = [
            PantryItemResponse(
                id=item_id,
                user_id=current_user.id,
                name="Deleted Item",
                quantity=0,
                unit="",
                category=None,
                expiry_date=None,
                added_at=datetime.now(),
                ingredient_id=item_id,  # Placeholder
            )
            for item_id in successful_ids
        ]

        bulk_response = PantryItemBulkResponse(
            successful=successful_responses,
            failed=failed_items,
            total_processed=len(bulk_data.item_ids),
            success_count=len(successful_ids),
            failure_count=len(failed_items),
        )

        return PantryItemBulkApiResponse(
            success=True,
            message=f"Bulk delete completed: {len(successful_ids)} successful, {len(failed_items)} failed",
            data=bulk_response,
        )

    except Exception as e:
        logger.error(f"Error in bulk delete pantry items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Statistics and Analytics Routes
@router.get(
    "/stats",
    response_model=PantryStatsApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pantry overview statistics",
    description="Get comprehensive statistics about the user's pantry",
)
async def get_pantry_statistics(
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Get pantry overview statistics."""
    try:
        logger.info(f"User {current_user.id} requesting pantry statistics")

        stats_data = await get_pantry_stats_overview(
            user_id=current_user.id,
            supabase=supabase,
        )

        stats_response = PantryStatsOverview(**stats_data)

        return PantryStatsApiResponse(
            success=True,
            message="Pantry statistics retrieved successfully",
            data=stats_response,
        )

    except PantryItemError as e:
        logger.error(f"Error getting pantry statistics for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting pantry statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/categories",
    response_model=PantryCategoryStatsApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pantry category statistics",
    description="Get breakdown of pantry items by category",
)
async def get_pantry_category_statistics(
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Get pantry category statistics."""
    try:
        logger.info(f"User {current_user.id} requesting pantry category statistics")

        stats_data = await get_pantry_category_stats(
            user_id=current_user.id,
            supabase=supabase,
        )

        stats_response = PantryCategoryStats(**stats_data)

        return PantryCategoryStatsApiResponse(
            success=True,
            message="Category statistics retrieved successfully",
            data=stats_response,
        )

    except PantryItemError as e:
        logger.error(f"Error getting category statistics for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting category statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/expiring",
    response_model=PantryExpiryApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pantry expiry report",
    description="Get report of items by expiry status (expired, expiring soon, fresh)",
)
async def get_pantry_expiry_report_endpoint(
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Get pantry expiry report."""
    try:
        logger.info(f"User {current_user.id} requesting pantry expiry report")

        report_data = await get_pantry_expiry_report(
            user_id=current_user.id,
            supabase=supabase,
        )

        report_response = PantryExpiryReport(**report_data)

        return PantryExpiryApiResponse(
            success=True,
            message="Expiry report retrieved successfully",
            data=report_response,
        )

    except PantryItemError as e:
        logger.error(f"Error getting expiry report for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting expiry report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/low-stock",
    response_model=PantryLowStockApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Get low stock report",
    description="Get report of items with low stock levels",
)
async def get_pantry_low_stock_report_endpoint(
    threshold: float = Query(1.0, description="Quantity threshold for low stock", ge=0, le=10),
    current_user=Depends(get_current_user),
    supabase: SyncClient = Depends(get_db),
):
    """Get pantry low stock report."""
    try:
        logger.info(f"User {current_user.id} requesting pantry low stock report with threshold {threshold}")

        report_data = await get_pantry_low_stock_report(
            user_id=current_user.id,
            supabase=supabase,
            threshold=threshold,
        )

        report_response = PantryLowStockReport(**report_data)

        return PantryLowStockApiResponse(
            success=True,
            message="Low stock report retrieved successfully",
            data=report_response,
        )

    except PantryItemError as e:
        logger.error(f"Error getting low stock report for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting low stock report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
