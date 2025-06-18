"""
Scripts monitoring routes.

Provides endpoints to monitor the status of startup scripts and caches.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from scripts.ingredient_loader import (
    get_ingredient_cache_stats,
    refresh_ingredient_cache,
    get_ingredient_names_for_ocr,
    search_ingredient_matches
)
from scripts.startup import get_startup_results

router = APIRouter(prefix="/scripts", tags=["Scripts & Monitoring"])


@router.get("/status", summary="Get scripts status")
async def get_scripts_status() -> Dict[str, Any]:
    """
    Get the status of all startup scripts and caches.
    
    Returns:
        Dict containing status information for all scripts and caches
    """
    try:
        # Get startup script results
        startup_results = get_startup_results()
        
        # Get ingredient cache stats
        ingredient_stats = get_ingredient_cache_stats()
        
        return {
            "startup_scripts": {
                "total_scripts": len(startup_results),
                "successful_scripts": sum(startup_results),
                "failed_scripts": len(startup_results) - sum(startup_results),
                "all_successful": all(startup_results) if startup_results else False,
                "results": startup_results
            },
            "ingredient_cache": ingredient_stats,
            "status": "healthy" if (all(startup_results) if startup_results else False) and ingredient_stats.get("cache_valid", False) else "degraded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scripts status: {str(e)}")


@router.get("/ingredients/cache/stats", summary="Get ingredient cache statistics")
async def get_ingredient_cache_statistics() -> Dict[str, Any]:
    """
    Get detailed statistics about the ingredient cache.
    
    Returns:
        Dict containing cache statistics
    """
    return get_ingredient_cache_stats()


@router.post("/ingredients/cache/refresh", summary="Refresh ingredient cache")
async def refresh_ingredients_cache() -> Dict[str, Any]:
    """
    Manually refresh the ingredient cache from the database.
    
    Returns:
        Dict containing refresh operation result
    """
    try:
        success = await refresh_ingredient_cache()
        
        if success:
            stats = get_ingredient_cache_stats()
            return {
                "success": True,
                "message": "Ingredient cache refreshed successfully",
                "cache_stats": stats
            }
        else:
            return {
                "success": False,
                "message": "Failed to refresh ingredient cache"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing cache: {str(e)}")


@router.get("/ingredients/names", summary="Get all ingredient names")
async def get_all_ingredient_names() -> Dict[str, Any]:
    """
    Get all ingredient names from the cache for OCR matching.
    
    Returns:
        Dict containing all ingredient names
    """
    try:
        names = get_ingredient_names_for_ocr()
        
        return {
            "total_ingredients": len(names),
            "ingredient_names": names,
            "cache_stats": get_ingredient_cache_stats()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ingredient names: {str(e)}")


@router.get("/ingredients/search", summary="Search ingredient matches")
async def search_ingredients(
    text: str,
    max_matches: int = 5
) -> Dict[str, Any]:
    """
    Search for ingredient matches in provided text.
    
    This endpoint can be used to test OCR matching functionality.
    
    Args:
        text: Text to search for ingredient matches
        max_matches: Maximum number of matches to return
        
    Returns:
        Dict containing matching ingredient names
    """
    try:
        matches = search_ingredient_matches(text, max_matches)
        
        return {
            "search_text": text,
            "max_matches": max_matches,
            "found_matches": len(matches),
            "matches": matches
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching ingredients: {str(e)}")


# Export router
__all__ = ["router"]
