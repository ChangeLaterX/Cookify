import React from 'react';
import { View, Text, StyleSheet, Image, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '@/context/AuthContext';
import Button from '@/components/ui/Button';
import Colors from '@/constants/Colors';
import { LogOut, Settings, ShieldCheck, CameraIcon, Info, HelpCircle, Bell } from 'lucide-react-native';

export default function ProfileScreen() {
  const { user, signOut } = useAuth();
  const { router } = require('expo-router'); // Using require here to avoid top-level import issues if any with router

  const handleSignOut = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Sign Out', 
          style: 'destructive',
          onPress: signOut
        }
      ]
    );
  };

  if (!user) {
    return null;
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <Text style={styles.title}>Profile</Text>
        </View>
        
        <View style={styles.profileCard}>
          <View style={styles.avatarContainer}>
            <Image 
              source={{ uri: 'https://images.pexels.com/photos/3785991/pexels-photo-3785991.jpeg' }}
              style={styles.avatar}
            />
            <View style={styles.cameraButton}>
              <CameraIcon size={16} color="white" />
            </View>
          </View>
          
          <Text style={styles.userName}>{user.email?.split('@')[0] || 'User'}</Text>
          <Text style={styles.userEmail}>{user.email}</Text>
        </View>
        
        <View style={styles.settingsSection}>
          <Text style={styles.sectionTitle}>Account Settings</Text>
          
          <View style={styles.settingsCard}>
            <Button
              title="Edit Profile"
              leftIcon={<Settings size={20} color={Colors.neutral[600]} />}
              variant="text"
              style={styles.settingButton}
              textStyle={styles.settingButtonText}
              onPress={() => Alert.alert('Coming Soon', 'This feature will be available soon!')}
            />
            
            <View style={styles.divider} />
            
            <Button
              title="Privacy & Security"
              leftIcon={<ShieldCheck size={20} color={Colors.neutral[600]} />}
              variant="text"
              style={styles.settingButton}
              textStyle={styles.settingButtonText}
              onPress={() => Alert.alert('Coming Soon', 'This feature will be available soon!')}
            />
            
            <View style={styles.divider} />

            <Button
              title="Notifications"
              leftIcon={<Bell size={20} color={Colors.neutral[600]} />}
              variant="text"
              style={styles.settingButton}
              textStyle={styles.settingButtonText}
              onPress={() => router.push('/(tabs)/alerts')}
            />
          </View>
        </View>
        
        <View style={styles.settingsSection}>
          <Text style={styles.sectionTitle}>Help & Support</Text>
          
          <View style={styles.settingsCard}>
            <Button
              title="FAQ"
              leftIcon={<HelpCircle size={20} color={Colors.neutral[600]} />}
              variant="text"
              style={styles.settingButton}
              textStyle={styles.settingButtonText}
              onPress={() => Alert.alert('Coming Soon', 'This feature will be available soon!')}
            />
            
            <View style={styles.divider} />
            
            <Button
              title="About Cookify"
              leftIcon={<Info size={20} color={Colors.neutral[600]} />}
              variant="text"
              style={styles.settingButton}
              textStyle={styles.settingButtonText}
              onPress={() => Alert.alert('About Cookify', 'Version 1.0.0\nBuilt with ❤️ for the Bolt Hackathon')}
            />
          </View>
        </View>
        
        <View style={styles.signOutButtonContainer}>
          <Button
            title="Sign Out"
            leftIcon={<LogOut size={20} color={Colors.error.main} />}
            variant="outline"
            style={styles.signOutButton}
            textStyle={{ color: Colors.error.main }}
            onPress={handleSignOut}
          />
        </View>
      </ScrollView>
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
  profileCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 24,
    marginHorizontal: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 4,
    borderColor: Colors.primary[100],
  },
  cameraButton: {
    position: 'absolute',
    right: 0,
    bottom: 0,
    backgroundColor: Colors.primary[500],
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'white',
  },
  userName: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 20,
    color: Colors.neutral[800],
  },
  userEmail: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
    marginTop: 4,
  },
  settingsSection: {
    marginTop: 24,
    paddingHorizontal: 24,
  },
  sectionTitle: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 16,
    color: Colors.neutral[700],
    marginBottom: 12,
  },
  settingsCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 1,
  },
  settingButton: {
    justifyContent: 'flex-start',
    paddingVertical: 16,
    backgroundColor: 'white',
    borderRadius: 0,
  },
  settingButtonText: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[800],
    textAlign: 'left',
  },
  divider: {
    height: 1,
    backgroundColor: Colors.neutral[200],
  },
  signOutButtonContainer: {
    marginTop: 36,
    marginBottom: 24,
    paddingHorizontal: 24,
  },
  signOutButton: {
    borderColor: Colors.error.main,
    marginTop: 8,
  },
});