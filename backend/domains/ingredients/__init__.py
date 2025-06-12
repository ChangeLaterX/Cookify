"""
Ingredients Domain.

This domain handles ingredient master data management including nutritional
information, pricing, and search functionality for the Cookify application.
"""

from .routes import router
from .schemas import (
    IngredientMasterCreate,
    IngredientMasterUpdate,
    IngredientMasterResponse,
    IngredientListResponse,
)
from .services import (
    get_all_ingredients,
    get_ingredient_by_id,
    create_ingredient,
    update_ingredient,
    delete_ingredient,
    search_ingredients,
)

__all__ = [
    "router",
    "IngredientMasterCreate",
    "IngredientMasterUpdate",
    "IngredientMasterResponse",
    "IngredientListResponse",
    "get_all_ingredients",
    "get_ingredient_by_id",
    "create_ingredient",
    "update_ingredient",
    "delete_ingredient",
    "search_ingredients",
]
