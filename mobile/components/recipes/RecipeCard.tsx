import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity, Image } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Recipe } from 'shared';
import { Clock, ChefHat } from 'lucide-react-native';
import { useRouter } from 'expo-router';

interface RecipeCardProps {
  recipe: Recipe;
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  const { colors } = useTheme();
  const router = useRouter();
  
  const handlePress = () => {
    router.push(`/recipes/${recipe.id}`);
  };
  
  // Get match percentage color
  const getMatchColor = (percentage: number) => {
    if (percentage >= 90) return colors.success;
    if (percentage >= 70) return colors.primary;
    if (percentage >= 50) return colors.warning;
    return colors.textSecondary;
  };

  return (
    <TouchableOpacity
      style={[
        styles.card,
        { backgroundColor: colors.card, borderColor: colors.border },
      ]}
      onPress={handlePress}
    >
      <View style={styles.imageContainer}>
        {recipe.imageUrl ? (
          <Image source={{ uri: recipe.imageUrl }} style={styles.image} />
        ) : (
          <View
            style={[styles.placeholderImage, { backgroundColor: colors.primaryLight }]}
          />
        )}
        
        {recipe.matchPercentage && (
          <View
            style={[
              styles.matchBadge,
              { backgroundColor: getMatchColor(recipe.matchPercentage) },
            ]}
          >
            <Text style={styles.matchText}>{recipe.matchPercentage}%</Text>
          </View>
        )}
      </View>
      
      <View style={styles.content}>
        <Text style={[styles.title, { color: colors.text }]}>{recipe.name}</Text>
        
        <Text
          style={[styles.description, { color: colors.textSecondary }]}
          numberOfLines={2}
        >
          {recipe.description}
        </Text>
        
        <View style={styles.metaContainer}>
          <View style={styles.metaItem}>
            <Clock size={16} color={colors.textSecondary} />
            <Text style={[styles.metaText, { color: colors.textSecondary }]}>
              {recipe.prepTime + recipe.cookTime} min
            </Text>
          </View>
          
          <View style={styles.metaItem}>
            <ChefHat size={16} color={colors.textSecondary} />
            <Text style={[styles.metaText, { color: colors.textSecondary }]}>
              {recipe.difficulty.charAt(0).toUpperCase() + recipe.difficulty.slice(1)}
            </Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 16,
    overflow: 'hidden',
  },
  imageContainer: {
    height: 160,
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  placeholderImage: {
    width: '100%',
    height: '100%',
  },
  matchBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  matchText: {
    color: 'white',
    fontSize: 12,
    fontFamily: 'Poppins-Bold',
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 18,
    fontFamily: 'Poppins-Bold',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
    marginBottom: 16,
  },
  metaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  metaText: {
    fontSize: 12,
    fontFamily: 'Poppins-Medium',
    marginLeft: 4,
  },
});