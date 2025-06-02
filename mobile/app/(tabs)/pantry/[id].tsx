import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, router } from 'expo-router';
import { usePantry } from '@/context/PantryContext';
import Button from '@/components/ui/Button';
import Colors from '@/constants/Colors';
import { ArrowLeft, Edit, Trash2, Calendar, ShoppingBag, Info } from 'lucide-react-native';
import { formatDate, getExpirationDescription } from '@/utils/dates';

export default function PantryItemDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { items, deleteItem } = usePantry();
  const [item, setItem] = useState(items.find(i => i.id === id));
  
  useEffect(() => {
    const foundItem = items.find(i => i.id === id);
    setItem(foundItem);
    
    if (!foundItem) {
      // Item not found, navigate back
      Alert.alert('Error', 'Item not found');
      router.back();
    }
  }, [id, items]);
  
  const handleDelete = () => {
    Alert.alert(
      'Delete Item',
      `Are you sure you want to delete ${item?.name}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: async () => {
            if (id) {
              await deleteItem(id);
              router.back();
            }
          }
        }
      ]
    );
  };
  
  if (!item) {
    return null;
  }
  
  // Determine expiration status
  const expirationDate = new Date(item.expiration_date);
  const currentDate = new Date();
  const isExpired = expirationDate < currentDate;
  const expiresWithinThreeDays = 
    expirationDate >= currentDate && 
    expirationDate <= new Date(currentDate.setDate(currentDate.getDate() + 3));
  
  const getExpirationStatusColor = () => {
    if (isExpired) return Colors.expiration.expired;
    if (expiresWithinThreeDays) return Colors.expiration.soon;
    return Colors.expiration.fresh;
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <ArrowLeft size={24} color={Colors.neutral[800]} />
        </TouchableOpacity>
        <Text style={styles.title}>Item Details</Text>
        <TouchableOpacity onPress={handleDelete} style={styles.deleteButton}>
          <Trash2 size={22} color={Colors.error.main} />
        </TouchableOpacity>
      </View>
      
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.content}>
          {/* Item Image */}
          <View style={styles.imageContainer}>
            {item.image_url ? (
              <Image source={{ uri: item.image_url }} style={styles.image} />
            ) : (
              <View style={styles.imagePlaceholder}>
                <Text style={styles.imagePlaceholderText}>{item.name.charAt(0).toUpperCase()}</Text>
              </View>
            )}
          </View>
          
          {/* Item Info */}
          <View style={styles.infoCard}>
            <View style={styles.nameRow}>
              <Text style={styles.itemName}>{item.name}</Text>
              <TouchableOpacity 
                style={styles.editButton}
                onPress={() => router.push(`/pantry/edit/${item.id}`)}
              >
                <Edit size={18} color={Colors.primary[500]} />
              </TouchableOpacity>
            </View>
            
            <View style={styles.detailRow}>
              <ShoppingBag size={18} color={Colors.neutral[600]} style={styles.icon} />
              <Text style={styles.detailLabel}>Quantity:</Text>
              <Text style={styles.detailValue}>
                {item.quantity} {item.unit}
              </Text>
            </View>
            
            <View style={styles.detailRow}>
              <Calendar size={18} color={Colors.neutral[600]} style={styles.icon} />
              <Text style={styles.detailLabel}>Purchased:</Text>
              <Text style={styles.detailValue}>{formatDate(item.purchase_date)}</Text>
            </View>
            
            <View style={styles.detailRow}>
              <Calendar size={18} color={getExpirationStatusColor()} style={styles.icon} />
              <Text style={styles.detailLabel}>Expires:</Text>
              <Text style={[styles.detailValue, { color: getExpirationStatusColor() }]}>
                {formatDate(item.expiration_date)}
              </Text>
            </View>
            
            <View style={[styles.expirationBanner, { backgroundColor: getExpirationStatusColor() + '20' }]}>
              <Text style={[styles.expirationText, { color: getExpirationStatusColor() }]}>
                {getExpirationDescription(item.expiration_date)}
              </Text>
            </View>
            
            <View style={styles.categoryContainer}>
              <Text style={styles.categoryLabel}>{item.category}</Text>
            </View>
            
            {item.notes && (
              <View style={styles.notesContainer}>
                <View style={styles.notesHeader}>
                  <Info size={18} color={Colors.neutral[600]} />
                  <Text style={styles.notesTitle}>Notes</Text>
                </View>
                <Text style={styles.notesText}>{item.notes}</Text>
              </View>
            )}
          </View>
          
          {/* Action Buttons */}
          <View style={styles.actionsContainer}>
            <Button
              title="Edit Item"
              variant="outline"
              leftIcon={<Edit size={20} color={Colors.primary[500]} />}
              onPress={() => router.push(`/pantry/edit/${item.id}`)}
              style={styles.actionButton}
            />
            
            <Button
              title="Delete Item"
              variant="outline"
              leftIcon={<Trash2 size={20} color={Colors.error.main} />}
              onPress={handleDelete}
              style={[styles.actionButton, styles.deleteActionButton]}
              textStyle={{ color: Colors.error.main }}
            />
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.neutral[200],
  },
  backButton: {
    padding: 4,
  },
  title: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 18,
    color: Colors.neutral[800],
  },
  deleteButton: {
    padding: 4,
  },
  content: {
    padding: 24,
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  image: {
    width: 150,
    height: 150,
    borderRadius: 12,
  },
  imagePlaceholder: {
    width: 150,
    height: 150,
    borderRadius: 12,
    backgroundColor: Colors.neutral[200],
    justifyContent: 'center',
    alignItems: 'center',
  },
  imagePlaceholderText: {
    fontFamily: 'Poppins-Bold',
    fontSize: 64,
    color: Colors.neutral[500],
  },
  infoCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  nameRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  itemName: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 24,
    color: Colors.neutral[800],
  },
  editButton: {
    padding: 8,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  icon: {
    marginRight: 8,
  },
  detailLabel: {
    fontFamily: 'Inter-SemiBold',
    fontSize: 14,
    color: Colors.neutral[700],
    width: 90,
  },
  detailValue: {
    fontFamily: 'Inter-Regular',
    fontSize: 14,
    color: Colors.neutral[800],
    flex: 1,
  },
  expirationBanner: {
    padding: 12,
    borderRadius: 8,
    marginVertical: 12,
  },
  expirationText: {
    fontFamily: 'Inter-SemiBold',
    fontSize: 14,
    textAlign: 'center',
  },
  categoryContainer: {
    backgroundColor: Colors.primary[100],
    alignSelf: 'flex-start',
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 16,
    marginTop: 8,
  },
  categoryLabel: {
    fontFamily: 'Inter-Medium',
    color: Colors.primary[700],
    fontSize: 12,
  },
  notesContainer: {
    marginTop: 16,
    padding: 12,
    backgroundColor: Colors.neutral[100],
    borderRadius: 8,
  },
  notesHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  notesTitle: {
    fontFamily: 'Inter-SemiBold',
    fontSize: 14,
    color: Colors.neutral[700],
    marginLeft: 8,
  },
  notesText: {
    fontFamily: 'Inter-Regular',
    fontSize: 14,
    color: Colors.neutral[700],
    lineHeight: 20,
  },
  actionsContainer: {
    marginTop: 16,
  },
  actionButton: {
    marginBottom: 12,
    borderWidth: 1,
    borderColor: Colors.primary[500],
  },
  deleteActionButton: {
    borderColor: Colors.error.main,
  },
});