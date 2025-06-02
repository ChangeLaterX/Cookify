import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { supabase } from '@/utils/supabase';
import { PantryItem } from '@/types/supabase';
import { useAuth } from './AuthContext';

interface PantryContextType {
  items: PantryItem[];
  loading: boolean;
  error: string | null;
  fetchItems: () => Promise<void>;
  addItem: (item: Omit<PantryItem, 'id' | 'user_id' | 'created_at'>) => Promise<void>;
  updateItem: (id: string, item: Partial<PantryItem>) => Promise<void>;
  deleteItem: (id: string) => Promise<void>;
  getExpiringItems: () => PantryItem[];
}

const PantryContext = createContext<PantryContextType | undefined>(undefined);

export const PantryProvider = ({ children }: { children: ReactNode }) => {
  const [items, setItems] = useState<PantryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  // Fetch pantry items when user changes
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
        .from('pantry_items')
        .select('*')
        .eq('user_id', user.id)
        .order('expiration_date', { ascending: true });
      
      if (error) throw error;
      
      setItems(data || []);
    } catch (err: any) {
      setError(err.message);
      console.error('Error fetching pantry items:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const addItem = async (item: Omit<PantryItem, 'id' | 'user_id' | 'created_at'>) => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const { data, error } = await supabase
        .from('pantry_items')
        .insert([{ ...item, user_id: user.id }])
        .select();
      
      if (error) throw error;
      
      setItems(prev => [...prev, data[0]]);
    } catch (err: any) {
      setError(err.message);
      console.error('Error adding pantry item:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateItem = async (id: string, item: Partial<PantryItem>) => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const { error } = await supabase
        .from('pantry_items')
        .update(item)
        .eq('id', id)
        .eq('user_id', user.id);
      
      if (error) throw error;
      
      setItems(prev => 
        prev.map(i => (i.id === id ? { ...i, ...item } : i))
      );
    } catch (err: any) {
      setError(err.message);
      console.error('Error updating pantry item:', err.message);
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
        .from('pantry_items')
        .delete()
        .eq('id', id)
        .eq('user_id', user.id);
      
      if (error) throw error;
      
      setItems(prev => prev.filter(i => i.id !== id));
    } catch (err: any) {
      setError(err.message);
      console.error('Error deleting pantry item:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const getExpiringItems = () => {
    // Get items expiring within 3 days
    const now = new Date();
    const threeDaysLater = new Date();
    threeDaysLater.setDate(now.getDate() + 3);
    
    return items.filter(item => {
      const expirationDate = new Date(item.expiration_date);
      return expirationDate <= threeDaysLater && expirationDate >= now;
    });
  };

  const value: PantryContextType = {
    items,
    loading,
    error,
    fetchItems,
    addItem,
    updateItem,
    deleteItem,
    getExpiringItems,
  };

  return <PantryContext.Provider value={value}>{children}</PantryContext.Provider>;
};

export const usePantry = (): PantryContextType => {
  const context = useContext(PantryContext);
  if (!context) {
    throw new Error('usePantry must be used within a PantryProvider');
  }
  return context;
};