"""
FastAPI Routes for Ingredients Domain.
Provides HTTP endpoints for ingredient master data management.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from core.config import settings
from .schemas import (
    IngredientMasterCreate,
    IngredientMasterUpdate,
    IngredientMasterResponse,
    IngredientListResponse,
    IngredientResponse,
    IngredientListApiResponse,
    MessageResponse,
    ErrorResponse,
)
from .services import (
    get_all_ingredients,
    get_ingredient_by_id,
    create_ingredient,
    update_ingredient,
    delete_ingredient,
    search_ingredients,
    IngredientError,
)
from middleware.security import get_current_user, get_optional_user

logger: logging.Logger = logging.getLogger(__name__)

# Create router for ingredient endpoints
router = APIRouter(prefix=settings.INGREDIENTS_PREFIX, tags=[settings.INGREDIENTS_TAG])


@router.get(
    settings.INGREDIENTS_MASTER_ENDPOINT,
    response_model=IngredientListApiResponse,
    status_code=status.HTTP_200_OK,
    summary=settings.INGREDIENTS_MASTER_LIST_TITLE,
    description=settings.INGREDIENTS_MASTER_LIST_DESCRIPTION,
)
async def list_ingredients(
    limit: int = Query(
        default=settings.INGREDIENTS_DEFAULT_LIMIT, 
        ge=1, 
        le=settings.INGREDIENTS_MAX_LIMIT, 
        description="Maximum number of results"
    ),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> IngredientListApiResponse:
    """
    List all ingredients in master table with pagination.

    Args:
        limit: Maximum number of ingredients to return (1-100)
        offset: Number of ingredients to skip for pagination

    Returns:
        IngredientListApiResponse with ingredients and pagination info

    Raises:
        HTTPException: 500 if database error occurs
    """
    try:
        logger.info(f"Listing ingredients with limit={limit}, offset={offset}")

        ingredient_list = await get_all_ingredients(limit=limit, offset=offset)

        logger.info(
            f"Successfully retrieved {len(ingredient_list.ingredients)} ingredients"
        )
        return IngredientListApiResponse(
            success=True,
            data=ingredient_list,
            message=f"Retrieved {len(ingredient_list.ingredients)} ingredients",
            error=None,
        )

    except IngredientError as e:
        logger.error(f"Failed to list ingredients: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error listing ingredients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.get(
    "/master/{ingredient_id}",
    response_model=IngredientResponse,
    status_code=status.HTTP_200_OK,
    summary="Get specific master ingredient",
    description="Retrieve a specific ingredient by its ID from the master table",
)
async def get_ingredient(ingredient_id: UUID) -> IngredientResponse:
    """
    Retrieve a specific master ingredient by ID.

    Args:
        ingredient_id: UUID of the ingredient to retrieve

    Returns:
        IngredientResponse with ingredient data

    Raises:
        HTTPException: 404 if ingredient not found, 500 if database error
    """
    try:
        logger.info(f"Retrieving ingredient with ID: {ingredient_id}")

        ingredient = await get_ingredient_by_id(ingredient_id)

        logger.info(f"Successfully retrieved ingredient: {ingredient.name}")
        return IngredientResponse(
            success=True,
            data=ingredient,
            message="Ingredient retrieved successfully",
            error=None,
        )

    except IngredientError as e:
        logger.warning(f"Failed to get ingredient {ingredient_id}: {e.message}")
        status_code = (
            status.HTTP_404_NOT_FOUND
            if e.error_code == "INGREDIENT_NOT_FOUND"
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error getting ingredient {ingredient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post(
    "/master",
    response_model=IngredientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new master ingredient",
    description="Create a new ingredient in the master table",
)
async def create_new_ingredient(
    ingredient_data: IngredientMasterCreate,
    current_user=Depends(get_current_user),
) -> IngredientResponse:
    """
    Create a new master ingredient.

    Args:
        ingredient_data: The ingredient data to create
        current_user: Authenticated user (required)

    Returns:
        IngredientResponse with created ingredient data

    Raises:
        HTTPException: 409 if ingredient name exists, 400 if validation fails, 500 if database error
    """
    try:
        logger.info(f"Creating new ingredient: {ingredient_data.name}")

        ingredient = await create_ingredient(ingredient_data)

        logger.info(f"Successfully created ingredient: {ingredient.name}")
        return IngredientResponse(
            success=True,
            data=ingredient,
            message="Ingredient created successfully",
            error=None,
        )

    except IngredientError as e:
        logger.warning(f"Failed to create ingredient: {e.message}")
        status_code = (
            status.HTTP_409_CONFLICT
            if e.error_code == "INGREDIENT_NAME_EXISTS"
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error creating ingredient: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.put(
    "/master/{ingredient_id}",
    response_model=IngredientResponse,
    status_code=status.HTTP_200_OK,
    summary="Update master ingredient",
    description="Update nutritional data or price for an ingredient",
)
async def update_existing_ingredient(
    ingredient_id: UUID,
    ingredient_data: IngredientMasterUpdate,
    current_user=Depends(get_current_user),
) -> IngredientResponse:
    """
    Update an existing master ingredient.

    Args:
        ingredient_id: UUID of the ingredient to update
        ingredient_data: The updated ingredient data
        current_user: Authenticated user (required)

    Returns:
        IngredientResponse with updated ingredient data

    Raises:
        HTTPException: 404 if ingredient not found, 409 if name exists, 500 if database error
    """
    try:
        logger.info(f"Updating ingredient with ID: {ingredient_id}")

        ingredient = await update_ingredient(ingredient_id, ingredient_data)

        logger.info(f"Successfully updated ingredient: {ingredient.name}")
        return IngredientResponse(
            success=True,
            data=ingredient,
            message="Ingredient updated successfully",
            error=None,
        )

    except IngredientError as e:
        logger.warning(f"Failed to update ingredient {ingredient_id}: {e.message}")
        if e.error_code == "INGREDIENT_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif e.error_code == "INGREDIENT_NAME_EXISTS":
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        raise HTTPException(
            status_code=status_code,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error updating ingredient {ingredient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.delete(
    "/master/{ingredient_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete master ingredient (admin-only)",
    description="Remove a master ingredient from the database (admin-only operation)",
)
async def delete_existing_ingredient(
    ingredient_id: UUID,
    current_user=Depends(get_current_user),
) -> MessageResponse:
    """
    Delete a master ingredient (admin-only).

    Args:
        ingredient_id: UUID of the ingredient to delete
        current_user: Authenticated user (required, admin role needed)

    Returns:
        MessageResponse confirming deletion

    Raises:
        HTTPException: 404 if ingredient not found, 403 if not admin, 500 if database error
    """
    try:
        # TODO: Add admin role check when user roles are implemented
        # if not current_user.is_admin:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail={"error": "Admin access required", "error_code": "INSUFFICIENT_PERMISSIONS"}
        #     )

        logger.info(f"Deleting ingredient with ID: {ingredient_id}")

        await delete_ingredient(ingredient_id)

        logger.info(f"Successfully deleted ingredient: {ingredient_id}")
        return MessageResponse(
            message="Ingredient deleted successfully",
            success=True,
        )

    except IngredientError as e:
        logger.warning(f"Failed to delete ingredient {ingredient_id}: {e.message}")
        status_code = (
            status.HTTP_404_NOT_FOUND
            if e.error_code == "INGREDIENT_NOT_FOUND"
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting ingredient {ingredient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.get(
    "/search",
    response_model=IngredientListApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Search ingredients by name",
    description="Search ingredients by name using query parameter",
)
async def search_ingredients_by_name(
    q: str = Query(..., min_length=1, max_length=255, description="Search query"),
    limit: int = Query(
        default=settings.INGREDIENTS_SEARCH_DEFAULT_LIMIT, 
        ge=1, 
        le=settings.INGREDIENTS_SEARCH_MAX_LIMIT, 
        description="Maximum number of results"
    ),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> IngredientListApiResponse:
    """
    Search ingredients by name.

    Args:
        q: Search query string
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination

    Returns:
        IngredientListApiResponse with matching ingredients

    Raises:
        HTTPException: 500 if search fails
    """
    try:
        logger.info(
            f"Searching ingredients with query: '{q}', limit={limit}, offset={offset}"
        )

        ingredient_list = await search_ingredients(query=q, limit=limit, offset=offset)

        logger.info(
            f"Found {len(ingredient_list.ingredients)} ingredients matching '{q}'"
        )
        return IngredientListApiResponse(
            success=True,
            data=ingredient_list,
            message=f"Found {len(ingredient_list.ingredients)} ingredients matching '{q}'",
            error=None,
        )

    except IngredientError as e:
        logger.error(f"Failed to search ingredients: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error searching ingredients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


# End of ingredients routes
