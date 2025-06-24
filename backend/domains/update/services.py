"""
Update services for cache and data refresh operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException, status

from .ingredient_cache import IngredientNamesManager
from .schemas import IngredientCacheUpdateResponse, UpdateStatus

logger = logging.getLogger(__name__)


class UpdateError(Exception):
    """Custom exception for update-related errors."""

    def __init__(self, message: str, error_code: str = "UPDATE_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


async def update_ingredient_cache(force: bool = False) -> IngredientCacheUpdateResponse:
    """
    Update the ingredient names cache file.

    Args:
        force: Whether to force update even if cache is fresh

    Returns:
        IngredientCacheUpdateResponse with update details

    Raises:
        UpdateError: If update fails
    """
    try:
        logger.info(f"Starting ingredient cache update (force: {force})")
        start_time = datetime.now()

        # Initialize the ingredient names manager
        manager = IngredientNamesManager()

        # Check if update is needed (unless forced)
        if not force and not manager.needs_update():
            metadata = manager._get_metadata()
            logger.info("Ingredient cache is up to date, no update needed")

            return IngredientCacheUpdateResponse(
                success=True,
                message="Ingredient cache is already up to date",
                timestamp=start_time,
                ingredient_count=metadata.get("ingredient_count"),
                cache_file_path=str(manager.file_path),
                last_database_update=(
                    datetime.fromisoformat(metadata["last_updated"])
                    if metadata.get("last_updated")
                    else None
                ),
                details={
                    "force_update": force,
                    "cache_was_fresh": True,
                    "update_interval_days": manager.update_interval_days,
                },
            )

        # Perform the update
        success = await manager.update_ingredient_names()

        if success:
            # Get updated metadata
            metadata = manager._get_metadata()
            ingredient_count = metadata.get("ingredient_count", 0)

            logger.info(
                f"Ingredient cache updated successfully with {ingredient_count} ingredients"
            )

            return IngredientCacheUpdateResponse(
                success=True,
                message=f"Ingredient cache updated successfully with {ingredient_count} ingredients",
                timestamp=datetime.now(),
                ingredient_count=ingredient_count,
                cache_file_path=str(manager.file_path),
                last_database_update=(
                    datetime.fromisoformat(metadata["last_updated"])
                    if metadata.get("last_updated")
                    else None
                ),
                details={
                    "force_update": force,
                    "cache_was_fresh": False,
                    "update_duration_seconds": (
                        datetime.now() - start_time
                    ).total_seconds(),
                    "update_interval_days": manager.update_interval_days,
                },
            )
        else:
            raise UpdateError(
                "Failed to update ingredient cache", "CACHE_UPDATE_FAILED"
            )

    except UpdateError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during ingredient cache update: {str(e)}")
        raise UpdateError(f"Unexpected error: {str(e)}", "UNEXPECTED_ERROR")


async def get_ingredient_cache_status() -> Dict[str, Any]:
    """
    Get the current status of the ingredient cache.

    Returns:
        Dictionary with cache status information
    """
    try:
        manager = IngredientNamesManager()
        metadata = manager._get_metadata()

        cache_exists = manager.file_path.exists()
        needs_update = manager.needs_update()

        return {
            "cache_file_exists": cache_exists,
            "cache_file_path": str(manager.file_path),
            "needs_update": needs_update,
            "last_updated": metadata.get("last_updated"),
            "ingredient_count": metadata.get("ingredient_count", 0),
            "update_interval_days": manager.update_interval_days,
            "metadata_file_exists": manager.metadata_path.exists(),
            "file_size_bytes": manager.file_path.stat().st_size if cache_exists else 0,
        }

    except Exception as e:
        logger.error(f"Error getting ingredient cache status: {str(e)}")
        raise UpdateError(f"Failed to get cache status: {str(e)}", "STATUS_ERROR")


async def force_refresh_all_caches() -> Dict[str, Any]:
    """
    Force refresh all application caches.

    Returns:
        Dictionary with results of all cache refresh operations
    """
    results = {}

    try:
        # Update ingredient cache
        ingredient_result = await update_ingredient_cache(force=True)
        results["ingredient_cache"] = {
            "success": ingredient_result.success,
            "message": ingredient_result.message,
            "ingredient_count": ingredient_result.ingredient_count,
        }

        # Add more cache updates here as needed
        # results["other_cache"] = await update_other_cache()

        overall_success = all(
            result.get("success", False) for result in results.values()
        )

        logger.info(f"Force refresh completed. Overall success: {overall_success}")

        return {
            "overall_success": overall_success,
            "timestamp": datetime.now(),
            "results": results,
            "message": (
                "All caches refreshed successfully"
                if overall_success
                else "Some cache refreshes failed"
            ),
        }

    except Exception as e:
        logger.error(f"Error during force refresh of all caches: {str(e)}")
        results["error"] = {
            "success": False,
            "message": f"Force refresh failed: {str(e)}",
        }

        return {
            "overall_success": False,
            "timestamp": datetime.now(),
            "results": results,
            "message": f"Force refresh failed: {str(e)}",
        }
