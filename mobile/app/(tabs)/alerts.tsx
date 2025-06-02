import React, { useEffect } from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { usePantry } from '@/context/PantryContext';
import Colors from '@/constants/Colors';
import ExpirationAlert from '@/components/ExpirationAlert';
import EmptyState from '@/components/EmptyState';
import { AlertCircle } from 'lucide-react-native';
import { differenceInDays } from '@/utils/dates';

export default function AlertsScreen() {
  const { items, loading, fetchItems } = usePantry();
  
  useEffect(() => {
    fetchItems();
  }, []);
  
  // Filter items to get expired and expiring soon items
  const expiringItems = items.filter(item => {
    const daysUntilExpiry = differenceInDays(new Date(), new Date(item.expiration_date));
    return daysUntilExpiry <= 5; // Show items expiring within 5 days or already expired
  });
  
  // Sort by expiration date (expired first, then soon to expire)
  const sortedItems = expiringItems.sort((a, b) => {
    return new Date(a.expiration_date).getTime() - new Date(b.expiration_date).getTime();
  });
  
  // Group by expiration status
  const expiredItems = sortedItems.filter(item => 
    differenceInDays(new Date(), new Date(item.expiration_date)) < 0
  );
  
  const expiringSoonItems = sortedItems.filter(item => {
    const days = differenceInDays(new Date(), new Date(item.expiration_date));
    return days >= 0 && days <= 5;
  });

  const renderSectionHeader = (title: string) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Expiration Alerts</Text>
      </View>
      
      {loading ? (
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Checking expiration dates...</Text>
        </View>
      ) : sortedItems.length > 0 ? (
        <FlatList
          data={[
            ...expiredItems.map(item => ({ ...item, section: 'expired' })),
            ...expiringSoonItems.map(item => ({ ...item, section: 'expiring' }))
          ]}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          renderItem={({ item, index }) => {
            const isFirstExpired = item.section === 'expired' && index === 0;
            const isFirstExpiring = item.section === 'expiring' && index === expiredItems.length;
            
            return (
              <View>
                {isFirstExpired && renderSectionHeader('Expired Items')}
                {isFirstExpiring && renderSectionHeader('Expiring Soon')}
                <ExpirationAlert 
                  item={item} 
                  onPress={(item) => router.push(`/(tabs)/pantry/${item.id}`)}
                />
              </View>
            );
          }}
        />
      ) : (
        <EmptyState
          icon={<AlertCircle size={64} color={Colors.success.main} />}
          title="No Expiring Items"
          message="All your pantry items are fresh! You'll get alerts here when items are about to expire."
          actionLabel="View Pantry"
          onAction={() => router.push('/(tabs)/pantry')}
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
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 16,
  },
  title: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 28,
    color: Colors.neutral[800],
  },
  sectionHeader: {
    backgroundColor: Colors.neutral[100],
    paddingVertical: 8,
    paddingHorizontal: 24,
    marginBottom: 12,
  },
  sectionTitle: {
    fontFamily: 'Inter-SemiBold',
    fontSize: 16,
    color: Colors.neutral[700],
  },
  listContent: {
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
  },
});