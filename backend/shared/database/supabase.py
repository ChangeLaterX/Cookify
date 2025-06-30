from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client, create_client

from core.config import settings


class SupabaseService:
    """Service class for Supabase operations."""

    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Lazy loading of the Supabase client."""
        if self._client is None:
            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return self._client

    def get_client(self) -> Client:
        """Returns the Supabase client."""
        return self.client

    # Ingredient Master Table Methods
    def get_ingredient_master(self, ingredient_id: Optional[UUID] = None):
        """Retrieves ingredients from the ingredient_master table."""
        query = self.client.table("ingredient_master")
        if ingredient_id:
            return query.eq("ingredient_id", str(ingredient_id)).execute()
        return query.select("*").execute()

    def search_ingredients(self, search_term: str):
        """Searches ingredients based on name."""
        return (
            self.client.table("ingredient_master")
            .select("*")
            .ilike("name", f"%{search_term}%")
            .execute()
        )

    # Pantry Items Methods
    def get_pantry_items(self, user_id: UUID):
        """Retrieves pantry items for a user."""
        return self.client.table("pantry_items").select("*").eq("user_id", str(user_id)).execute()

    def add_pantry_item(self, item_data: Dict[str, Any]):
        """Adds an item to the pantry."""
        return self.client.table("pantry_items").insert(item_data).execute()

    def update_pantry_item(self, item_id: UUID, update_data: Dict[str, Any]):
        """Updates a pantry item."""
        return (
            self.client.table("pantry_items").update(update_data).eq("id", str(item_id)).execute()
        )

    def delete_pantry_item(self, item_id: UUID):
        """Deletes a pantry item."""
        return self.client.table("pantry_items").delete().eq("id", str(item_id)).execute()

    # Recipes Methods
    def get_recipes(self, limit: int = settings.PAGINATION_DEFAULT_PER_PAGE, offset: int = 0):
        """Retrieves recipes."""
        return self.client.table("recipes").select("*").limit(limit).offset(offset).execute()

    def get_recipe_by_id(self, recipe_id: UUID):
        """Retrieves a recipe by ID."""
        return self.client.table("recipes").select("*").eq("id", str(recipe_id)).single().execute()

    def search_recipes(self, search_term: str):
        """Searches recipes based on title or description."""
        return (
            self.client.table("recipes")
            .select("*")
            .or_(f"title.ilike.%{search_term}%,description.ilike.%{search_term}%")
            .execute()
        )

    def add_recipe(self, recipe_data: Dict[str, Any]):
        """Adds a new recipe."""
        return self.client.table("recipes").insert(recipe_data).execute()

    # Preferences Methods
    def get_user_preferences(self, user_id: UUID):
        """Retrieves user preferences."""
        return self.client.table("preferences").select("*").eq("user_id", str(user_id)).execute()

    def upsert_preferences(self, preferences_data: Dict[str, Any]):
        """Creates or updates user preferences."""
        return self.client.table("preferences").upsert(preferences_data).execute()

    # Saved Recipes Methods
    def get_saved_recipes(self, user_id: UUID):
        """Retrieves saved recipes for a user."""
        return (
            self.client.table("saved_recipes")
            .select("*, recipes(*)")
            .eq("user_id", str(user_id))
            .execute()
        )

    def save_recipe(self, user_id: UUID, recipe_id: UUID):
        """Saves a recipe for a user."""
        return (
            self.client.table("saved_recipes")
            .insert({"user_id": str(user_id), "recipe_id": str(recipe_id)})
            .execute()
        )

    def unsave_recipe(self, user_id: UUID, recipe_id: UUID):
        """Removes a saved recipe."""
        return (
            self.client.table("saved_recipes")
            .delete()
            .eq("user_id", str(user_id))
            .eq("recipe_id", str(recipe_id))
            .execute()
        )

    # Meal Plans Methods
    def get_meal_plans(self, user_id: UUID):
        """Retrieves meal plans for a user."""
        return (
            self.client.table("meal_plans")
            .select("*")
            .eq("user_id", str(user_id))
            .order("week_start_date", desc=True)
            .execute()
        )

    def get_meal_plan_by_week(self, user_id: UUID, week_start_date: str):
        """Retrieves meal plan for a specific week."""
        return (
            self.client.table("meal_plans")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("week_start_date", week_start_date)
            .execute()
        )

    def create_meal_plan(self, meal_plan_data: Dict[str, Any]):
        """Creates a new meal plan."""
        return self.client.table("meal_plans").insert(meal_plan_data).execute()

    def update_meal_plan(self, plan_id: UUID, update_data: Dict[str, Any]):
        """Updates a meal plan."""
        return self.client.table("meal_plans").update(update_data).eq("id", str(plan_id)).execute()

    # Shopping Lists Methods
    def get_shopping_lists(self, user_id: UUID):
        """Retrieves shopping lists for a user."""
        return (
            self.client.table("shopping_lists")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .execute()
        )

    def get_shopping_list_by_plan(self, plan_id: UUID):
        """Retrieves shopping list for a specific meal plan."""
        return self.client.table("shopping_lists").select("*").eq("plan_id", str(plan_id)).execute()

    def create_shopping_list(self, shopping_list_data: Dict[str, Any]):
        """Creates a new shopping list."""
        return self.client.table("shopping_lists").insert(shopping_list_data).execute()

    def update_shopping_list(self, list_id: UUID, update_data: Dict[str, Any]):
        """Updates a shopping list."""
        return (
            self.client.table("shopping_lists").update(update_data).eq("id", str(list_id)).execute()
        )

    def delete_shopping_list(self, list_id: UUID):
        """Deletes a shopping list."""
        return self.client.table("shopping_lists").delete().eq("id", str(list_id)).execute()


# Global service instance
supabase_service = SupabaseService()


# Convenience function for backward compatibility
def get_supabase_client() -> Client:
    """Get the Supabase client instance."""
    return supabase_service.client
