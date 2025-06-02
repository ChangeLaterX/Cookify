import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { ShoppingListItem as ShoppingListItemType } from '@/types/supabase';
import Colors from '@/constants/Colors';
import { CheckCircle2, Circle, Trash2 } from 'lucide-react-native';

interface ShoppingListItemProps {
  item: ShoppingListItemType;
  onToggle: (id: string, isCompleted: boolean) => void;
  onDelete: (id: string) => void;
}

const ShoppingListItem: React.FC<ShoppingListItemProps> = ({ 
  item, 
  onToggle,
  onDelete 
}) => {
  return (
    <View style={styles.container}>
      <Pressable 
        style={styles.checkbox} 
        onPress={() => onToggle(item.id, !item.is_completed)}
      >
        {item.is_completed ? (
          <CheckCircle2 size={24} color={Colors.primary[500]} />
        ) : (
          <Circle size={24} color={Colors.neutral[400]} />
        )}
      </Pressable>
      
      <View style={styles.contentContainer}>
        <Text 
          style={[
            styles.name,
            item.is_completed && styles.completedText
          ]}
        >
          {item.name}
        </Text>
        
        {(item.quantity > 0 || item.unit) && (
          <Text style={styles.quantity}>
            {item.quantity} {item.unit || ''}
          </Text>
        )}
        
        {item.category && (
          <View style={styles.categoryContainer}>
            <Text style={styles.category}>{item.category}</Text>
          </View>
        )}
      </View>
      
      <Pressable style={styles.deleteButton} onPress={() => onDelete(item.id)}>
        <Trash2 size={20} color={Colors.error.main} />
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  checkbox: {
    marginRight: 12,
  },
  contentContainer: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: '500',
    color: Colors.neutral[800],
    marginBottom: 2,
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: Colors.neutral[400],
  },
  quantity: {
    fontSize: 14,
    color: Colors.neutral[600],
    marginBottom: 4,
  },
  categoryContainer: {
    backgroundColor: Colors.primary[100],
    alignSelf: 'flex-start',
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: 4,
  },
  category: {
    fontSize: 12,
    color: Colors.primary[700],
  },
  deleteButton: {
    padding: 8,
  },
});

export default ShoppingListItem;