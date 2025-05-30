import React, { useState } from 'react';
import { StyleSheet, View, Text, FlatList, TextInput, TouchableOpacity, RefreshControl } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Search, Filter } from 'lucide-react-native';
import RecipeCard from '@/components/recipes/RecipeCard';
import EmptyState from '@/components/common/EmptyState';
import FilterChip from '@/components/common/FilterChip';

// Mock recipe data until backend is integrated
const MOCK_RECIPES = [
  {
    id: '1',
    name: 'Pasta Carbonara',
    description: 'Classic Italian pasta dish with eggs, cheese, pancetta, and pepper',
    prepTime: 10,
    cookTime: 20,
    servings: 2,
    difficulty: 'medium',
    cuisineType: 'Italian',
    imageUrl: 'https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg?auto=compress&cs=tinysrgb&h=350',
    matchPercentage: 90,
    ingredients: [],
    instructions: [],
    tags: ['pasta', 'quick', 'dinner'],
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'Chicken Stir Fry',
    description: 'Quick and healthy stir fry with chicken and fresh vegetables',
    prepTime: 15,
    cookTime: 10,
    servings: 4,
    difficulty: 'easy',
    cuisineType: 'Asian',
    imageUrl: 'https://images.pexels.com/photos/3763815/pexels-photo-3763815.jpeg?auto=compress&cs=tinysrgb&h=350',
    matchPercentage: 75,
    ingredients: [],
    instructions: [],
    tags: ['chicken', 'quick', 'healthy'],
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '3',
    name: 'Vegetable Curry',
    description: 'Fragrant and spicy vegetable curry with coconut milk',
    prepTime: 20,
    cookTime: 30,
    servings: 4,
    difficulty: 'medium',
    cuisineType: 'Indian',
    imageUrl: 'https://images.pexels.com/photos/2474661/pexels-photo-2474661.jpeg?auto=compress&cs=tinysrgb&h=350',
    matchPercentage: 65,
    ingredients: [],
    instructions: [],
    tags: ['vegetarian', 'spicy', 'curry'],
    userId: '1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
];

const CUISINES = ['All', 'Italian', 'Asian', 'Indian', 'American', 'Mexican'];
const DIFFICULTIES = ['All', 'Easy', 'Medium', 'Hard'];
const MEAL_TYPES = ['All', 'Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert'];

export default function RecipesScreen() {
  const { colors } = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCuisine, setSelectedCuisine] = useState('All');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedMealType, setSelectedMealType] = useState('All');
  const [sortBy, setSortBy] = useState('match'); // 'match', 'time', 'alphabetical'
  
  // Filter recipes based on search and filters
  const filteredRecipes = MOCK_RECIPES.filter(recipe => {
    const matchesSearch = searchQuery === '' || 
      recipe.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recipe.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recipe.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCuisine = selectedCuisine === 'All' || 
      recipe.cuisineType === selectedCuisine;
    
    const matchesDifficulty = selectedDifficulty === 'All' || 
      recipe.difficulty === selectedDifficulty.toLowerCase();
    
    // For meal type, we would need to add this property to the recipe model
    // For now, let's assume all recipes match the meal type filter
    const matchesMealType = true;
    
    return matchesSearch && matchesCuisine && matchesDifficulty && matchesMealType;
  });
  
  // Sort recipes
  const sortedRecipes = [...filteredRecipes].sort((a, b) => {
    if (sortBy === 'match') {
      return b.matchPercentage - a.matchPercentage;
    } else if (sortBy === 'time') {
      return (a.prepTime + a.cookTime) - (b.prepTime + b.cookTime);
    } else { // alphabetical
      return a.name.localeCompare(b.name);
    }
  });

  const onRefresh = () => {
    setRefreshing(true);
    // In a real app, this would fetch recipes from the API
    setTimeout(() => {
      setRefreshing(false);
    }, 1000);
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
    filtersContainer: {
      borderColor: colors.border,
    },
    sectionTitle: {
      color: colors.text,
    },
  });

  return (
    <View style={[styles.container, dynamicStyles.container]}>
      <View style={styles.header}>
        <View style={[styles.searchContainer, dynamicStyles.searchContainer]}>
          <Search size={20} color={colors.textSecondary} />
          <TextInput
            style={[styles.searchInput, dynamicStyles.searchInput]}
            placeholder="Search recipes..."
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
      </View>
      
      {showFilters && (
        <View style={[styles.filtersContainer, dynamicStyles.filtersContainer]}>
          <View style={styles.filterSection}>
            <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>Cuisine</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipContainer}>
              {CUISINES.map(cuisine => (
                <FilterChip
                  key={cuisine}
                  label={cuisine}
                  selected={selectedCuisine === cuisine}
                  onPress={() => setSelectedCuisine(cuisine)}
                />
              ))}
            </ScrollView>
          </View>
          
          <View style={styles.filterSection}>
            <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>Difficulty</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipContainer}>
              {DIFFICULTIES.map(difficulty => (
                <FilterChip
                  key={difficulty}
                  label={difficulty}
                  selected={selectedDifficulty === difficulty}
                  onPress={() => setSelectedDifficulty(difficulty)}
                />
              ))}
            </ScrollView>
          </View>
          
          <View style={styles.filterSection}>
            <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>Sort By</Text>
            <View style={styles.sortOptions}>
              <FilterChip
                label="Best Match"
                selected={sortBy === 'match'}
                onPress={() => setSortBy('match')}
              />
              <FilterChip
                label="Cooking Time"
                selected={sortBy === 'time'}
                onPress={() => setSortBy('time')}
              />
              <FilterChip
                label="Alphabetical"
                selected={sortBy === 'alphabetical'}
                onPress={() => setSortBy('alphabetical')}
              />
            </View>
          </View>
        </View>
      )}
      
      <FlatList
        data={sortedRecipes}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <RecipeCard recipe={item} />}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <EmptyState
            title="No recipes found"
            description={
              searchQuery || selectedCuisine !== 'All' || selectedDifficulty !== 'All'
                ? "Try adjusting your filters or search query"
                : "Add ingredients to your pantry to get recipe suggestions"
            }
            icon="utensils"
          />
        }
      />
    </View>
  );
}

import { ScrollView } from 'react-native-gesture-handler';

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 16,
  },
  searchContainer: {
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
  filtersContainer: {
    padding: 16,
    borderBottomWidth: 1,
  },
  filterSection: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontFamily: 'Poppins-Medium',
    marginBottom: 8,
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'nowrap',
    gap: 8,
  },
  sortOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  listContent: {
    padding: 16,
  },
});