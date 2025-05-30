import React, { useState } from 'react';
import { StyleSheet, View, Text, FlatList, TouchableOpacity, RefreshControl } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Plus } from 'lucide-react-native';
import { useRouter } from 'expo-router';
import ShoppingListCard from '@/components/shopping/ShoppingListCard';
import EmptyState from '@/components/common/EmptyState';

// Mock shopping lists data until backend is integrated
const MOCK_SHOPPING_LISTS = [
  {
    id: '1',
    name: 'Weekly Groceries',
    items: [
      { id: '1', name: 'Milk', quantity: 1, unit: 'gallon', category: 'dairy', isChecked: false },
      { id: '2', name: 'Eggs', quantity: 12, unit: 'pcs', category: 'dairy', isChecked: true },
      { id: '3', name: 'Bread', quantity: 1, unit: 'loaf', category: 'bakery', isChecked: false },
      { id: '4', name: 'Apples', quantity: 5, unit: 'pcs', category: 'produce', isChecked: false },
    ],
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'Party Supplies',
    items: [
      { id: '5', name: 'Chips', quantity: 3, unit: 'bags', category: 'snacks', isChecked: false },
      { id: '6', name: 'Soda', quantity: 2, unit: 'bottles', category: 'beverages', isChecked: false },
      { id: '7', name: 'Ice Cream', quantity: 1, unit: 'tub', category: 'frozen', isChecked: false },
    ],
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
];

export default function ShoppingScreen() {
  const { colors } = useTheme();
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);
  
  // In a real app, this would come from a context or API
  const [shoppingLists, setShoppingLists] = useState(MOCK_SHOPPING_LISTS);

  const onRefresh = () => {
    setRefreshing(true);
    // In a real app, this would fetch shopping lists from the API
    setTimeout(() => {
      setRefreshing(false);
    }, 1000);
  };

  const handleCreateList = () => {
    router.push('/shopping/create');
  };

  const dynamicStyles = StyleSheet.create({
    container: {
      backgroundColor: colors.background,
    },
    headerTitle: {
      color: colors.text,
    },
    subtitle: {
      color: colors.textSecondary,
    },
    createButton: {
      backgroundColor: colors.primary,
    },
    createButtonText: {
      color: colors.white,
    },
  });

  return (
    <View style={[styles.container, dynamicStyles.container]}>
      <View style={styles.header}>
        <View>
          <Text style={[styles.headerTitle, dynamicStyles.headerTitle]}>My Lists</Text>
          <Text style={[styles.subtitle, dynamicStyles.subtitle]}>
            Manage your shopping lists
          </Text>
        </View>
        
        <TouchableOpacity
          style={[styles.createButton, dynamicStyles.createButton]}
          onPress={handleCreateList}
        >
          <Plus size={24} color={colors.white} />
        </TouchableOpacity>
      </View>
      
      <FlatList
        data={shoppingLists}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ShoppingListCard shoppingList={item} />}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <EmptyState
            title="No shopping lists"
            description="Create your first shopping list by tapping the + button"
            icon="shopping-cart"
          />
        }
      />
      
      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.createListButton, dynamicStyles.createButton]}
          onPress={handleCreateList}
        >
          <Text style={[styles.createListButtonText, dynamicStyles.createButtonText]}>
            Create New List
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontFamily: 'Poppins-Bold',
  },
  subtitle: {
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
    marginTop: 4,
  },
  createButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    padding: 16,
    paddingTop: 0,
    flexGrow: 1,
  },
  footer: {
    padding: 16,
    paddingTop: 0,
  },
  createListButton: {
    height: 56,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  createListButtonText: {
    fontSize: 16,
    fontFamily: 'Poppins-Bold',
  },
});