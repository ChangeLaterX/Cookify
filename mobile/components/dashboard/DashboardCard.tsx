import React, { ReactNode } from 'react';
import { StyleSheet, View, Text, TouchableOpacity } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Link } from 'expo-router';

interface DashboardCardProps {
  title: string;
  subtitle?: string;
  count?: number;
  icon: ReactNode;
  color: string;
  route: string;
}

export default function DashboardCard({
  title,
  subtitle,
  count,
  icon,
  color,
  route,
}: DashboardCardProps) {
  const { colors } = useTheme();

  return (
    <Link href={route} asChild>
      <TouchableOpacity
        style={[
          styles.card,
          {
            backgroundColor: colors.card,
            borderColor: colors.border,
          },
        ]}
      >
        <View style={[styles.iconContainer, { backgroundColor: color }]}>
          {icon}
        </View>
        
        <View style={styles.content}>
          <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
          
          {subtitle ? (
            <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
              {subtitle}
            </Text>
          ) : count !== undefined ? (
            <Text style={[styles.count, { color: colors.textSecondary }]}>
              {count}
            </Text>
          ) : null}
        </View>
      </TouchableOpacity>
    </Link>
  );
}

const styles = StyleSheet.create({
  card: {
    width: '48%',
    borderRadius: 12,
    borderWidth: 1,
    padding: 16,
    marginBottom: 16,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  content: {},
  title: {
    fontSize: 16,
    fontFamily: 'Poppins-Medium',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 12,
    fontFamily: 'Poppins-Regular',
  },
  count: {
    fontSize: 20,
    fontFamily: 'Poppins-Bold',
  },
});