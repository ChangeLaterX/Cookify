import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
// import { supabase } from '@/utils/supabase'; // Supabase client removed
import { PantryItem } from '@/types/api'; // Assuming this type matches your backend structure for now
import { useAuth } from './AuthContext';
import { API_BASE_URL } from '@env';

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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/pantry`, {
      //   headers: {
      //     // Add Authorization header if needed, e.g.,
      //     // 'Authorization': `Bearer ${session?.access_token}`,
      //   },
      // });
      // if (!response.ok) throw new Error('Failed to fetch pantry items');
      // const data = await response.json();
      // setItems(data || []);
      console.warn('fetchItems: API call not implemented');
      setItems([]); // Placeholder
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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/pantry`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     // 'Authorization': `Bearer ${session?.access_token}`,
      //   },
      //   body: JSON.stringify({ ...item, user_id: user.id }) // Adjust payload as needed
      // });
      // if (!response.ok) throw new Error('Failed to add pantry item');
      // const newItem = await response.json();
      // setItems(prev => [...prev, newItem]);
      console.warn('addItem: API call not implemented');
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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/pantry/${id}`, {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     // 'Authorization': `Bearer ${session?.access_token}`,
      //   },
      //   body: JSON.stringify(item)
      // });
      // if (!response.ok) throw new Error('Failed to update pantry item');
      // setItems(prev =>
      //   prev.map(i => (i.id === id ? { ...i, ...item } : i))
      // );
      console.warn('updateItem: API call not implemented');
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
      
      // TODO: Replace with API call to your Python backend
      // Example:
      // const response = await fetch(`${API_BASE_URL}/pantry/${id}`, {
      //   method: 'DELETE',
      //   headers: {
      //     // 'Authorization': `Bearer ${session?.access_token}`,
      //   },
      // });
      // if (!response.ok) throw new Error('Failed to delete pantry item');
      // setItems(prev => prev.filter(i => i.id !== id));
      console.warn('deleteItem: API call not implemented');
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