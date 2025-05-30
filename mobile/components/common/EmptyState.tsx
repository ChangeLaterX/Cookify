import React from 'react';
import { StyleSheet, View, Text } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { PackageOpen, UtensilsCrossed, ShoppingCart } from 'lucide-react-native';

interface EmptyStateProps {
  title: string;
  description: string;
  icon: 'package' | 'utensils' | 'shopping-cart';
}

export default function EmptyState({ title, description, icon }: EmptyStateProps) {
  const { colors } = useTheme();

  const renderIcon = () => {
    const iconSize = 64;
    const iconColor = colors.textSecondary;

    switch (icon) {
      case 'package':
        return <PackageOpen size={iconSize} color={iconColor} />;
      case 'utensils':
        return <UtensilsCrossed size={iconSize} color={iconColor} />;
      case 'shopping-cart':
        return <ShoppingCart size={iconSize} color={iconColor} />;
      default:
        return <PackageOpen size={iconSize} color={iconColor} />;
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.iconContainer}>{renderIcon()}</View>
      <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
      <Text style={[styles.description, { color: colors.textSecondary }]}>
        {description}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    marginTop: 48,
  },
  iconContainer: {
    marginBottom: 16,
    opacity: 0.6,
  },
  title: {
    fontSize: 18,
    fontFamily: 'Poppins-Bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  description: {
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
    textAlign: 'center',
    maxWidth: '80%',
  },
});