export interface User {
  id: string;
  email: string;
  created_at: string;
  user_metadata?: { [key: string]: any };
}

export interface PantryItem {
  id: string;
  user_id: string;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  purchase_date: string;
  expiration_date: string;
  notes?: string;
  image_url?: string;
  created_at: string;
}

export interface Recipe {
  id: string;
  name: string;
  description: string;
  instructions: string;
  cooking_time: number;
  serving_size: number;
  image_url?: string;
  ingredients: Ingredient[];
}

export interface Ingredient {
  id: string;
  recipe_id: string;
  name: string;
  quantity: number;
  unit: string;
}

export interface ShoppingListItem {
  id: string;
  user_id: string;
  name: string;
  category?: string;
  quantity: number;
  unit?: string;
  is_completed: boolean;
  created_at: string;
}

export interface FoodCategory {
  id: string;
  name: string;
  average_shelf_life: number; // in days
  storage_tips: string;
}