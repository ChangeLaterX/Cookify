import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
// import { supabase } from '@/utils/supabase'; // Supabase client removed
import { Recipe } from '@/types/api'; // Assuming this type matches your backend structure for now
import { usePantry } from './PantryContext';
import { API_BASE_URL } from '@env';

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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/recipes`, {
      //   headers: {
      //     // Add Authorization header if needed
      //   },
      // });
      // if (!response.ok) throw new Error('Failed to fetch recipes');
      // const data = await response.json();
      // setRecipes(data || []);
      console.warn('fetchRecipes: API call not implemented');
      setRecipes([]); // Placeholder
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