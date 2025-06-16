import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { router } from 'expo-router';
import { User } from '@/types/api';
import AsyncStorage from '@react-native-async-storage/async-storage';
const API_BASE_URL = "http://dev.krija.info:8000/api"

interface MockSessionUser {
  id: string;
  aud: string;
  role: string;
  email: string;
  email_confirmed_at: string;
  phone: string;
  confirmed_at: string;
  last_sign_in_at: string;
  app_metadata: { provider: string; providers: string[] };
  user_metadata: object;
  created_at: string;
  updated_at: string;
}

interface LocalSession {
  access_token: string;
  token_type: string;
  user: MockSessionUser;
  expires_in: number;
  expires_at: number;
  refresh_token: string;
}

interface AuthContextType {
  user: User | null;
  session: LocalSession | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: any | null }>;
  signUp: (email: string, password: string, username: string) => Promise<{ error: any | null, data: any | null }>;
  signOut: () => Promise<{ error: any | null }>;
  resetPassword: (email: string) => Promise<{ error: any | null }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {

  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<LocalSession | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore session and user from AsyncStorage on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const storedSession = await AsyncStorage.getItem('session');
        const storedUser = await AsyncStorage.getItem('user');
        if (storedSession && storedUser) {
          setSession(JSON.parse(storedSession));
          setUser(JSON.parse(storedUser));
        }
      } catch (e) {
        console.error('Failed to restore session:', e);
      } finally {
        setLoading(false);
      }
    };
    restoreSession();
  }, []);


  const signIn = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const responseData = await response.json();
      console.log('Signin response:', responseData);
      if (response.ok && responseData.success) {
        const { access_token, expires_at, expires_in, refresh_token, token_type } = responseData.data;

        const sessionUser = {
          id: 'mock-user-id',
          aud: 'authenticated',
          role: 'authenticated',
          email: email,
          email_confirmed_at: new Date().toISOString(),
          phone: '',
          confirmed_at: new Date().toISOString(),
          last_sign_in_at: new Date().toISOString(),
          app_metadata: { provider: 'email', providers: ['email'] },
          user_metadata: {},
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        const session = {
          access_token: access_token,
          token_type: token_type,
          user: sessionUser,
          expires_in: expires_in,
          expires_at: Math.floor(new Date(expires_at).getTime()),
          refresh_token: refresh_token,
        };

        setSession(session);
        setUser(sessionUser);
        await AsyncStorage.setItem('session', JSON.stringify(session));
        await AsyncStorage.setItem('user', JSON.stringify(sessionUser));
        setLoading(false);
        setTimeout(() => {
          router.replace('/(tabs)');
        }, 0);

        // router.push('/(tabs)');
        return { error: null };
      } else {
        const errorMessage = getErrorMessage(responseData, 'Sign in failed.');
        setLoading(false);
        return { error: { message: errorMessage } };
      }
    } catch (e: any) {
      console.error('Signin API call error:', e);
      setLoading(false);
      return { error: { message: e.message || 'An unexpected network error occurred.' } };
    }
  };

  const signUp = async (email: string, password: string, username: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, username }),
      });

      const responseData = await response.json();

      if (response.ok && responseData.success) {
        const { access_token, expires_at, expires_in, refresh_token, token_type } = responseData.data;

        const sessionUser = {
          id: 'mock-user-id',
          aud: 'authenticated',
          role: 'authenticated',
          email: email,
          email_confirmed_at: new Date().toISOString(),
          phone: '',
          confirmed_at: new Date().toISOString(),
          last_sign_in_at: new Date().toISOString(),
          app_metadata: { provider: 'email', providers: ['email'] },
          user_metadata: { username: username },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        const session = {
          access_token: access_token,
          token_type: token_type,
          user: sessionUser,
          expires_in: expires_in,
          expires_at: Math.floor(new Date(expires_at).getTime()),
          refresh_token: refresh_token,
        };

        setSession(session);
        setUser(sessionUser);
        setLoading(false);
        router.replace('/(tabs)');
        return { data: responseData, error: null };
      } else {
        const errorMessage = getErrorMessage(responseData, 'Sign up failed.');
        setLoading(false);
        return { data: null, error: { message: errorMessage } };
      }
    } catch (e: any) {
      console.error('Signup API call error:', e);
      setLoading(false);
      return { data: null, error: { message: e.message || 'An unexpected network error occurred.' } };
    }
  };

  const signOut = async () => {
    setLoading(true);
    try {
      // Clear user and session state
      setUser(null);
      setSession(null);
      // Remove persisted session and user from AsyncStorage
      await AsyncStorage.removeItem('session');
      await AsyncStorage.removeItem('user');
      // Navigate to login screen after sign out
      setTimeout(() => {
        router.replace('/(auth)/login');
      }, 0);

      setLoading(false);
      return { error: null };
    } catch (e: any) {
      console.error('Logout API call error:', e);
      setLoading(false);
      return { error: { message: e.message || 'An unexpected network error occurred.' } };
    }
  };

  const resetPassword = async (email: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const responseData = await response.json();

      if (response.ok && responseData.success) {
        setLoading(false);
        return { error: null };
      } else {
        const errorMessage = getErrorMessage(responseData, 'Reset password failed.');
        setLoading(false);
        return { error: { message: errorMessage } };
      }
    } catch (e: any) {
      console.error('Reset password API call error:', e);
      setLoading(false);
      return { error: { message: e.message || 'An unexpected network error occurred.' } };
    }
  };

  const value = {
    user,
    session,
    loading,
    signIn,
    signUp,
    signOut,
    resetPassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const getErrorMessage = (responseData: any, defaultMessage: string) => {
  let errorMessage = defaultMessage;
  if (responseData.detail && Array.isArray(responseData.detail) && responseData.detail.length > 0) {
    errorMessage = responseData.detail.map((err: any) => err.msg).join('; ');
  } else if (responseData.message) {
    errorMessage = responseData.message;
  } else if (typeof responseData === 'string') {
    errorMessage = responseData;
  }
  return errorMessage;
};