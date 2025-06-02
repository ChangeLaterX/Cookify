import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useShoppingList } from '@/context/ShoppingListContext';
import Colors from '@/constants/Colors';
import ShoppingListItem from '@/components/ShoppingListItem';
import EmptyState from '@/components/EmptyState';
import { Plus, CheckSquare, ShoppingCart, Trash2 } from 'lucide-react-native';

export default function ShoppingListScreen() {
  const { items, fetchItems, addItem, toggleItemCompletion, deleteItem, clearCompletedItems } = useShoppingList();
  
  const [newItemName, setNewItemName] = useState('');
  const [newItemQuantity, setNewItemQuantity] = useState('1');
  
  useEffect(() => {
    fetchItems();
  }, []);
  
  const handleAddItem = async () => {
    if (!newItemName.trim()) {
      return;
    }
    
    await addItem({
      name: newItemName.trim(),
      quantity: parseInt(newItemQuantity) || 1,
      is_completed: false,
    });
    
    setNewItemName('');
    setNewItemQuantity('1');
  };
  
  const handleClearCompleted = () => {
    if (items.some(item => item.is_completed)) {
      Alert.alert(
        'Clear Completed Items',
        'Are you sure you want to remove all completed items?',
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Clear', 
            style: 'destructive',
            onPress: clearCompletedItems
          }
        ]
      );
    }
  };
  
  // Count completed and remaining items
  const completedCount = items.filter(item => item.is_completed).length;
  const remainingCount = items.length - completedCount;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Shopping List</Text>
        
        {items.length > 0 && items.some(item => item.is_completed) && (
          <TouchableOpacity 
            style={styles.clearButton}
            onPress={handleClearCompleted}
          >
            <Trash2 size={20} color={Colors.error.main} />
          </TouchableOpacity>
        )}
      </View>
      
      <View style={styles.addContainer}>
        <View style={styles.inputsContainer}>
          <TextInput
            style={styles.nameInput}
            placeholder="Add an item..."
            value={newItemName}
            onChangeText={setNewItemName}
            placeholderTextColor={Colors.neutral[400]}
            returnKeyType="done"
            onSubmitEditing={handleAddItem}
          />
          
          <View style={styles.quantityInputContainer}>
            <TextInput
              style={styles.quantityInput}
              placeholder="1"
              keyboardType="numeric"
              value={newItemQuantity}
              onChangeText={setNewItemQuantity}
              placeholderTextColor={Colors.neutral[400]}
            />
          </View>
        </View>
        
        <TouchableOpacity 
          style={[
            styles.addButton,
            !newItemName.trim() && styles.addButtonDisabled
          ]}
          onPress={handleAddItem}
          disabled={!newItemName.trim()}
        >
          <Plus size={24} color="white" />
        </TouchableOpacity>
      </View>
      
      {items.length > 0 && (
        <View style={styles.countsContainer}>
          <View style={styles.countItem}>
            <Text style={styles.countNumber}>{remainingCount}</Text>
            <Text style={styles.countLabel}>remaining</Text>
          </View>
          
          <View style={styles.countDivider} />
          
          <View style={styles.countItem}>
            <Text style={styles.countNumber}>{completedCount}</Text>
            <Text style={styles.countLabel}>completed</Text>
          </View>
        </View>
      )}
      
      {items.length > 0 ? (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <ShoppingListItem 
              item={item} 
              onToggle={toggleItemCompletion} 
              onDelete={deleteItem}
            />
          )}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      ) : (
        <EmptyState
          icon={<ShoppingCart size={64} color={Colors.neutral[400]} />}
          title="Your shopping list is empty"
          message="Add items to your shopping list to make sure you don't forget anything on your next grocery trip."
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
  clearButton: {
    padding: 8,
  },
  addContainer: {
    flexDirection: 'row',
    paddingHorizontal: 24,
    paddingBottom: 16,
    alignItems: 'center',
  },
  inputsContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 50,
    borderWidth: 1,
    borderColor: Colors.neutral[200],
    marginRight: 12,
  },
  nameInput: {
    flex: 3,
    height: '100%',
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[800],
  },
  quantityInputContainer: {
    flex: 1,
    borderLeftWidth: 1,
    borderLeftColor: Colors.neutral[200],
    paddingLeft: 12,
    height: '100%',
    justifyContent: 'center',
  },
  quantityInput: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[800],
    width: '100%',
    textAlign: 'center',
  },
  addButton: {
    backgroundColor: Colors.primary[500],
    width: 50,
    height: 50,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
  },
  addButtonDisabled: {
    backgroundColor: Colors.neutral[400],
  },
  countsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.neutral[100],
    paddingVertical: 10,
    marginHorizontal: 24,
    borderRadius: 12,
    marginBottom: 16,
  },
  countItem: {
    flex: 1,
    alignItems: 'center',
  },
  countNumber: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 18,
    color: Colors.primary[600],
  },
  countLabel: {
    fontFamily: 'Inter-Regular',
    fontSize: 14,
    color: Colors.neutral[600],
  },
  countDivider: {
    height: 30,
    width: 1,
    backgroundColor: Colors.neutral[300],
  },
  listContent: {
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
});