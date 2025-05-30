import { BaseItem } from './common';
import { PantryCategory } from './pantry';

export interface RecipeIngredient {
  name: string;
  quantity: number;
  unit: string;
  category: PantryCategory;
  isOptional: boolean;
}

export interface Recipe extends BaseItem {
  name: string;
  description: string;
  ingredients: RecipeIngredient[];
  instructions: string[];
  prepTime: number;
  cookTime: number;
  servings: number;
  difficulty: 'easy' | 'medium' | 'hard';
  cuisineType: string;
  tags: string[];
  imageUrl?: string;
}

export interface RecipeSuggestion {
  recipe: Recipe;
  matchPercentage: number;
  missingIngredients: RecipeIngredient[];
}