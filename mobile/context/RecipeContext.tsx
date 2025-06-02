import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { supabase } from '@/utils/supabase';
import { Recipe } from '@/types/supabase';
import { usePantry } from './PantryContext';

interface RecipeContextType {
  recipes: Recipe[];
  suggestedRecipes: Recipe[];
  loading: boolean;
  error: string | null;
  fetchRecipes: () => Promise<void>;
  getSuggestedRecipes: () => Promise<void>;
  getRecipeById: (id: string) => Recipe | undefined;
}

const RecipeContext = createContext<RecipeContextType | undefined>(undefined);

export const RecipeProvider = ({ children }: { children: ReactNode }) => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [suggestedRecipes, setSuggestedRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { items: pantryItems } = usePantry();

  useEffect(() => {
    fetchRecipes();
  }, []);

  useEffect(() => {
    if (pantryItems.length > 0) {
      getSuggestedRecipes();
    }
  }, [pantryItems]);

  const fetchRecipes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const { data, error } = await supabase
        .from('recipes')
        .select(`
          *,
          ingredients:recipe_ingredients(*)
        `);
      
      if (error) throw error;
      
      setRecipes(data || []);
    } catch (err: any) {
      setError(err.message);
      console.error('Error fetching recipes:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSuggestedRecipes = async () => {
    // For MVP, we'll do a simple matching algorithm
    // More sophisticated algorithms could be implemented later
    
    const pantryIngredients = pantryItems.map(item => item.name.toLowerCase());
    
    const matchedRecipes = recipes
      .map(recipe => {
        const recipeIngredients = recipe.ingredients.map(ing => ing.name.toLowerCase());
        
        // Count how many ingredients we have in pantry
        const matchCount = recipeIngredients.filter(ing => 
          pantryIngredients.some(pItem => pItem.includes(ing) || ing.includes(pItem))
        ).length;
        
        // Calculate match percentage
        const matchPercentage = recipeIngredients.length > 0 
          ? (matchCount / recipeIngredients.length) * 100 
          : 0;
        
        return { 
          recipe, 
          matchCount,
          matchPercentage 
        };
      })
      .filter(item => item.matchPercentage >= 50) // Match at least 50% of ingredients
      .sort((a, b) => b.matchPercentage - a.matchPercentage)
      .map(item => item.recipe);
    
    setSuggestedRecipes(matchedRecipes);
  };

  const getRecipeById = (id: string) => {
    return recipes.find(recipe => recipe.id === id);
  };

  const value: RecipeContextType = {
    recipes,
    suggestedRecipes,
    loading,
    error,
    fetchRecipes,
    getSuggestedRecipes,
    getRecipeById,
  };

  return <RecipeContext.Provider value={value}>{children}</RecipeContext.Provider>;
};

export const useRecipes = (): RecipeContextType => {
  const context = useContext(RecipeContext);
  if (!context) {
    throw new Error('useRecipes must be used within a RecipeProvider');
  }
  return context;
};