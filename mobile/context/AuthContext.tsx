import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
// import { supabase } from '@/utils/supabase'; // Supabase client removed
import { User } from '@/types/api';
// import { Session } from '@supabase/supabase-js'; // Supabase Session type removed
import { API_BASE_URL } from '@env';

// Define a minimal local Session type to match the mockSession structure
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
  user: MockSessionUser; // Use the locally defined user type for the mock
  expires_in: number;
  expires_at: number;
  refresh_token: string;
}

interface AuthContextType {
  user: User | null;
  session: LocalSession | null; // Use local Session type
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: any | null }>;
  signUp: (email: string, password: string) => Promise<{ error: any | null, data: any | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: any | null }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  // Mock user and session for bypassing login
  const mockUser: User = {
    id: 'mock-user-id',
    email: 'test@example.com',
    created_at: new Date().toISOString(),
    // Add any other required fields from your User type in mobile/types/supabase.ts
    // Ensure all non-optional fields from your User type are present
  };

  const mockSession: LocalSession = { // Use local Session type
    access_token: 'mock-access-token',
    token_type: 'bearer',
    user: {
      id: mockUser.id,
      aud: 'authenticated',
      role: 'authenticated',
      email: mockUser.email,
      email_confirmed_at: new Date().toISOString(),
      phone: '',
      confirmed_at: new Date().toISOString(),
      last_sign_in_at: new Date().toISOString(),
      app_metadata: { provider: 'email', providers: ['email'] },
      user_metadata: {},
      created_at: mockUser.created_at,
      updated_at: new Date().toISOString(),
      // Add any other required fields from Supabase's User type if your Session type expects them
    } as any, // Using 'as any' here to simplify mock, ensure it matches Session's user type structure
    expires_in: 3600,
    expires_at: Math.floor(Date.now() / 1000) + 3600,
    refresh_token: 'mock-refresh-token',
  };

  const [user, setUser] = useState<User | null>(mockUser);
  const [session, setSession] = useState<LocalSession | null>(mockSession); // Use local Session type
  const [loading, setLoading] = useState(false); // Start with loading false

  // useEffect(() => {
  //   // Set up listener for auth changes
  //   const { data: authListener } = supabase.auth.onAuthStateChange(
  //     async (event, currentSession) => {
  //       setSession(currentSession);
  //       setUser(currentSession?.user?.email ? (currentSession.user as User) : null);
  //       setLoading(false);
  //     }
  //   );
  //
  //   // Get initial session
  //   supabase.auth.getSession().then(({ data: { session: currentSession } }) => {
  //     setSession(currentSession);
  //     setUser(currentSession?.user?.email ? (currentSession.user as User) : null);
  //     setLoading(false);
  //   });
  //
  //   return () => {
  //     authListener?.subscription.unsubscribe();
  //   };
  // }, []);

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    console.warn('signIn function is not implemented for custom backend yet.');
    // TODO: Implement signIn with your custom backend
    setLoading(false);
    return { error: { message: 'Sign in not implemented' } };
  };

  const signUp = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, user_metadata: {} }),
      });

      const responseData = await response.json();

      if (response.ok) {
        // Assuming responseData is { user: ApiUser, session: ApiSession }
        // And ApiSession contains session.user which is compatible with the User type
        setSession(responseData.session);
        setUser(responseData.session.user); // Or responseData.user if that's preferred and compatible
        setLoading(false);
        return { data: responseData, error: null };
      } else {
        let errorMessage = 'Sign up failed.';
        if (responseData.detail && Array.isArray(responseData.detail) && responseData.detail.length > 0) {
          errorMessage = responseData.detail.map((err: any) => err.msg).join('; ');
        } else if (responseData.message) {
          errorMessage = responseData.message;
        } else if (typeof responseData === 'string') { // Fallback for plain text error
          errorMessage = responseData;
        }
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
    console.warn('signOut function is not implemented for custom backend yet.');
    // TODO: Implement signOut with your custom backend
    // For now, to make the mock login bypass work with a sign out button:
    setUser(null);
    setSession(null);
    // This will likely redirect to auth screens if your root layout handles it.
  };

  const resetPassword = async (email: string) => {
    console.warn('resetPassword function is not implemented for custom backend yet.');
    // TODO: Implement resetPassword with your custom backend
    return { error: { message: 'Reset password not implemented' } };
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