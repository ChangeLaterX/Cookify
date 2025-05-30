import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { PantryItem } from 'shared';
import { getExpirationStatus, formatRelativeTime } from 'shared';
import { useRouter } from 'expo-router';
import { ChevronRight } from 'lucide-react-native';

interface PantryItemCardProps {
  item: PantryItem;
}

export default function PantryItemCard({ item }: PantryItemCardProps) {
  const { colors } = useTheme();
  const router = useRouter();
  
  const expirationStatus = getExpirationStatus(item.expirationDate);
  
  const getStatusColor = () => {
    switch (expirationStatus) {
      case 'expired':
        return colors.error;
      case 'expiring-soon':
        return colors.warning;
      case 'good':
        return colors.success;
      default:
        return colors.textSecondary;
    }
  };
  
  const getStatusText = () => {
    switch (expirationStatus) {
      case 'expired':
        return 'Expired';
      case 'expiring-soon':
        return 'Expiring Soon';
      case 'good':
        return 'Good';
      default:
        return 'No expiration';
    }
  };
  
  const handlePress = () => {
    router.push(`/pantry/${item.id}`);
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
        <View style={styles.mainInfo}>
          <Text style={[styles.name, { color: colors.text }]}>{item.name}</Text>
          <Text style={[styles.category, { color: colors.textSecondary }]}>
            {item.category.charAt(0).toUpperCase() + item.category.slice(1)}
          </Text>
        </View>
        
        <View style={styles.details}>
          <View style={styles.quantityContainer}>
            <Text style={[styles.quantity, { color: colors.text }]}>
              {item.quantity} {item.unit}
            </Text>
          </View>
          
          <View style={styles.statusContainer}>
            <Text
              style={[
                styles.statusIndicator,
                { backgroundColor: getStatusColor() },
              ]}
            />
            <Text style={[styles.statusText, { color: getStatusColor() }]}>
              {getStatusText()}
            </Text>
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
  mainInfo: {
    marginBottom: 8,
  },
  name: {
    fontSize: 16,
    fontFamily: 'Poppins-Medium',
    marginBottom: 2,
  },
  category: {
    fontSize: 12,
    fontFamily: 'Poppins-Regular',
  },
  details: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  quantityContainer: {},
  quantity: {
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    fontFamily: 'Poppins-Medium',
  },
  rightContent: {
    marginLeft: 8,
  },
});