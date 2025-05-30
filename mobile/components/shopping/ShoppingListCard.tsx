import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { ShoppingList } from 'shared';
import { formatRelativeTime } from 'shared';
import { useRouter } from 'expo-router';
import { ChevronRight, ShoppingBag } from 'lucide-react-native';

interface ShoppingListCardProps {
  shoppingList: ShoppingList;
}

export default function ShoppingListCard({ shoppingList }: ShoppingListCardProps) {
  const { colors } = useTheme();
  const router = useRouter();
  
  const checkedCount = shoppingList.items.filter(item => item.isChecked).length;
  const totalCount = shoppingList.items.length;
  const progress = totalCount > 0 ? (checkedCount / totalCount) * 100 : 0;
  
  const handlePress = () => {
    router.push(`/shopping/${shoppingList.id}`);
  };

  return (
    <TouchableOpacity
      style={[
        styles.card,
        { backgroundColor: colors.card, borderColor: colors.border },
      ]}
      onPress={handlePress}
    >
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={[styles.title, { color: colors.text }]}>{shoppingList.name}</Text>
          <Text style={[styles.date, { color: colors.textSecondary }]}>
            {formatRelativeTime(shoppingList.createdAt)}
          </Text>
        </View>
        
        <View style={styles.details}>
          <View style={styles.iconContainer}>
            <ShoppingBag size={24} color={colors.primary} />
          </View>
          
          <View style={styles.infoContainer}>
            <Text style={[styles.itemCount, { color: colors.text }]}>
              {checkedCount} of {totalCount} items
            </Text>
            
            <View style={[styles.progressBar, { backgroundColor: colors.border }]}>
              <View
                style={[
                  styles.progressFill,
                  {
                    backgroundColor: colors.primary,
                    width: `${progress}%`,
                  },
                ]}
              />
            </View>
          </View>
        </View>
      </View>
      
      <View style={styles.rightContent}>
        <ChevronRight size={20} color={colors.textSecondary} />
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderRadius: 12,
    borderWidth: 1,
    padding: 16,
    marginBottom: 12,
  },
  content: {
    flex: 1,
  },
  header: {
    marginBottom: 12,
  },
  title: {
    fontSize: 18,
    fontFamily: 'Poppins-Bold',
    marginBottom: 4,
  },
  date: {
    fontSize: 12,
    fontFamily: 'Poppins-Regular',
  },
  details: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    marginRight: 12,
  },
  infoContainer: {
    flex: 1,
  },
  itemCount: {
    fontSize: 14,
    fontFamily: 'Poppins-Medium',
    marginBottom: 8,
  },
  progressBar: {
    height: 6,
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
  },
  rightContent: {
    marginLeft: 8,
  },
});