import { Redirect } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import LoginScreen from './(auth)/login';

export default function Index() {
  const { user, loading } = useAuth();

  // While loading, show nothing
  if (loading) {
    return null;
  }

  // If not authenticated, render the LoginScreen directly
  if (!user) {
    return <LoginScreen />;
  } else {
    return <Redirect href="/(tabs)" />;
  }
}