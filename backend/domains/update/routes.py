"""
Update API routes for cache and data refresh operations.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from .schemas import IngredientCacheUpdateResponse
from .services import (
    update_ingredient_cache,
    get_ingredient_cache_status,
    force_refresh_all_caches,
    UpdateError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/update", tags=["Update Operations"])


@router.post(
    "/ingredient_cache",
    response_model=IngredientCacheUpdateResponse,
    summary="Update Ingredient Cache",
    description="Update the ingredient names cache file from the database"
)
async def update_ingredient_cache_endpoint(
    force: bool = Query(False, description="Force update even if cache is fresh"),
    background_tasks: BackgroundTasks = None
) -> IngredientCacheUpdateResponse:
    """
    Update the ingredient names cache file.
    
    This endpoint updates the local cache file containing all ingredient names
    from the database. The cache is automatically updated weekly, but this
    endpoint allows for manual updates when needed.
    
    Args:
        force: If True, forces an update even if the cache is considered fresh
        background_tasks: FastAPI background tasks (injected)
        
    Returns:
        IngredientCacheUpdateResponse with update details
        
    Raises:
        HTTPException: If the update fails
    """
    try:
        logger.info(f"Ingredient cache update requested (force: {force})")
        result = await update_ingredient_cache(force=force)
        
        logger.info(f"Ingredient cache update completed successfully")
        return result
        
    except UpdateError as e:
        logger.error(f"Update error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": e.error_code,
                "message": e.message
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during cache update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during the update"
            }
        )


@router.get(
    "/ingredient_cache/status",
    response_model=Dict[str, Any],
    summary="Get Ingredient Cache Status",
    description="Get current status and metadata of the ingredient cache"
)
async def get_ingredient_cache_status_endpoint() -> Dict[str, Any]:
    """
    Get the current status of the ingredient names cache.
    
    Returns information about the cache file including when it was last updated,
    how many ingredients it contains, and whether it needs an update.
    
    Returns:
        Dictionary containing cache status information
        
    Raises:
        HTTPException: If unable to retrieve status
    """
    try:
        logger.info("Ingredient cache status requested")
        status_info = await get_ingredient_cache_status()
        
        logger.info("Ingredient cache status retrieved successfully")
        return status_info
        
    except UpdateError as e:
        logger.error(f"Error getting cache status: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": e.error_code,
                "message": e.message
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error getting cache status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving status"
            }
        )


@router.post(
    "/all_caches",
    response_model=Dict[str, Any],
    summary="Force Refresh All Caches",
    description="Force refresh all application caches"
)
async def force_refresh_all_caches_endpoint() -> Dict[str, Any]:
    """
    Force refresh all application caches.
    
    This endpoint triggers a force refresh of all caches in the application,
    including the ingredient names cache and any other caches that may be added
    in the future.
    
    Returns:
        Dictionary with results of all cache refresh operations
        
    Raises:
        HTTPException: If any cache refresh fails
    """
    try:
        logger.info("Force refresh of all caches requested")
        result = await force_refresh_all_caches()
        
        if result["overall_success"]:
            logger.info("All caches refreshed successfully")
            return result
        else:
            logger.warning("Some cache refreshes failed")
            # Return 207 Multi-Status to indicate partial success
            return JSONResponse(
                status_code=status.HTTP_207_MULTI_STATUS,
                content=result
            )
            
    except Exception as e:
        logger.error(f"Unexpected error during force refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during cache refresh"
            }
        )
