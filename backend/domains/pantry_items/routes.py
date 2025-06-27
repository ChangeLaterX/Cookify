"""
FastAPI Routes for Pantry Items Domain.
Provides HTTP endpoints for user pantry management.
"""

import math
from typing import Optional
from uuid import UUID

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
