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
    diet_type: DietType
    disliked_items: List[str] = []
    cuisine_preferences: List[str] = []
    goal: Goal
    allergies: List[str] = []
    calorie_target: int
    preferred_meal_times: Dict[str, str] = {}


class Preferences(PreferencesBase):
    """Schema für Preferences-Daten aus der Datenbank."""
    id: UUID
    user_id: UUID


class PantryItemBase(BaseModel):
    """Basis-Schema für PantryItem-Daten."""
    name: str
    quantity: float
    unit: Unit
    category: str
    expiry_date: Optional[date] = None


class PantryItem(PantryItemBase):
    """Schema für PantryItem-Daten aus der Datenbank."""
    id: UUID
    user_id: UUID
    added_at: datetime


class RecipeBase(BaseModel):
    """Basis-Schema für Recipe-Daten."""
    source: RecipeSource
    source_url: Optional[str] = None
    title: str
    description: str
    image_url: Optional[str] = None
    ingredients: List[Dict[str, Any]]
    instructions: str
    estimated_time: int
    difficulty: Difficulty
    calories: Optional[int] = None
    user_generated: bool = False
    tags: List[str] = []
    nutrition: Dict[str, Any] = {}


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
    saved_at: datetime


class MealPlanBase(BaseModel):
    """Basis-Schema für MealPlan-Daten."""
    week_start_date: date
    meals: List[Dict[str, Any]]
    budget_allocated: Optional[float] = None
    notes: Optional[str] = None


class MealPlan(MealPlanBase):
    """Schema für MealPlan-Daten aus der Datenbank."""
    id: UUID
    user_id: UUID
    generated_at: datetime


class ShoppingListBase(BaseModel):
    """Basis-Schema für ShoppingList-Daten."""
    items: List[Dict[str, Any]]


class ShoppingList(ShoppingListBase):
    """Schema für ShoppingList-Daten aus der Datenbank."""
    id: UUID
    user_id: UUID
    plan_id: Optional[UUID] = None
    created_at: datetime


# Response Models mit flexiblen Schemas für Datenbankabfragen
class DatabaseResponse(BaseModel):
    """Flexibles Schema für Datenbankresponses."""
    model_config = {"extra": "allow"}
    
    def __init__(self, **data) -> None:
        super().__init__(**data)