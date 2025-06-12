from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from uuid import UUID
from enum import Enum


class DietType(str, Enum):
    vegan = "vegan"
    vegetarian = "vegetarian"
    keto = "keto"
    paleo = "paleo"
    omnivore = "omnivore"


class Goal(str, Enum):
    weight_loss = "weight_loss"
    weight_gain = "weight_gain"
    maintenance = "maintenance"
    none = "none"


class Unit(str, Enum):
    g = "g"
    ml = "ml"
    pcs = "pcs"
    kg = "kg"
    l = "l"
    tbsp = "tbsp"
    tsp = "tsp"
    cup = "cup"


class RecipeSource(str, Enum):
    imported = "imported"
    generated = "generated"
    user_submitted = "user_submitted"


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class AuthProvider(str, Enum):
    email = "email"
    google = "google"
    apple = "apple"


# Base Models
class IngredientMasterBase(BaseModel):
    """Basis-Schema für IngredientMaster-Daten."""
    name: str
    calories_per_100g: float
    proteins_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    price_per_100g_cents: int


class IngredientMaster(IngredientMasterBase):
    """Schema für IngredientMaster-Daten aus der Datenbank."""
    ingredient_id: UUID


class UserBase(BaseModel):
    """Basis-Schema für User-Daten."""
    email: str
    auth_provider: AuthProvider = AuthProvider.email
    onboarding_done: bool = False


class User(UserBase):
    """Schema für User-Daten aus der Datenbank."""
    id: UUID
    hashed_password: str
    created_at: datetime
    last_login: Optional[datetime] = None


class PreferencesBase(BaseModel):
    """Basis-Schema für Preferences-Daten."""
    diet_type: str
    disliked_items: Optional[Dict[str, Any]] = None
    cuisine_preferences: Optional[Dict[str, Any]] = None
    goal: Optional[str] = None
    allergies: Optional[Dict[str, Any]] = None
    calorie_target: Optional[int] = None
    preferred_meal_times: Optional[Dict[str, Any]] = None


class Preferences(PreferencesBase):
    """Schema für Preferences-Daten aus der Datenbank."""
    id: UUID
    user_id: UUID


class PantryItemBase(BaseModel):
    """Basis-Schema für PantryItem-Daten."""
    name: str
    quantity: float
    unit: str
    category: Optional[str] = None
    expiry_date: Optional[date] = None


class PantryItem(PantryItemBase):
    """Schema für PantryItem-Daten aus der Datenbank."""
    id: UUID
    user_id: UUID
    added_at: datetime


class RecipeBase(BaseModel):
    """Basis-Schema für Recipe-Daten."""
    source: str
    source_url: Optional[str] = None
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    ingredients: Dict[str, Any]  # JSONB field
    instructions: str
    estimated_time: Optional[int] = None
    difficulty: Optional[str] = None
    calories: Optional[int] = None
    user_generated: bool = False
    tags: Optional[str] = None
    nutrition: Optional[Dict[str, Any]] = None  # JSONB field


class Recipe(RecipeBase):
    """Schema für Recipe-Daten aus der Datenbank."""
    id: UUID
    created_at: datetime


class SavedRecipeBase(BaseModel):
    """Basis-Schema für SavedRecipe-Daten."""
    user_id: UUID
    recipe_id: UUID


class SavedRecipe(SavedRecipeBase):
    """Schema für SavedRecipe-Daten aus der Datenbank."""
    created_at: datetime


class MealPlanBase(BaseModel):
    """Basis-Schema für MealPlan-Daten."""
    week_start_date: date
    meals: Optional[Dict[str, Any]] = None  # JSONB field
    budget_allocated: Optional[float] = None
    notes: Optional[str] = None


class MealPlan(MealPlanBase):
    """Schema für MealPlan-Daten aus der Datenbank."""
    id: UUID
    user_id: UUID
    generated_at: datetime


class ShoppingListBase(BaseModel):
    """Basis-Schema für ShoppingList-Daten."""
    items: Optional[Dict[str, Any]] = None  # JSONB field


class ShoppingList(ShoppingListBase):
    """Schema für ShoppingList-Daten aus der Datenbank."""
    id: UUID
    user_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    created_at: datetime


# Response Models mit flexiblen Schemas für Datenbankabfragen
class DatabaseResponse(BaseModel):
    """Flexibles Schema für Datenbankresponses."""
    model_config = {"extra": "allow"}
    
    def __init__(self, **data) -> None:
        super().__init__(**data)