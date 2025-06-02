import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { useRecipes } from '@/context/RecipeContext';
import RecipeCard from '@/components/RecipeCard';
import Colors from '@/constants/Colors';
import { Search, UtensilsCrossed } from 'lucide-react-native';
import EmptyState from '@/components/EmptyState';

export default function RecipesScreen() {
  const { recipes, suggestedRecipes, loading } = useRecipes();
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filter recipes based on search query
  const filteredRecipes = recipes.filter(recipe => 
    recipe.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    recipe.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const displayedRecipes = searchQuery ? filteredRecipes : suggestedRecipes;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Recipes</Text>
      </View>
      
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Search size={20} color={Colors.neutral[500]} style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search recipes"
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor={Colors.neutral[400]}
          />
        </View>
      </View>
      
      {!searchQuery && (
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>
            Suggested For You
          </Text>
          <Text style={styles.sectionSubtitle}>
            Based on your pantry items
          </Text>
        </View>
      )}
      
      {loading ? (
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Finding recipes for you...</Text>
        </View>
      ) : displayedRecipes.length > 0 ? (
        <FlatList
          data={displayedRecipes}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <RecipeCard 
              recipe={item} 
              onPress={(recipe) => router.push(`/recipes/${recipe.id}`)}
            />
          )}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      ) : (
        <EmptyState
          icon={<UtensilsCrossed size={64} color={Colors.neutral[400]} />}
          title={searchQuery ? "No matching recipes" : "No suggested recipes yet"}
          message={searchQuery 
            ? "Try a different search term or check back later for more recipes." 
            : "Add more items to your pantry to get personalized recipe suggestions."}
          actionLabel={searchQuery ? "Clear Search" : "View All Recipes"}
          onAction={() => searchQuery ? setSearchQuery('') : null}
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
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 16,
  },
  title: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 28,
    color: Colors.neutral[800],
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
  sectionHeader: {
    paddingHorizontal: 24,
    marginBottom: 16,
  },
  sectionTitle: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 18,
    color: Colors.neutral[800],
  },
  sectionSubtitle: {
    fontFamily: 'Inter-Regular',
    fontSize: 14,
    color: Colors.neutral[600],
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
});