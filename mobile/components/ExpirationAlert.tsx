import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { PantryItem } from '@/types/supabase';
import Colors from '@/constants/Colors';
import { AlertTriangle, Calendar } from 'lucide-react-native';
import { differenceInDays } from '@/utils/dates';

interface ExpirationAlertProps {
  item: PantryItem;
  onPress: (item: PantryItem) => void;
}

const ExpirationAlert: React.FC<ExpirationAlertProps> = ({ item, onPress }) => {
  const daysUntilExpiry = differenceInDays(new Date(), new Date(item.expiration_date));
  
  const getAlertStyle = () => {
    if (daysUntilExpiry < 0) {
      return {
        backgroundColor: Colors.error.light,
        iconColor: Colors.error.dark,
        textColor: Colors.error.dark,
      };
    } else if (daysUntilExpiry <= 1) {
      return {
        backgroundColor: Colors.warning.light,
        iconColor: Colors.warning.dark,
        textColor: Colors.warning.dark,
      };
    } else {
      return {
        backgroundColor: Colors.neutral[200],
        iconColor: Colors.neutral[600],
        textColor: Colors.neutral[700],
      };
    }
  };
  
  const alertStyle = getAlertStyle();
  
  const getAlertText = () => {
    if (daysUntilExpiry < 0) {
      return `EXPIRED: ${item.name} expired ${Math.abs(daysUntilExpiry)} days ago`;
    } else if (daysUntilExpiry === 0) {
      return `URGENT: ${item.name} expires today`;
    } else if (daysUntilExpiry === 1) {
      return `ATTENTION: ${item.name} expires tomorrow`;
    } else {
      return `REMINDER: ${item.name} expires in ${daysUntilExpiry} days`;
    }
  };

  return (
    <Pressable 
      style={[styles.container, { backgroundColor: alertStyle.backgroundColor }]}
      onPress={() => onPress(item)}
    >
      {daysUntilExpiry <= 0 ? (
        <AlertTriangle size={20} color={alertStyle.iconColor} style={styles.icon} />
      ) : (
        <Calendar size={20} color={alertStyle.iconColor} style={styles.icon} />
      )}
      
      <Text style={[styles.alertText, { color: alertStyle.textColor }]}>
        {getAlertText()}
      </Text>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  icon: {
    marginRight: 8,
  },
  alertText: {
    fontSize: 14,
    fontWeight: '500',
    flex: 1,
  },
});

export default ExpirationAlert;