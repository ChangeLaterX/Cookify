import React from 'react';
import { View, Text, StyleSheet, Image, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, router } from 'expo-router';
import { useRecipes } from '@/context/RecipeContext';
import { useShoppingList } from '@/context/ShoppingListContext';
import Colors from '@/constants/Colors';
import Button from '@/components/ui/Button';
import { ArrowLeft, Clock, Users, Check, ShoppingCart, Heart } from 'lucide-react-native';

export default function RecipeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { getRecipeById } = useRecipes();
  const { addItem } = useShoppingList();
  
  const recipe = getRecipeById(id as string);
  
  if (!recipe) {
    return null;
  }
  
  const handleAddToShoppingList = async () => {
    try {
      // Add all recipe ingredients to shopping list
      for (const ingredient of recipe.ingredients) {
        await addItem({
          name: ingredient.name,
          quantity: ingredient.quantity,
          unit: ingredient.unit,
          is_completed: false,
        });
      }
      
      alert('Added all ingredients to your shopping list!');
    } catch (error) {
      console.error('Error adding to shopping list:', error);
      alert('Failed to add ingredients to shopping list.');
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <ArrowLeft size={24} color="white" />
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.favoriteButton}>
          <Heart size={24} color="white" fill="white" />
        </TouchableOpacity>
      </View>
      
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.imageContainer}>
          <Image 
            source={{ 
              uri: recipe.image_url || 'https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg'
            }} 
            style={styles.image} 
          />
          <View style={styles.imageGradient} />
        </View>
        
        <View style={styles.contentContainer}>
          <Text style={styles.title}>{recipe.name}</Text>
          
          <View style={styles.metaContainer}>
            <View style={styles.metaItem}>
              <Clock size={16} color={Colors.neutral[600]} style={styles.metaIcon} />
              <Text style={styles.metaText}>{recipe.cooking_time} minutes</Text>
            </View>
            
            <View style={styles.metaDivider} />
            
            <View style={styles.metaItem}>
              <Users size={16} color={Colors.neutral[600]} style={styles.metaIcon} />
              <Text style={styles.metaText}>Serves {recipe.serving_size}</Text>
            </View>
          </View>
          
          <Text style={styles.description}>{recipe.description}</Text>
          
          {/* Ingredients */}
          <Text style={styles.sectionTitle}>Ingredients</Text>
          <View style={styles.ingredientsContainer}>
            {recipe.ingredients.map((ingredient, index) => (
              <View key={index} style={styles.ingredientRow}>
                <View style={styles.checkCircle}>
                  <Check size={12} color={Colors.primary[500]} />
                </View>
                <Text style={styles.ingredientText}>
                  <Text style={styles.ingredientName}>{ingredient.name}</Text>
                  {ingredient.quantity && ingredient.unit ? 
                    ` (${ingredient.quantity} ${ingredient.unit})` : ''}
                </Text>
              </View>
            ))}
          </View>
          
          {/* Instructions */}
          <Text style={styles.sectionTitle}>Instructions</Text>
          <View style={styles.instructionsContainer}>
            {recipe.instructions.split('\n').map((instruction, index) => (
              instruction.trim() && (
                <View key={index} style={styles.instructionRow}>
                  <View style={styles.instructionNumber}>
                    <Text style={styles.instructionNumberText}>{index + 1}</Text>
                  </View>
                  <Text style={styles.instructionText}>{instruction.trim()}</Text>
                </View>
              )
            ))}
          </View>
        </View>
      </ScrollView>
      
      <View style={styles.footer}>
        <Button
          title="Add Ingredients to Shopping List"
          leftIcon={<ShoppingCart size={20} color="white" />}
          fullWidth
          onPress={handleAddToShoppingList}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
  },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 16,
    zIndex: 10,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  favoriteButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  imageContainer: {
    height: 300,
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  imageGradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 80,
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  contentContainer: {
    flex: 1,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    backgroundColor: 'white',
    marginTop: -20,
    paddingTop: 24,
    paddingHorizontal: 24,
    paddingBottom: 100,
  },
  title: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 24,
    color: Colors.neutral[800],
    marginBottom: 12,
  },
  metaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaIcon: {
    marginRight: 4,
  },
  metaText: {
    fontFamily: 'Inter-Medium',
    fontSize: 14,
    color: Colors.neutral[600],
  },
  metaDivider: {
    height: 16,
    width: 1,
    backgroundColor: Colors.neutral[300],
    marginHorizontal: 12,
  },
  description: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[700],
    lineHeight: 24,
    marginBottom: 24,
  },
  sectionTitle: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 20,
    color: Colors.neutral[800],
    marginBottom: 16,
  },
  ingredientsContainer: {
    marginBottom: 24,
  },
  ingredientRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  checkCircle: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: Colors.primary[100],
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  ingredientText: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[700],
  },
  ingredientName: {
    fontFamily: 'Inter-Medium',
  },
  instructionsContainer: {
    marginBottom: 24,
  },
  instructionRow: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  instructionNumber: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: Colors.primary[500],
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    marginTop: 2,
  },
  instructionNumberText: {
    fontFamily: 'Inter-Bold',
    fontSize: 14,
    color: 'white',
  },
  instructionText: {
    flex: 1,
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[700],
    lineHeight: 24,
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: Colors.neutral[200],
    paddingHorizontal: 24,
    paddingVertical: 16,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
});