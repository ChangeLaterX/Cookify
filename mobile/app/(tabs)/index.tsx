import React, { useEffect, useState } from 'react';
import { StyleSheet, View, Text, ScrollView, TouchableOpacity, RefreshControl } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { usePantry } from '@/contexts/PantryContext';
import { getExpirationStatus } from '../../../shared/src/utils/dateUtils';
import { Bell, ShoppingCart, UtensilsCrossed } from 'lucide-react-native';
import { PantryItem } from '../../../shared/src/types/pantry';
import { Link } from 'expo-router';
import ExpiringItemCard from '@/components/pantry/ExpiringItemCard';
import DashboardCard from '@/components/dashboard/DashboardCard';

export default function DashboardScreen() {
  const { colors } = useTheme();
  const { pantryItems, fetchPantryItems, loading } = usePantry();
  const [refreshing, setRefreshing] = useState(false);

  // Get expiring items (expiring within 3 days)
  const expiringItems = pantryItems.filter(
    item => getExpirationStatus(item.expirationDate) === 'expiring-soon'
  );

  // Get expired items
  const expiredItems = pantryItems.filter(
    item => getExpirationStatus(item.expirationDate) === 'expired'
  );

  // Get low stock items (quantity <= 1)
  const lowStockItems = pantryItems.filter(item => item.quantity <= 1);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchPantryItems();
    setRefreshing(false);
  };

  const dynamicStyles = StyleSheet.create({
    container: {
      backgroundColor: colors.background,
    },
    welcomeText: {
      color: colors.text,
    },
    subtitleText: {
      color: colors.textSecondary,
    },
    sectionTitle: {
      color: colors.text,
    },
    card: {
      backgroundColor: colors.card,
      borderColor: colors.border,
    },
    cardTitle: {
      color: colors.text,
    },
    cardSubtitle: {
      color: colors.textSecondary,
    },
    warningText: {
      color: colors.warning,
    },
    dangerText: {
      color: colors.error,
    },
    actionButton: {
      backgroundColor: colors.primary,
    },
    actionButtonText: {
      color: colors.white,
    },
  });

  return (
    <ScrollView 
      style={[styles.container, dynamicStyles.container]}
      contentContainerStyle={styles.contentContainer}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.welcomeSection}>
        <Text style={[styles.welcomeText, dynamicStyles.welcomeText]}>Hello!</Text>
        <Text style={[styles.subtitle, dynamicStyles.subtitleText]}>
          Here's what's happening in your pantry
        </Text>
      </View>

      <View style={styles.alertsSection}>
        <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>Alerts</Text>
        
        <View style={styles.cardGrid}>
          <DashboardCard
            title="Expiring Soon"
            count={expiringItems.length}
            icon={<Bell size={24} color={colors.warning} />}
            color={colors.warningLight}
            route="/pantry?filter=expiring"
          />
          
          <DashboardCard
            title="Expired Items"
            count={expiredItems.length}
            icon={<Bell size={24} color={colors.error} />}
            color={colors.errorLight}
            route="/pantry?filter=expired"
          />
          
          <DashboardCard
            title="Low Stock"
            count={lowStockItems.length}
            icon={<ShoppingCart size={24} color={colors.primary} />}
            color={colors.primaryLight}
            route="/pantry?filter=low-stock"
          />
          
          <DashboardCard
            title="Recipe Ideas"
            subtitle="Based on your pantry"
            icon={<UtensilsCrossed size={24} color={colors.secondary} />}
            color={colors.secondaryLight}
            route="/recipes"
          />
        </View>
      </View>

      {expiringItems.length > 0 && (
        <View style={styles.expiringSection}>
          <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>
            Expiring Soon
          </Text>
          
          <View style={styles.expiringList}>
            {expiringItems.slice(0, 3).map(item => (
              <ExpiringItemCard key={item.id} item={item} />
            ))}
            
            {expiringItems.length > 3 && (
              <Link href="/pantry?filter=expiring\" asChild>
                <TouchableOpacity style={[styles.viewAllButton, dynamicStyles.actionButton]}>
                  <Text style={[styles.viewAllButtonText, dynamicStyles.actionButtonText]}>
                    View All ({expiringItems.length})
                  </Text>
                </TouchableOpacity>
              </Link>
            )}
          </View>
        </View>
      )}

      <View style={styles.actionsSection}>
        <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>
          Quick Actions
        </Text>
        
        <View style={styles.actionButtons}>
          <Link href="/pantry/add" asChild>
            <TouchableOpacity style={[styles.actionButton, dynamicStyles.actionButton]}>
              <Text style={[styles.actionButtonText, dynamicStyles.actionButtonText]}>
                Add Pantry Item
              </Text>
            </TouchableOpacity>
          </Link>
          
          <Link href="/shopping/create" asChild>
            <TouchableOpacity style={[styles.actionButton, dynamicStyles.actionButton]}>
              <Text style={[styles.actionButtonText, dynamicStyles.actionButtonText]}>
                Create Shopping List
              </Text>
            </TouchableOpacity>
          </Link>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    paddingHorizontal: 16,
    paddingBottom: 32,
  },
  welcomeSection: {
    marginTop: 16,
    marginBottom: 24,
  },
  welcomeText: {
    fontSize: 28,
    fontFamily: 'Poppins-Bold',
  },
  subtitle: {
    fontSize: 16,
    fontFamily: 'Poppins-Regular',
    marginTop: 4,
  },
  alertsSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontFamily: 'Poppins-Bold',
    marginBottom: 12,
  },
  cardGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  expiringSection: {
    marginBottom: 24,
  },
  expiringList: {
    gap: 12,
  },
  viewAllButton: {
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  viewAllButtonText: {
    fontFamily: 'Poppins-Medium',
    fontSize: 14,
  },
  actionsSection: {
    marginBottom: 16,
  },
  actionButtons: {
    gap: 12,
  },
  actionButton: {
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionButtonText: {
    fontFamily: 'Poppins-Bold',
    fontSize: 16,
  },
});