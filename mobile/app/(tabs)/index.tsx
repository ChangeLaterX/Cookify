import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import { usePantry } from '@/context/PantryContext';
import { useRecipes } from '@/context/RecipeContext';
import Colors from '@/constants/Colors';
import ExpirationAlert from '@/components/ExpirationAlert';
import RecipeCard from '@/components/RecipeCard';
import { Bell, Plus, ShoppingCart } from 'lucide-react-native';
import Button from '@/components/ui/Button';

export default function HomeScreen() {
  const { user } = useAuth();
  const { items: pantryItems, getExpiringItems } = usePantry();
  const { suggestedRecipes } = useRecipes();

  const expiringItems = getExpiringItems();

  if (!user) {
    return null;
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Hello,</Text>
            <Text style={styles.username}>{user.email?.split('@')[0] || 'Chef'}</Text>
          </View>
          <Pressable
            style={styles.notificationButton}
            onPress={() => router.push('/(tabs)/alerts')}
          >
            {expiringItems.length > 0 && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{expiringItems.length}</Text>
              </View>
            )}
            <Bell size={24} color={Colors.neutral[800]} />
          </Pressable>
        </View>

        <View style={styles.quickActionsContainer}>
          <Pressable
            style={styles.quickActionButton}
            onPress={() => router.push('/(tabs)/pantry/add')}
          >
            <Plus size={24} color="white" />
            <Text style={styles.quickActionText}>Add Item</Text>
          </Pressable>
          
          <Pressable
            style={[styles.quickActionButton, { backgroundColor: Colors.secondary[500] }]}
            onPress={() => router.push('/(tabs)/shopping-list')}
          >
            <ShoppingCart size={24} color="white" />
            <Text style={styles.quickActionText}>Shopping List</Text>
          </Pressable>
          
          <Pressable
            style={[styles.quickActionButton, { backgroundColor: Colors.accent[500] }]}
            onPress={() => router.push('/(tabs)/scan-receipt')}
          >
            <View style={styles.cameraIcon}>
              <Text style={styles.cameraIconText}>📷</Text>
            </View>
            <Text style={styles.quickActionText}>Scan Receipt</Text>
          </Pressable>
        </View>

        {/* Expiration Alerts */}
        {expiringItems.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Expiration Alerts</Text>
              <Pressable onPress={() => router.push('/(tabs)/alerts')}>
                <Text style={styles.seeAllText}>See all</Text>
              </Pressable>
            </View>
            
            <View style={styles.expirationAlerts}>
              {expiringItems.slice(0, 3).map((item) => (
                <ExpirationAlert 
                  key={item.id} 
                  item={item} 
                  onPress={() => router.push(`/(tabs)/pantry/${item.id}`)} 
                />
              ))}
            </View>
          </View>
        )}

        {/* Recipe Suggestions */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recipe Suggestions</Text>
            <Pressable onPress={() => router.push('/(tabs)/recipes')}>
              <Text style={styles.seeAllText}>See all</Text>
            </Pressable>
          </View>
          
          {suggestedRecipes.length > 0 ? (
            <View style={styles.recipesContainer}>
              {suggestedRecipes.slice(0, 3).map((recipe) => (
                <RecipeCard 
                  key={recipe.id} 
                  recipe={recipe}
                  onPress={() => router.push(`/(tabs)/recipes/${recipe.id}`)}
                />
              ))}
            </View>
          ) : (
            <View style={styles.emptyRecipesContainer}>
              <Image
                source={{ uri: 'https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg' }}
                style={styles.emptyRecipesImage}
              />
              <Text style={styles.emptyRecipesTitle}>No recipe suggestions yet</Text>
              <Text style={styles.emptyRecipesText}>
                Add more items to your pantry to get personalized recipe recommendations.
              </Text>
              <Button
                title="Add Pantry Items"
                onPress={() => router.push('/(tabs)/pantry/add')}
                style={styles.emptyRecipesButton}
              />
            </View>
          )}
        </View>

        {/* Pantry Summary */}
        <View style={[styles.section, styles.pantryStatsSection]}>
          <Text style={styles.sectionTitle}>Pantry Summary</Text>
          
          <View style={styles.statsContainer}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{pantryItems.length}</Text>
              <Text style={styles.statLabel}>Total Items</Text>
            </View>
            
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{expiringItems.length}</Text>
              <Text style={styles.statLabel}>Expiring Soon</Text>
            </View>
            
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{Object.keys(
                pantryItems.reduce((acc, item) => {
                  acc[item.category] = true;
                  return acc;
                }, {} as Record<string, boolean>)
              ).length}</Text>
              <Text style={styles.statLabel}>Categories</Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.neutral[50],
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 32,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 20,
  },
  greeting: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
  },
  username: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 24,
    color: Colors.neutral[800],
  },
  notificationButton: {
    position: 'relative',
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.neutral[100],
    justifyContent: 'center',
    alignItems: 'center',
  },
  badge: {
    position: 'absolute',
    top: 0,
    right: 0,
    minWidth: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: Colors.error.main,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1,
  },
  badgeText: {
    fontFamily: 'Inter-Bold',
    color: 'white',
    fontSize: 10,
    paddingHorizontal: 4,
  },
  quickActionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    marginBottom: 24,
  },
  quickActionButton: {
    flex: 1,
    backgroundColor: Colors.primary[500],
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 8,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  quickActionText: {
    fontFamily: 'Inter-Medium',
    color: 'white',
    marginTop: 8,
    fontSize: 12,
    textAlign: 'center',
  },
  cameraIcon: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  cameraIconText: {
    fontSize: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    marginBottom: 16,
  },
  sectionTitle: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 18,
    color: Colors.neutral[800],
  },
  seeAllText: {
    fontFamily: 'Inter-Medium',
    fontSize: 14,
    color: Colors.primary[600],
  },
  expirationAlerts: {
    paddingHorizontal: 24,
  },
  recipesContainer: {
    paddingHorizontal: 24,
  },
  emptyRecipesContainer: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    margin: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  emptyRecipesImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    marginBottom: 16,
  },
  emptyRecipesTitle: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 18,
    color: Colors.neutral[800],
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyRecipesText: {
    fontFamily: 'Inter-Regular',
    fontSize: 14,
    color: Colors.neutral[600],
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  emptyRecipesButton: {
    minWidth: 180,
  },
  pantryStatsSection: {
    paddingHorizontal: 24,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 1,
  },
  statNumber: {
    fontFamily: 'Poppins-Bold',
    fontSize: 24,
    color: Colors.primary[500],
    marginBottom: 4,
  },
  statLabel: {
    fontFamily: 'Inter-Medium',
    fontSize: 12,
    color: Colors.neutral[600],
    textAlign: 'center',
  },
});