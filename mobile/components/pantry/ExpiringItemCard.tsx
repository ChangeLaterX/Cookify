import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { PantryItem } from 'shared';
import { getDaysUntilExpiration } from 'shared';
import { useRouter } from 'expo-router';

interface ExpiringItemCardProps {
  item: PantryItem;
}

export default function ExpiringItemCard({ item }: ExpiringItemCardProps) {
  const { colors } = useTheme();
  const router = useRouter();
  
  const daysUntilExpiration = getDaysUntilExpiration(item.expirationDate);
  
  const handlePress = () => {
    router.push(`/pantry/${item.id}`);
  };

  return (
    <TouchableOpacity
      style={[
        styles.card,
        {
          backgroundColor: colors.warningLight,
          borderColor: colors.warning,
        },
      ]}
      onPress={handlePress}
    >
      <View style={styles.content}>
        <Text style={[styles.name, { color: colors.text }]}>{item.name}</Text>
        <Text style={[styles.quantity, { color: colors.textSecondary }]}>
          {item.quantity} {item.unit}
        </Text>
      </View>
      
      <View style={styles.expirationContainer}>
        <Text
          style={[
            styles.expirationText,
            { color: colors.warning },
          ]}
        >
          {daysUntilExpiration === 0
            ? 'Expires today'
            : daysUntilExpiration === 1
            ? 'Expires tomorrow'
            : `Expires in ${daysUntilExpiration} days`}
        </Text>
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
  },
  content: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontFamily: 'Poppins-Medium',
    marginBottom: 4,
  },
  quantity: {
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
  },
  expirationContainer: {
    paddingLeft: 12,
  },
  expirationText: {
    fontSize: 14,
    fontFamily: 'Poppins-Medium',
  },
});