import React from 'react';
import { StyleSheet, ScrollView } from 'react-native';
import { PantryCategory } from 'shared';
import FilterChip from '@/components/common/FilterChip';

interface CategoryFilterProps {
  selectedCategory: PantryCategory | 'all';
  onSelectCategory: (category: PantryCategory | 'all') => void;
}

export default function CategoryFilter({ selectedCategory, onSelectCategory }: CategoryFilterProps) {
  const categories: (PantryCategory | 'all')[] = [
    'all',
    'produce',
    'dairy',
    'meat',
    'seafood',
    'frozen',
    'canned',
    'dry goods',
    'snacks',
    'beverages',
    'condiments',
    'spices',
    'baking',
    'other',
  ];

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {categories.map((category) => (
        <FilterChip
          key={category}
          label={
            category === 'all'
              ? 'All'
              : category.charAt(0).toUpperCase() + category.slice(1)
          }
          selected={selectedCategory === category}
          onPress={() => onSelectCategory(category)}
        />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
});