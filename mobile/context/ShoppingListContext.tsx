import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
// import { supabase } from '@/utils/supabase'; // Supabase client removed
import { ShoppingListItem } from '@/types/api'; // Assuming this type matches your backend structure for now
import { useAuth } from './AuthContext';
import { API_BASE_URL } from '@env';

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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/shopping-list`, { headers: { /* Auth */ } });
      // if (!response.ok) throw new Error('Failed to fetch shopping list items');
      // const data = await response.json();
      // setItems(data || []);
      console.warn('fetchItems (ShoppingList): API call not implemented');
      setItems([]); // Placeholder
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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/shopping-list`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json', /* Auth */ },
      //   body: JSON.stringify({ ...item, user_id: user.id })
      // });
      // if (!response.ok) throw new Error('Failed to add shopping list item');
      // const newItem = await response.json();
      // setItems(prev => [...prev, newItem]);
      console.warn('addItem (ShoppingList): API call not implemented');
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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/shopping-list/${id}`, {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json', /* Auth */ },
      //   body: JSON.stringify(item)
      // });
      // if (!response.ok) throw new Error('Failed to update shopping list item');
      // setItems(prev =>
      //   prev.map(i => (i.id === id ? { ...i, ...item } : i))
      // );
      console.warn('updateItem (ShoppingList): API call not implemented');
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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/shopping-list/${id}`, {
      //   method: 'DELETE',
      //   headers: { /* Auth */ },
      // });
      // if (!response.ok) throw new Error('Failed to delete shopping list item');
      // setItems(prev => prev.filter(i => i.id !== id));
      console.warn('deleteItem (ShoppingList): API call not implemented');
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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/shopping-list/completed`, {
      //   method: 'DELETE',
      //   headers: { /* Auth */ },
      // });
      // if (!response.ok) throw new Error('Failed to clear completed items');
      // setItems(prev => prev.filter(i => !i.is_completed));
      console.warn('clearCompletedItems (ShoppingList): API call not implemented');
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