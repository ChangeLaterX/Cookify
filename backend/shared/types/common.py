"""
Common type definitions and enums.
"""
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel


class RecipeSource(str, Enum):
    """Recipe source enumeration."""
    USER = "user"
    IMPORTED = "imported"
    API = "api"


class Difficulty(str, Enum):
    """Recipe difficulty enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MealType(str, Enum):
    """Meal type enumeration."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class DatabaseResponse(BaseModel):
    """Standard database response model."""
    data: List[Dict[str, Any]]
    count: Optional[int] = None
    error: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    per_page: int = 50
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        return self.per_page
