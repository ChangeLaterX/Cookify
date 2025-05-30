import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, FlatList, TextInput, TouchableOpacity, RefreshControl } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { usePantry } from '@/contexts/PantryContext';
import { useSearchParams, useRouter } from 'expo-router';
import { Search, Plus, Filter } from 'lucide-react-native';
import PantryItemCard from '@/components/pantry/PantryItemCard';
import CategoryFilter from '@/components/pantry/CategoryFilter';
import EmptyState from '@/components/common/EmptyState';
import { PantryItem, PantryCategory } from 'shared';

export default function PantryScreen() {
  const { colors } = useTheme();
  const { pantryItems, fetchPantryItems, loading } = usePantry();
  const params = useSearchParams();
  const router = useRouter();
  
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<PantryCategory | 'all'>('all');
  const [showFilters, setShowFilters] = useState(false);
  
  // Get filter from URL params
  const filter = params.filter as string | undefined;

  // Filter items based on search, category, and URL filter
  const filteredItems = pantryItems.filter(item => {
    // Search filter
    const matchesSearch = searchQuery === '' || 
      item.name.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Category filter
    const matchesCategory = selectedCategory === 'all' || 
      item.category === selectedCategory;
    
    // URL filter
    let matchesUrlFilter = true;
    if (filter === 'expiring') {
      const expirationDate = item.expirationDate ? new Date(item.expirationDate) : null;
      const today = new Date();
      const threeDaysLater = new Date();
      threeDaysLater.setDate(today.getDate() + 3);
      
      matchesUrlFilter = expirationDate !== null && 
        expirationDate > today && 
        expirationDate <= threeDaysLater;
    } else if (filter === 'expired') {
      const expirationDate = item.expirationDate ? new Date(item.expirationDate) : null;
      const today = new Date();
      
      matchesUrlFilter = expirationDate !== null && expirationDate < today;
    } else if (filter === 'low-stock') {
      matchesUrlFilter = item.quantity <= 1;
    }
    
    return matchesSearch && matchesCategory && matchesUrlFilter;
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchPantryItems();
    setRefreshing(false);
  };

  const handleCategorySelect = (category: PantryCategory | 'all') => {
    setSelectedCategory(category);
  };

  const dynamicStyles = StyleSheet.create({
    container: {
      backgroundColor: colors.background,
    },
    searchContainer: {
      backgroundColor: colors.card,
      borderColor: colors.border,
    },
    searchInput: {
      color: colors.text,
    },
    filterButton: {
      backgroundColor: showFilters ? colors.primary : colors.card,
    },
    filterIcon: {
      color: showFilters ? colors.white : colors.text,
    },
    addButton: {
      backgroundColor: colors.primary,
    },
    addButtonText: {
      color: colors.white,
    },
    emptyText: {
      color: colors.textSecondary,
    }
  });

  return (
    <View style={[styles.container, dynamicStyles.container]}>
      <View style={styles.header}>
        <View style={[styles.searchContainer, dynamicStyles.searchContainer]}>
          <Search size={20} color={colors.textSecondary} />
          <TextInput
            style={[styles.searchInput, dynamicStyles.searchInput]}
            placeholder="Search pantry items..."
            placeholderTextColor={colors.textSecondary}
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <TouchableOpacity
            style={[styles.filterButton, dynamicStyles.filterButton]}
            onPress={() => setShowFilters(!showFilters)}
          >
            <Filter size={20} color={showFilters ? colors.white : colors.text} />
          </TouchableOpacity>
        </View>
        
        <TouchableOpacity
          style={[styles.addButton, dynamicStyles.addButton]}
          onPress={() => router.push('/pantry/add')}
        >
          <Plus size={24} color={colors.white} />
        </TouchableOpacity>
      </View>
      
      {showFilters && (
        <CategoryFilter
          selectedCategory={selectedCategory}
          onSelectCategory={handleCategorySelect}
        />
      )}
      
      <FlatList
        data={filteredItems}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <PantryItemCard item={item} />}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <EmptyState
            title="No pantry items found"
            description={
              searchQuery || selectedCategory !== 'all' || filter
                ? "Try adjusting your filters or search query"
                : "Add your first pantry item by tapping the + button"
            }
            icon="package"
          />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    padding: 16,
    alignItems: 'center',
    gap: 12,
  },
  searchContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    height: 48,
    borderRadius: 8,
    borderWidth: 1,
    paddingHorizontal: 12,
  },
  searchInput: {
    flex: 1,
    height: '100%',
    marginLeft: 8,
    fontFamily: 'Poppins-Regular',
  },
  filterButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    padding: 16,
    paddingTop: 0,
  },
});