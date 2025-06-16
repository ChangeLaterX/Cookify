import React from 'react';
import { StyleSheet, ActivityIndicator, View } from 'react-native';
import { Tabs, router } from 'expo-router';
import Colors from '@/constants/Colors';
import { Home, ShoppingBasket, UtensilsCrossed, User, ClipboardList } from 'lucide-react-native';
import { useAuth } from '@/context/AuthContext';

export default function TabLayout() {
  const { user, loading } = useAuth();

  React.useEffect(() => {
    if (!loading && !user) {
      router.replace('/(auth)/login');
    }
  }, [user, loading]);

  // While loading, render nothing (or a loading indicator)
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary[500]} />
      </View>
    );
  }

  // If no user is logged in, render nothing while redirecting
  if (!user) {
    return null;
  }

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarActiveTintColor: Colors.primary[500],
        tabBarInactiveTintColor: Colors.neutral[400],
        tabBarLabelStyle: styles.tabBarLabel,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => (
            <Home size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="pantry/index" // Explicitly target pantry/index.tsx
        options={{
          title: 'Pantry', // Set the desired title
          tabBarIcon: ({ color, size }) => (
            <ShoppingBasket size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="recipes/index" // Explicitly target recipes/index.tsx
        options={{
          title: 'Recipes', // Set the desired title
          tabBarIcon: ({ color, size }) => (
            <UtensilsCrossed size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="shopping-list"
        options={{
          title: 'Shopping List',
          tabBarIcon: ({ color, size }) => (
            <ClipboardList size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <User size={size} color={color} />
          ),
        }}
      />
      {/* Screens that are part of the (tabs) group but not actual tabs */}
      <Tabs.Screen name="alerts" options={{ href: null }} />
      <Tabs.Screen name="scan-receipt" options={{ href: null }} />
      {/* Pantry sub-screens */}
      <Tabs.Screen name="pantry/add" options={{ href: null }} />
      <Tabs.Screen name="pantry/[id]" options={{ href: null }} />
      <Tabs.Screen name="pantry/edit/[id]" options={{ href: null }} />
      {/* Recipes sub-screens */}
      <Tabs.Screen name="recipes/[id]" options={{ href: null }} />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: Colors.neutral[200],
    height: 60,
    paddingBottom: 6,
    paddingTop: 6,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  tabBarLabel: {
    fontFamily: 'Inter-Medium',
    fontSize: 12,
  },
   loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});