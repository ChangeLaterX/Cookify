"""
Database Models for Ingredients Domain.
Defines the data structure for ingredient master data.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID


class IngredientMaster:
    """
    Model representing an ingredient in the master database.
    Maps to the public.ingredient_master table.
    """

    def __init__(
        self,
        ingredient_id: UUID,
        name: str,
        calories_per_100g: float,
        proteins_per_100g: float,
        fat_per_100g: float,
        carbs_per_100g: float,
        price_per_100g_cents: int,
    ):
        self.ingredient_id = ingredient_id
        self.name = name
        self.calories_per_100g = calories_per_100g
        self.proteins_per_100g = proteins_per_100g
        self.fat_per_100g = fat_per_100g
        self.carbs_per_100g = carbs_per_100g
        self.price_per_100g_cents = price_per_100g_cents

    @classmethod
    def from_dict(cls, data: dict) -> "IngredientMaster":
        """Create IngredientMaster instance from dictionary."""
        return cls(
            ingredient_id=data["ingredient_id"],
            name=data["name"],
            calories_per_100g=data["calories_per_100g"],
            proteins_per_100g=data["proteins_per_100g"],
            fat_per_100g=data["fat_per_100g"],
            carbs_per_100g=data["carbs_per_100g"],
            price_per_100g_cents=data["price_per_100g_cents"],
        )

    def to_dict(self) -> dict:
        """Convert IngredientMaster instance to dictionary."""
        return {
            "ingredient_id": self.ingredient_id,
            "name": self.name,
            "calories_per_100g": self.calories_per_100g,
            "proteins_per_100g": self.proteins_per_100g,
            "fat_per_100g": self.fat_per_100g,
            "carbs_per_100g": self.carbs_per_100g,
            "price_per_100g_cents": self.price_per_100g_cents,
        }

    def __repr__(self) -> str:
        return f"<IngredientMaster(id={self.ingredient_id}, name='{self.name}')>"
