import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { supabase } from '@/utils/supabase';
import { ShoppingListItem } from '@/types/supabase';
import { useAuth } from './AuthContext';

interface ShoppingListContextType {
  items: ShoppingListItem[];
  loading: boolean;
  error: string | null;
  fetchItems: () => Promise<void>;
  addItem: (item: Omit<ShoppingListItem, 'id' | 'user_id' | 'created_at'>) => Promise<void>;
  updateItem: (id: string, item: Partial<ShoppingListItem>) => Promise<void>;
  deleteItem: (id: string) => Promise<void>;
  toggleItemCompletion: (id: string, isCompleted: boolean) => Promise<void>;
  clearCompletedItems: () => Promise<void>;
}

const ShoppingListContext = createContext<ShoppingListContextType | undefined>(undefined);

export const ShoppingListProvider = ({ children }: { children: ReactNode }) => {
  const [items, setItems] = useState<ShoppingListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchItems();
    } else {
      setItems([]);
      setLoading(false);
    }
  }, [user]);

  const fetchItems = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const { data, error } = await supabase
        .from('shopping_list_items')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: true });
      
      if (error) throw error;
      
      setItems(data || []);
    } catch (err: any) {
      setError(err.message);
      console.error('Error fetching shopping list items:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const addItem = async (item: Omit<ShoppingListItem, 'id' | 'user_id' | 'created_at'>) => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const { data, error } = await supabase
        .from('shopping_list_items')
        .insert([{ ...item, user_id: user.id }])
        .select();
      
      if (error) throw error;
      
      setItems(prev => [...prev, data[0]]);
    } catch (err: any) {
      setError(err.message);
      console.error('Error adding shopping list item:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateItem = async (id: string, item: Partial<ShoppingListItem>) => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const { error } = await supabase
        .from('shopping_list_items')
        .update(item)
        .eq('id', id)
        .eq('user_id', user.id);
      
      if (error) throw error;
      
      setItems(prev => 
        prev.map(i => (i.id === id ? { ...i, ...item } : i))
      );
    } catch (err: any) {
      setError(err.message);
      console.error('Error updating shopping list item:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (id: string) => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const { error } = await supabase
        .from('shopping_list_items')
        .delete()
        .eq('id', id)
        .eq('user_id', user.id);
      
      if (error) throw error;
      
      setItems(prev => prev.filter(i => i.id !== id));
    } catch (err: any) {
      setError(err.message);
      console.error('Error deleting shopping list item:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleItemCompletion = async (id: string, isCompleted: boolean) => {
    await updateItem(id, { is_completed: isCompleted });
  };

  const clearCompletedItems = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const { error } = await supabase
        .from('shopping_list_items')
        .delete()
        .eq('user_id', user.id)
        .eq('is_completed', true);
      
      if (error) throw error;
      
      setItems(prev => prev.filter(i => !i.is_completed));
    } catch (err: any) {
      setError(err.message);
      console.error('Error clearing completed shopping list items:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const value: ShoppingListContextType = {
    items,
    loading,
    error,
    fetchItems,
    addItem,
    updateItem,
    deleteItem,
    toggleItemCompletion,
    clearCompletedItems,
  };

  return <ShoppingListContext.Provider value={value}>{children}</ShoppingListContext.Provider>;
};

export const useShoppingList = (): ShoppingListContextType => {
  const context = useContext(ShoppingListContext);
  if (!context) {
    throw new Error('useShoppingList must be used within a ShoppingListProvider');
  }
  return context;
};