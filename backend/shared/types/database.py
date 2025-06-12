"""
Pydantic models for Supabase database schema.
These models match the actual database structure.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from uuid import UUID


# ============================================================================
# INGREDIENT MASTER TABLE
# ============================================================================

class IngredientMasterBase(BaseModel):
    """Base schema for ingredient_master table."""
    name: str = Field(..., description="Name of the ingredient")
    calories_per_100g: float = Field(..., description="Calories per 100g")
    proteins_per_100g: float = Field(..., description="Proteins per 100g")
    fat_per_100g: float = Field(..., description="Fat per 100g")
    carbs_per_100g: float = Field(..., description="Carbohydrates per 100g")
    price_per_100g_cents: int = Field(..., description="Price per 100g in cents")


class IngredientMasterCreate(IngredientMasterBase):
    """Schema for creating a new ingredient."""
    pass


class IngredientMasterUpdate(BaseModel):
    """Schema for updating an ingredient."""
    name: Optional[str] = None
    calories_per_100g: Optional[float] = None
    proteins_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    price_per_100g_cents: Optional[int] = None


class IngredientMaster(IngredientMasterBase):
    """Complete ingredient master model from database."""
    ingredient_id: UUID


# ============================================================================
# PANTRY ITEMS TABLE
# ============================================================================

class PantryItemBase(BaseModel):
    """Base schema for pantry_items table."""
    name: str = Field(..., description="Name of the pantry item")
    quantity: float = Field(..., description="Quantity of the item")
    unit: str = Field(..., description="Unit of measurement")
    category: Optional[str] = Field(None, description="Category of the item")
    expiry_date: Optional[date] = Field(None, description="Expiry date")


class PantryItemCreate(PantryItemBase):
    """Schema for creating a new pantry item."""
    user_id: UUID


class PantryItemUpdate(BaseModel):
    """Schema for updating a pantry item."""
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    expiry_date: Optional[date] = None


class PantryItem(PantryItemBase):
    """Complete pantry item model from database."""
    id: UUID
    user_id: UUID
    added_at: datetime


# ============================================================================
# RECIPES TABLE
# ============================================================================

class RecipeBase(BaseModel):
    """Base schema for recipes table."""
    source: str = Field(..., description="Source of the recipe")
    source_url: Optional[str] = Field(None, description="URL of the source")
    title: str = Field(..., description="Title of the recipe")
    description: Optional[str] = Field(None, description="Description of the recipe")
    image_url: Optional[str] = Field(None, description="URL of the recipe image")
    ingredients: Dict[str, Any] = Field(..., description="Ingredients as JSONB")
    instructions: str = Field(..., description="Cooking instructions")
    estimated_time: Optional[int] = Field(None, description="Estimated cooking time in minutes")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    calories: Optional[int] = Field(None, description="Calories per serving")
    user_generated: bool = Field(default=False, description="Whether recipe is user-generated")
    tags: Optional[str] = Field(None, description="Recipe tags")
    nutrition: Optional[Dict[str, Any]] = Field(None, description="Nutrition info as JSONB")


class RecipeCreate(RecipeBase):
    """Schema for creating a new recipe."""
    pass


class RecipeUpdate(BaseModel):
    """Schema for updating a recipe."""
    source: Optional[str] = None
    source_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    ingredients: Optional[Dict[str, Any]] = None
    instructions: Optional[str] = None
    estimated_time: Optional[int] = None
    difficulty: Optional[str] = None
    calories: Optional[int] = None
    user_generated: Optional[bool] = None
    tags: Optional[str] = None
    nutrition: Optional[Dict[str, Any]] = None


class Recipe(RecipeBase):
    """Complete recipe model from database."""
    id: UUID
    created_at: datetime


# ============================================================================
# PREFERENCES TABLE
# ============================================================================

class PreferencesBase(BaseModel):
    """Base schema for preferences table."""
    diet_type: str = Field(..., description="Type of diet")
    disliked_items: Optional[Dict[str, Any]] = Field(None, description="Disliked items as JSONB")
    cuisine_preferences: Optional[Dict[str, Any]] = Field(None, description="Cuisine preferences as JSONB")
    goal: Optional[str] = Field(None, description="User's goal")
    allergies: Optional[Dict[str, Any]] = Field(None, description="Allergies as JSONB")
    calorie_target: Optional[int] = Field(None, description="Daily calorie target")
    preferred_meal_times: Optional[Dict[str, Any]] = Field(None, description="Preferred meal times as JSONB")


class PreferencesCreate(PreferencesBase):
    """Schema for creating user preferences."""
    user_id: UUID


class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    diet_type: Optional[str] = None
    disliked_items: Optional[Dict[str, Any]] = None
    cuisine_preferences: Optional[Dict[str, Any]] = None
    goal: Optional[str] = None
    allergies: Optional[Dict[str, Any]] = None
    calorie_target: Optional[int] = None
    preferred_meal_times: Optional[Dict[str, Any]] = None


class Preferences(PreferencesBase):
    """Complete preferences model from database."""
    id: UUID
    user_id: UUID


# ============================================================================
# SAVED RECIPES TABLE
# ============================================================================

class SavedRecipeBase(BaseModel):
    """Base schema for saved_recipes table."""
    user_id: UUID
    recipe_id: UUID


class SavedRecipeCreate(SavedRecipeBase):
    """Schema for creating a saved recipe."""
    pass


class SavedRecipe(SavedRecipeBase):
    """Complete saved recipe model from database."""
    created_at: datetime

    # Optional: Include recipe details when fetched with join
    recipe: Optional[Recipe] = None


# ============================================================================
# MEAL PLANS TABLE
# ============================================================================

class MealPlanBase(BaseModel):
    """Base schema for meal_plans table."""
    week_start_date: date = Field(..., description="Start date of the week")
    meals: Optional[Dict[str, Any]] = Field(None, description="Meals data as JSONB")
    budget_allocated: Optional[float] = Field(None, description="Budget allocated for the week")
    notes: Optional[str] = Field(None, description="Additional notes")


class MealPlanCreate(MealPlanBase):
    """Schema for creating a meal plan."""
    user_id: UUID


class MealPlanUpdate(BaseModel):
    """Schema for updating a meal plan."""
    week_start_date: Optional[date] = None
    meals: Optional[Dict[str, Any]] = None
    budget_allocated: Optional[float] = None
    notes: Optional[str] = None


class MealPlan(MealPlanBase):
    """Complete meal plan model from database."""
    id: UUID
    user_id: UUID
    generated_at: datetime


# ============================================================================
# SHOPPING LISTS TABLE
# ============================================================================

class ShoppingListBase(BaseModel):
    """Base schema for shopping_lists table."""
    items: Optional[Dict[str, Any]] = Field(None, description="Shopping items as JSONB")


class ShoppingListCreate(ShoppingListBase):
    """Schema for creating a shopping list."""
    user_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None


class ShoppingListUpdate(BaseModel):
    """Schema for updating a shopping list."""
    items: Optional[Dict[str, Any]] = None


class ShoppingList(ShoppingListBase):
    """Complete shopping list model from database."""
    id: UUID
    user_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    created_at: datetime


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class DatabaseResponse(BaseModel):
    """Generic response model for database operations."""
    model_config = ConfigDict(extra="allow")
    
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Response model for paginated data."""
    items: List[Any] = []
    total: int = 0
    page: int = 1
    per_page: int = 50
    total_pages: int = 0
