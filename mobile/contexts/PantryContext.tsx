import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { PantryItem } from 'shared';
import { useAuth } from './AuthContext';

// Mock data until backend is integrated
const MOCK_PANTRY_ITEMS: PantryItem[] = [
  {
    id: '1',
    name: 'Milk',
    quantity: 1,
    unit: 'gallon',
    category: 'dairy',
    expirationDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
    purchaseDate: new Date().toISOString(),
    isStaple: true,
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'Eggs',
    quantity: 12,
    unit: 'pcs',
    category: 'dairy',
    expirationDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    purchaseDate: new Date().toISOString(),
    isStaple: true,
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '3',
    name: 'Bread',
    quantity: 1,
    unit: 'loaf',
    category: 'dry goods',
    expirationDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    purchaseDate: new Date().toISOString(),
    isStaple: true,
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '4',
    name: 'Chicken Breast',
    quantity: 1,
    unit: 'lb',
    category: 'meat',
    expirationDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    purchaseDate: new Date().toISOString(),
    isStaple: false,
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '5',
    name: 'Apples',
    quantity: 5,
    unit: 'pcs',
    category: 'produce',
    expirationDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    purchaseDate: new Date().toISOString(),
    isStaple: false,
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

interface PantryContextType {
  pantryItems: PantryItem[];
  loading: boolean;
  error: string | null;
  fetchPantryItems: () => Promise<void>;
  addPantryItem: (item: Omit<PantryItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => Promise<PantryItem>;
  updatePantryItem: (id: string, updates: Partial<PantryItem>) => Promise<void>;
  deletePantryItem: (id: string) => Promise<void>;
}

const PantryContext = createContext<PantryContextType>({
  pantryItems: [],
  loading: false,
  error: null,
  fetchPantryItems: async () => {},
  addPantryItem: async () => ({} as PantryItem),
  updatePantryItem: async () => {},
  deletePantryItem: async () => {},
});

export const usePantry = () => useContext(PantryContext);

export const PantryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [pantryItems, setPantryItems] = useState<PantryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  // Fetch pantry items when user changes
  useEffect(() => {
    if (user) {
      fetchPantryItems();
    } else {
      setPantryItems([]);
    }
  }, [user]);

  const fetchPantryItems = async (): Promise<void> => {
    if (!user) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, this would be a Supabase query
      // const { data, error } = await supabase
      //   .from('pantry_items')
      //   .select('*')
      //   .eq('user_id', user.id);
      
      // if (error) throw error;
      
      // setPantryItems(data);
      
      // Mock implementation for now
      setTimeout(() => {
        setPantryItems(MOCK_PANTRY_ITEMS);
        setLoading(false);
      }, 500);
    } catch (err: any) {
      console.error('Error fetching pantry items:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const addPantryItem = async (
    item: Omit<PantryItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>
  ): Promise<PantryItem> => {
    if (!user) throw new Error('User not authenticated');
    
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, this would be a Supabase insert
      // const { data, error } = await supabase
      //   .from('pantry_items')
      //   .insert({
      //     ...item,
      //     user_id: user.id,
      //   })
      //   .select()
      //   .single();
      
      // if (error) throw error;
      
      // Mock implementation for now
      const newItem: PantryItem = {
        ...item,
        id: Math.random().toString(36).substring(2, 9),
        userId: user.id,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      setPantryItems(prev => [...prev, newItem]);
      return newItem;
    } catch (err: any) {
      console.error('Error adding pantry item:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updatePantryItem = async (id: string, updates: Partial<PantryItem>): Promise<void> => {
    if (!user) throw new Error('User not authenticated');
    
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, this would be a Supabase update
      // const { error } = await supabase
      //   .from('pantry_items')
      //   .update({
      //     ...updates,
      //     updated_at: new Date().toISOString(),
      //   })
      //   .eq('id', id)
      //   .eq('user_id', user.id);
      
      // if (error) throw error;
      
      // Mock implementation for now
      setPantryItems(prev =>
        prev.map(item =>
          item.id === id
            ? { ...item, ...updates, updatedAt: new Date().toISOString() }
            : item
        )
      );
    } catch (err: any) {
      console.error('Error updating pantry item:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deletePantryItem = async (id: string): Promise<void> => {
    if (!user) throw new Error('User not authenticated');
    
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, this would be a Supabase delete
      // const { error } = await supabase
      //   .from('pantry_items')
      //   .delete()
      //   .eq('id', id)
      //   .eq('user_id', user.id);
      
      // if (error) throw error;
      
      // Mock implementation for now
      setPantryItems(prev => prev.filter(item => item.id !== id));
    } catch (err: any) {
      console.error('Error deleting pantry item:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return (
    <PantryContext.Provider
      value={{
        pantryItems,
        loading,
        error,
        fetchPantryItems,
        addPantryItem,
        updatePantryItem,
        deletePantryItem,
      }}
    >
      {children}
    </PantryContext.Provider>
  );
};