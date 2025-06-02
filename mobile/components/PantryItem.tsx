import React from 'react';
import { View, Text, StyleSheet, Image, Pressable } from 'react-native';
import { PantryItem as PantryItemType } from '@/types/supabase';
import { differenceInDays } from '@/utils/dates';
import Colors from '@/constants/Colors';
import { Calendar, Clock } from 'lucide-react-native';

interface PantryItemProps {
  item: PantryItemType;
  onPress: (item: PantryItemType) => void;
}

export const PantryItemCard: React.FC<PantryItemProps> = ({ item, onPress }) => {
  const daysUntilExpiry = differenceInDays(new Date(), new Date(item.expiration_date));
  
  const getExpirationColor = () => {
    if (daysUntilExpiry < 0) {
      return Colors.expiration.expired; // Expired
    } else if (daysUntilExpiry <= 3) {
      return Colors.expiration.soon; // Expiring soon
    } else {
      return Colors.expiration.fresh; // Fresh
    }
  };
  
  const getExpirationText = () => {
    if (daysUntilExpiry < 0) {
      return `Expired ${Math.abs(daysUntilExpiry)} days ago`;
    } else if (daysUntilExpiry === 0) {
      return 'Expires today';
    } else if (daysUntilExpiry === 1) {
      return 'Expires tomorrow';
    } else {
      return `Expires in ${daysUntilExpiry} days`;
    }
  };

  return (
    <Pressable 
      style={[styles.container, { borderLeftColor: getExpirationColor() }]}
      onPress={() => onPress(item)}
    >
      <View style={styles.imageContainer}>
        {item.image_url ? (
          <Image source={{ uri: item.image_url }} style={styles.image} />
        ) : (
          <View style={[styles.placeholderImage, { backgroundColor: Colors.neutral[200] }]}>
            <Text style={styles.placeholderText}>{item.name.charAt(0).toUpperCase()}</Text>
          </View>
        )}
      </View>
      
      <View style={styles.contentContainer}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.quantity}>
          {item.quantity} {item.unit}
        </Text>
        
        <View style={styles.expirationContainer}>
          <Calendar size={16} color={getExpirationColor()} style={styles.icon} />
          <Text style={[styles.expirationText, { color: getExpirationColor() }]}>
            {getExpirationText()}
          </Text>
        </View>
      </View>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    marginBottom: 12,
    borderLeftWidth: 4,
    overflow: 'hidden',
  },
  imageContainer: {
    width: 80,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  placeholderImage: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.neutral[500],
  },
  contentContainer: {
    flex: 1,
    padding: 12,
    justifyContent: 'space-between',
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.neutral[800],
    marginBottom: 2,
  },
  quantity: {
    fontSize: 14,
    color: Colors.neutral[600],
    marginBottom: 4,
  },
  expirationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    marginRight: 4,
  },
  expirationText: {
    fontSize: 12,
    fontWeight: '500',
  },
});

export default PantryItemCard;