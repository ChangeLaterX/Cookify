import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Platform, KeyboardAvoidingView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { usePantry } from '@/context/PantryContext';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import Colors from '@/constants/Colors';
import { ArrowLeft, Calendar, Camera, Package } from 'lucide-react-native';
import { calculateExpirationDate, formatDate } from '@/utils/dates';

// Food categories with default shelf life
const FOOD_CATEGORIES = [
  { name: 'Fruits', shelfLife: 7 },
  { name: 'Vegetables', shelfLife: 7 },
  { name: 'Dairy', shelfLife: 14 },
  { name: 'Meat', shelfLife: 5 },
  { name: 'Grains', shelfLife: 90 },
  { name: 'Canned Goods', shelfLife: 730 }, // ~2 years
  { name: 'Baking', shelfLife: 180 }, // ~6 months
  { name: 'Condiments', shelfLife: 180 },
  { name: 'Snacks', shelfLife: 30 },
  { name: 'Beverages', shelfLife: 60 },
  { name: 'Frozen Foods', shelfLife: 90 },
  { name: 'Other', shelfLife: 30 },
];

export default function AddPantryItemScreen() {
  const { addItem } = usePantry();
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [unit, setUnit] = useState('');
  const [category, setCategory] = useState('');
  // const [purchaseDate, setPurchaseDate] = useState(formatDate(new Date()));
  const [expirationDate, setExpirationDate] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleCategorySelect = (selectedCategory: string) => {
    setCategory(selectedCategory);
    
    // Calculate expiration date based on category's shelf life
    const selectedCategoryInfo = FOOD_CATEGORIES.find(cat => cat.name === selectedCategory);
    if (selectedCategoryInfo) {
      const calculatedExpirationDate = calculateExpirationDate(
        new Date(), 
        selectedCategoryInfo.shelfLife
      );
      setExpirationDate(formatDate(calculatedExpirationDate));
    }
  };
  
  const handleAddItem = async () => {
    if (!name) {
      setError('Item name is required');
      return;
    }
    
    if (!category) {
      setError('Please select a category');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      await addItem({
        name,
        category,
        quantity: Number(quantity) || 1,
        unit,
        purchase_date: new Date().toISOString(),
        expiration_date: new Date(expirationDate).toISOString(),
        notes,
      });
      
      router.back();
    } catch (err: any) {
      setError(err.message || 'Failed to add item. Please try again.');
      console.error('Add item error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={100}
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ArrowLeft size={24} color={Colors.neutral[800]} />
          </TouchableOpacity>
          <Text style={styles.title}>Add Pantry Item</Text>
          <View style={{ width: 24 }} /> {/* For symmetry */}
        </View>
        
        <ScrollView 
          contentContainerStyle={styles.formContainer}
          showsVerticalScrollIndicator={false}
        >
          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}
          
          {/* Item Photo (Placeholder) */}
          <TouchableOpacity style={styles.photoContainer}>
            <View style={styles.photoPlaceholder}>
              <Camera size={36} color={Colors.neutral[400]} />
              <Text style={styles.photoText}>Add Photo</Text>
            </View>
          </TouchableOpacity>
          
          <Input
            label="Item Name"
            placeholder="Enter item name"
            value={name}
            onChangeText={setName}
            leftIcon={<Package size={20} color={Colors.neutral[500]} />}
          />
          
          <View style={styles.rowContainer}>
            <Input
              label="Quantity"
              placeholder="1"
              keyboardType="numeric"
              value={quantity}
              onChangeText={setQuantity}
              containerStyle={{ flex: 1, marginRight: 12 }}
            />
            
            <Input
              label="Unit"
              placeholder="pcs, kg, g"
              value={unit}
              onChangeText={setUnit}
              containerStyle={{ flex: 2 }}
            />
          </View>
          
          <Text style={styles.labelText}>Category</Text>
          <View style={styles.categoriesContainer}>
            {FOOD_CATEGORIES.map((cat) => (
              <TouchableOpacity
                key={cat.name}
                style={[
                  styles.categoryChip,
                  category === cat.name && styles.selectedCategoryChip
                ]}
                onPress={() => handleCategorySelect(cat.name)}
              >
                <Text
                  style={[
                    styles.categoryLabel,
                    category === cat.name && styles.selectedCategoryLabel
                  ]}
                >
                  {cat.name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <Input
            label="Expiration Date"
            placeholder="MM/DD/YYYY"
            value={expirationDate}
            onChangeText={setExpirationDate}
            leftIcon={<Calendar size={20} color={Colors.neutral[500]} />}
          />
          
          <Input
            label="Notes (Optional)"
            placeholder="Add any additional information"
            value={notes}
            onChangeText={setNotes}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
            inputStyle={{ height: 100, paddingTop: 12 }}
          />
          
          <Button
            title="Add Item"
            onPress={handleAddItem}
            loading={loading}
            fullWidth
            style={styles.addButton}
          />
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.neutral[200],
  },
  backButton: {
    padding: 4,
  },
  title: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 18,
    color: Colors.neutral[800],
  },
  formContainer: {
    padding: 24,
    paddingBottom: 40,
  },
  errorContainer: {
    backgroundColor: Colors.error.light,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    fontFamily: 'Inter-Regular',
    color: Colors.error.main,
  },
  photoContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  photoPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 12,
    backgroundColor: Colors.neutral[100],
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.neutral[300],
    borderStyle: 'dashed',
  },
  photoText: {
    fontFamily: 'Inter-Medium',
    color: Colors.neutral[600],
    marginTop: 8,
  },
  rowContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  labelText: {
    fontFamily: 'Inter-Medium',
    fontSize: 14,
    color: Colors.neutral[700],
    marginBottom: 8,
  },
  categoriesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16,
  },
  categoryChip: {
    backgroundColor: Colors.neutral[100],
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    margin: 4,
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
  addButton: {
    marginTop: 16,
  },
});