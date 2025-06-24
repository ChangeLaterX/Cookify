"""
Ingredient Services with Supabase Integration.
Handles business logic for ingredient master data management.
"""

import logging
from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from core.config import settings
from shared.database.supabase import get_supabase_client

from .models import IngredientMaster
from .schemas import (
    IngredientListResponse,
    IngredientMasterCreate,
    IngredientMasterResponse,
    IngredientMasterUpdate,
)

logger = logging.getLogger(__name__)


class IngredientError(Exception):
    """Custom exception for ingredient-related errors."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


async def get_all_ingredients(
    limit: Optional[int] = None, offset: int = 0
) -> IngredientListResponse:
    """
    Get all ingredients from master table with pagination.

    Args:
        limit: Maximum number of ingredients to return (defaults to config setting)
        offset: Number of ingredients to skip

    Returns:
        IngredientListResponse with ingredients and pagination info

    Raises:
        IngredientError: If database query fails
    """
    if limit is None:
        limit = settings.INGREDIENTS_DEFAULT_LIMIT

    # Enforce maximum page size for ingredients
    limit = min(limit, settings.INGREDIENTS_MAX_LIMIT)
    try:
        supabase: Client = get_supabase_client()

        # Get total count
        all_response = (
            supabase.table("ingredient_master").select("ingredient_id").execute()
        )
        total = len(all_response.data) if all_response.data else 0

        # Get paginated results
        response = (
            supabase.table("ingredient_master")
            .select("*")
            .range(offset, offset + limit - 1)
            .order("name")
            .execute()
        )

        ingredients = [
            IngredientMasterResponse(**ingredient) for ingredient in response.data
        ]

        logger.info(f"Retrieved {len(ingredients)} ingredients from database")
        return IngredientListResponse(
            ingredients=ingredients, total=total, limit=limit, offset=offset
        )

    except Exception as e:
        logger.error(f"Failed to retrieve ingredients: {str(e)}")
        raise IngredientError(
            message="Failed to retrieve ingredients", error_code="DATABASE_ERROR"
        )


async def get_ingredient_by_id(ingredient_id: UUID) -> IngredientMasterResponse:
    """
    Get a specific ingredient by ID.

    Args:
        ingredient_id: The UUID of the ingredient

    Returns:
        IngredientMasterResponse with ingredient data

    Raises:
        IngredientError: If ingredient not found or database query fails
    """
    try:
        supabase: Client = get_supabase_client()

        response = (
            supabase.table("ingredient_master")
            .select("*")
            .eq("ingredient_id", str(ingredient_id))
            .execute()
        )

        if not response.data:
            raise IngredientError(
                message="Ingredient not found", error_code="INGREDIENT_NOT_FOUND"
            )

        ingredient = IngredientMasterResponse(**response.data[0])
        logger.info(f"Retrieved ingredient {ingredient_id}")
        return ingredient

    except IngredientError:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve ingredient {ingredient_id}: {str(e)}")
        raise IngredientError(
            message="Failed to retrieve ingredient", error_code="DATABASE_ERROR"
        )


async def create_ingredient(
    ingredient_data: IngredientMasterCreate,
) -> IngredientMasterResponse:
    """
    Create a new ingredient in master table.

    Args:
        ingredient_data: The ingredient data to create

    Returns:
        IngredientMasterResponse with created ingredient data

    Raises:
        IngredientError: If ingredient name already exists or creation fails
    """
    try:
        supabase: Client = get_supabase_client()

        # Check if ingredient name already exists
        existing_response = (
            supabase.table("ingredient_master")
            .select("name")
            .eq("name", ingredient_data.name)
            .execute()
        )

        if existing_response.data:
            raise IngredientError(
                message="Ingredient with this name already exists",
                error_code="INGREDIENT_NAME_EXISTS",
            )

        # Create new ingredient
        response = (
            supabase.table("ingredient_master").insert(ingredient_data.dict()).execute()
        )

        if not response.data:
            raise IngredientError(
                message="Failed to create ingredient", error_code="CREATION_FAILED"
            )

        ingredient = IngredientMasterResponse(**response.data[0])
        logger.info(f"Created ingredient: {ingredient.name}")
        return ingredient

    except IngredientError:
        raise
    except Exception as e:
        logger.error(f"Failed to create ingredient: {str(e)}")
        raise IngredientError(
            message="Failed to create ingredient", error_code="DATABASE_ERROR"
        )


async def update_ingredient(
    ingredient_id: UUID, ingredient_data: IngredientMasterUpdate
) -> IngredientMasterResponse:
    """
    Update an existing ingredient.

    Args:
        ingredient_id: The UUID of the ingredient to update
        ingredient_data: The updated ingredient data

    Returns:
        IngredientMasterResponse with updated ingredient data

    Raises:
        IngredientError: If ingredient not found, name exists, or update fails
    """
    try:
        supabase: Client = get_supabase_client()

        # Check if ingredient exists
        existing_response = (
            supabase.table("ingredient_master")
            .select("*")
            .eq("ingredient_id", str(ingredient_id))
            .execute()
        )

        if not existing_response.data:
            raise IngredientError(
                message="Ingredient not found", error_code="INGREDIENT_NOT_FOUND"
            )

        # Check if name already exists for another ingredient
        if ingredient_data.name:
            name_check_response = (
                supabase.table("ingredient_master")
                .select("ingredient_id")
                .eq("name", ingredient_data.name)
                .neq("ingredient_id", str(ingredient_id))
                .execute()
            )

            if name_check_response.data:
                raise IngredientError(
                    message="Ingredient with this name already exists",
                    error_code="INGREDIENT_NAME_EXISTS",
                )

        # Update ingredient
        update_data = {k: v for k, v in ingredient_data.dict().items() if v is not None}

        response = (
            supabase.table("ingredient_master")
            .update(update_data)
            .eq("ingredient_id", str(ingredient_id))
            .execute()
        )

        if not response.data:
            raise IngredientError(
                message="Failed to update ingredient", error_code="UPDATE_FAILED"
            )

        ingredient = IngredientMasterResponse(**response.data[0])
        logger.info(f"Updated ingredient: {ingredient_id}")
        return ingredient

    except IngredientError:
        raise
    except Exception as e:
        logger.error(f"Failed to update ingredient {ingredient_id}: {str(e)}")
        raise IngredientError(
            message="Failed to update ingredient", error_code="DATABASE_ERROR"
        )


async def delete_ingredient(ingredient_id: UUID) -> bool:
    """
    Delete an ingredient from master table.

    Args:
        ingredient_id: The UUID of the ingredient to delete

    Returns:
        True if deletion was successful

    Raises:
        IngredientError: If ingredient not found or deletion fails
    """
    try:
        supabase: Client = get_supabase_client()

        # Check if ingredient exists
        existing_response = (
            supabase.table("ingredient_master")
            .select("ingredient_id")
            .eq("ingredient_id", str(ingredient_id))
            .execute()
        )

        if not existing_response.data:
            raise IngredientError(
                message="Ingredient not found", error_code="INGREDIENT_NOT_FOUND"
            )

        # Delete ingredient
        response = (
            supabase.table("ingredient_master")
            .delete()
            .eq("ingredient_id", str(ingredient_id))
            .execute()
        )

        logger.info(f"Deleted ingredient: {ingredient_id}")
        return True

    except IngredientError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete ingredient {ingredient_id}: {str(e)}")
        raise IngredientError(
            message="Failed to delete ingredient", error_code="DATABASE_ERROR"
        )


async def search_ingredients(
    query: str, limit: Optional[int] = None, offset: int = 0
) -> IngredientListResponse:
    """
    Search ingredients by name.

    Args:
        query: Search query string
        limit: Maximum number of results to return (defaults to config setting)
        offset: Number of results to skip

    Returns:
        IngredientListResponse with matching ingredients

    Raises:
        IngredientError: If search fails
    """
    if limit is None:
        limit = settings.INGREDIENTS_SEARCH_DEFAULT_LIMIT

    # Enforce maximum page size for ingredient search
    limit = min(limit, settings.INGREDIENTS_SEARCH_MAX_LIMIT)
    try:
        supabase: Client = get_supabase_client()

        # Search with case-insensitive partial matching
        search_pattern = f"%{query}%"

        # Get total count for search results
        all_search_response = (
            supabase.table("ingredient_master")
            .select("ingredient_id")
            .ilike("name", search_pattern)
            .execute()
        )
        total = len(all_search_response.data) if all_search_response.data else 0

        # Get paginated search results
        response = (
            supabase.table("ingredient_master")
            .select("*")
            .ilike("name", search_pattern)
            .range(offset, offset + limit - 1)
            .order("name")
            .execute()
        )

        ingredients = [
            IngredientMasterResponse(**ingredient) for ingredient in response.data
        ]

        logger.info(f"Found {len(ingredients)} ingredients matching '{query}'")
        return IngredientListResponse(
            ingredients=ingredients, total=total, limit=limit, offset=offset
        )

    except Exception as e:
        logger.error(f"Failed to search ingredients with query '{query}': {str(e)}")
        raise IngredientError(
            message="Failed to search ingredients", error_code="SEARCH_ERROR"
        )
