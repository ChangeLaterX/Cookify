from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_db
from ...core.exceptions import NotFoundException
from ...domains.auth.dependencies import get_current_user
from . import schemas, service
from ...shared.types.common import PaginatedResponse

router = APIRouter()

@router.get("/items", response_model=PaginatedResponse[schemas.PantryItemResponse])
async def get_pantry_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    expiring_soon: Optional[bool] = None,
    expired: Optional[bool] = None,
    search: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all pantry items for the current user with optional filtering.
    """
    items, total = await service.get_pantry_items(
        db=db,
        user_id=current_user["id"],
        page=page,
        limit=limit,
        category=category,
        expiring_soon=expiring_soon,
        expired=expired,
        search=search,
    )
    
    return PaginatedResponse[schemas.PantryItemResponse](
        data=items,
        total=total,
        page=page,
        limit=limit,
    )

@router.get("/items/{item_id}", response_model=schemas.PantryItemResponse)
async def get_pantry_item(
    item_id: str = Path(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific pantry item by ID.
    """
    item = await service.get_pantry_item_by_id(db, item_id, current_user["id"])
    if not item:
        raise NotFoundException(detail="Pantry item not found")
    return item

@router.post("/items", response_model=schemas.PantryItemResponse, status_code=201)
async def create_pantry_item(
    item: schemas.PantryItemCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new pantry item.
    """
    return await service.create_pantry_item(db, item, current_user["id"])

@router.put("/items/{item_id}", response_model=schemas.PantryItemResponse)
async def update_pantry_item(
    item: schemas.PantryItemUpdate,
    item_id: str = Path(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing pantry item.
    """
    updated_item = await service.update_pantry_item(db, item_id, item, current_user["id"])
    if not updated_item:
        raise NotFoundException(detail="Pantry item not found")
    return updated_item

@router.delete("/items/{item_id}")
async def delete_pantry_item(
    item_id: str = Path(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a pantry item.
    """
    success = await service.delete_pantry_item(db, item_id, current_user["id"])
    if not success:
        raise NotFoundException(detail="Pantry item not found")
    return {"success": True}

@router.get("/stats", response_model=schemas.PantryStats)
async def get_pantry_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics about the user's pantry.
    """
    return await service.get_pantry_stats(db, current_user["id"])