import React from 'react';
import { View, Text, Image, StyleSheet, Pressable } from 'react-native';
import { Recipe } from '@/types/supabase';
import Colors from '@/constants/Colors';
import { Clock, Users } from 'lucide-react-native';

interface RecipeCardProps {
  recipe: Recipe;
  matchPercentage?: number;
  onPress: (recipe: Recipe) => void;
}

const RecipeCard: React.FC<RecipeCardProps> = ({ 
  recipe, 
  matchPercentage,
  onPress 
}) => {
  return (
    <Pressable 
      style={styles.container} 
      onPress={() => onPress(recipe)}
    >
      <View style={styles.imageContainer}>
        <Image 
          source={{ 
            uri: recipe.image_url || 'https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg' 
          }} 
          style={styles.image} 
        />
        
        {matchPercentage && (
          <View style={styles.matchBadge}>
            <Text style={styles.matchText}>{Math.round(matchPercentage)}% match</Text>
          </View>
        )}
      </View>
      
      <View style={styles.contentContainer}>
        <Text style={styles.title} numberOfLines={1}>{recipe.name}</Text>
        <Text style={styles.description} numberOfLines={2}>{recipe.description}</Text>
        
        <View style={styles.metaContainer}>
          <View style={styles.metaItem}>
            <Clock size={14} color={Colors.neutral[600]} />
            <Text style={styles.metaText}>{recipe.cooking_time} min</Text>
          </View>
          
          <View style={styles.metaItem}>
            <Users size={14} color={Colors.neutral[600]} />
            <Text style={styles.metaText}>Serves {recipe.serving_size}</Text>
          </View>
        </View>
      </View>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    borderRadius: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    marginBottom: 16,
    width: '100%',
  },
  imageContainer: {
    position: 'relative',
    width: '100%',
    height: 160,
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  matchBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: Colors.primary[500],
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 12,
  },
  matchText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  contentContainer: {
    padding: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
    color: Colors.neutral[800],
  },
  description: {
    fontSize: 14,
    color: Colors.neutral[600],
    marginBottom: 8,
  },
  metaContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaText: {
    fontSize: 12,
    color: Colors.neutral[600],
    marginLeft: 4,
  },
});

export default RecipeCard;