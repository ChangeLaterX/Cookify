import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Button from './ui/Button';
import Colors from '@/constants/Colors';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({ 
  icon, 
  title, 
  message, 
  actionLabel, 
  onAction 
}) => {
  return (
    <View style={styles.container}>
      {icon && (
        <View style={styles.iconContainer}>
          {icon}
        </View>
      )}
      
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.message}>{message}</Text>
      
      {actionLabel && onAction && (
        <Button 
          title={actionLabel} 
          variant="primary" 
          onPress={onAction}
          style={styles.button}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  iconContainer: {
    marginBottom: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.neutral[800],
    marginBottom: 8,
    textAlign: 'center',
  },
  message: {
    fontSize: 16,
    color: Colors.neutral[600],
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  button: {
    minWidth: 150,
  },
});

export default EmptyState;