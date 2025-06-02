import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, Pressable, TextInput } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { usePantry } from '@/context/PantryContext';
import Colors from '@/constants/Colors';
import PantryItemCard from '@/components/PantryItem';
import EmptyState from '@/components/EmptyState';
import { PantryItem } from '@/types/supabase';
import { Plus, Search, Package, Filter, ScanLine } from 'lucide-react-native';

export default function PantryScreen() {
  const { items, loading, fetchItems } = usePantry();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  
  useEffect(() => {
    fetchItems();
  }, []);
  
  // Get unique categories from pantry items
  const categories = Array.from(
    new Set(items.map(item => item.category))
  );
  
  // Filter items based on search query and selected category
  const filteredItems = items.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory ? item.category === selectedCategory : true;
    return matchesSearch && matchesCategory;
  });

  const renderItem = ({ item }: { item: PantryItem }) => (
    <PantryItemCard 
      item={item} 
      onPress={(item) => router.push(`/pantry/${item.id}`)}
    />
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Pantry</Text>
        
        <View style={styles.headerActions}>
          <Pressable
            style={styles.actionButton}
            onPress={() => router.push('/(tabs)/scan-receipt')}
          >
            <ScanLine size={24} color={Colors.primary[600]} />
          </Pressable>
          <Pressable
            style={[styles.actionButton, styles.addButton]}
            onPress={() => router.push('/(tabs)/pantry/add')}
          >
            <Plus size={24} color="white" />
          </Pressable>
        </View>
      </View>
      
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Search size={20} color={Colors.neutral[500]} style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search pantry items"
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor={Colors.neutral[400]}
          />
        </View>
      </View>
      
      {categories.length > 0 && (
        <FlatList
          horizontal
          data={['All', ...categories]}
          keyExtractor={(item) => item}
          showsHorizontalScrollIndicator={false}
          style={styles.categoriesList}
          contentContainerStyle={styles.categoriesContent}
          renderItem={({ item }) => (
            <Pressable
              style={[
                styles.categoryChip,
                (selectedCategory === item || (item === 'All' && !selectedCategory)) && 
                  styles.selectedCategoryChip
              ]}
              onPress={() => setSelectedCategory(item === 'All' ? null : item)}
            >
              <Text 
                style={[
                  styles.categoryLabel,
                  (selectedCategory === item || (item === 'All' && !selectedCategory)) && 
                    styles.selectedCategoryLabel
                ]}
              >
                {item}
              </Text>
            </Pressable>
          )}
        />
      )}
      
      {loading ? (
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading pantry items...</Text>
        </View>
      ) : filteredItems.length > 0 ? (
        <FlatList
          data={filteredItems}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      ) : items.length > 0 ? (
        <View style={styles.noResultsContainer}>
          <Text style={styles.noResultsText}>No items match your search</Text>
        </View>
      ) : (
        <EmptyState
          icon={<Package size={64} color={Colors.neutral[400]} />}
          title="Your pantry is empty"
          message="Start adding items to your pantry to keep track of what you have and get recipe suggestions."
          actionLabel="Add First Item"
          onAction={() => router.push('/(tabs)/pantry/add')}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.neutral[50],
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 16,
  },
  title: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 28,
    color: Colors.neutral[800],
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12, // Add some space between buttons
    // Common styling for action buttons (e.g., border for scan button)
    borderWidth: 1,
    borderColor: Colors.neutral[300], // Light border for scan button
  },
  addButton: {
    backgroundColor: Colors.primary[500],
    borderColor: Colors.primary[500], // Ensure border matches for consistency or remove if not needed
    elevation: 2, // Keep elevation for the add button
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
  },
  searchContainer: {
    paddingHorizontal: 24,
    marginBottom: 16,
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 12,
    paddingHorizontal: 12,
    height: 48,
    borderWidth: 1,
    borderColor: Colors.neutral[200],
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: '100%',
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[800],
  },
  categoriesList: {
    maxHeight: 50,
    marginBottom: 16,
  },
  categoriesContent: {
    paddingHorizontal: 16,
  },
  categoryChip: {
    backgroundColor: Colors.neutral[100],
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    marginHorizontal: 8,
  },
  selectedCategoryChip: {
    backgroundColor: Colors.primary[500],
  },
  categoryLabel: {
    fontFamily: 'Inter-Medium',
    fontSize: 14,
    color: Colors.neutral[700],
  },
  selectedCategoryLabel: {
    color: 'white',
  },
  listContent: {
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
  },
  noResultsContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  noResultsText: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
    textAlign: 'center',
  },
});