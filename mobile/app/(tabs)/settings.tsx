import React from 'react';
import { StyleSheet, View, Text, ScrollView, TouchableOpacity, Switch } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { Moon, Sun, Bell, User, Info, LogOut, ChevronRight } from 'lucide-react-native';

export default function SettingsScreen() {
  const { colors, isDark, toggleTheme } = useTheme();
  const { signOut, user } = useAuth();
  
  const handleSignOut = async () => {
    await signOut();
  };

  const dynamicStyles = StyleSheet.create({
    container: {
      backgroundColor: colors.background,
    },
    sectionTitle: {
      color: colors.textSecondary,
    },
    card: {
      backgroundColor: colors.card,
    },
    rowText: {
      color: colors.text,
    },
    divider: {
      backgroundColor: colors.border,
    },
    dangerText: {
      color: colors.error,
    },
    versionText: {
      color: colors.textSecondary,
    },
  });

  return (
    <ScrollView 
      style={[styles.container, dynamicStyles.container]}
      contentContainerStyle={styles.contentContainer}
    >
      <View style={styles.profileSection}>
        <View style={styles.profileInfo}>
          <User size={40} color={colors.primary} />
          <View style={styles.profileText}>
            <Text style={[styles.profileName, dynamicStyles.rowText]}>
              {user?.email || 'User'}
            </Text>
            <Text style={[styles.profileEmail, dynamicStyles.sectionTitle]}>
              {user?.email || 'user@example.com'}
            </Text>
          </View>
        </View>
        
        <TouchableOpacity style={styles.editButton}>
          <Text style={{ color: colors.primary, fontFamily: 'Poppins-Medium' }}>
            Edit
          </Text>
        </TouchableOpacity>
      </View>
      
      <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>
        Appearance
      </Text>
      
      <View style={[styles.card, dynamicStyles.card]}>
        <View style={styles.settingsRow}>
          <View style={styles.rowLeft}>
            {isDark ? (
              <Moon size={22} color={colors.primary} />
            ) : (
              <Sun size={22} color={colors.primary} />
            )}
            <Text style={[styles.rowText, dynamicStyles.rowText]}>Dark Mode</Text>
          </View>
          <Switch
            value={isDark}
            onValueChange={toggleTheme}
            trackColor={{ false: '#ccc', true: colors.primaryLight }}
            thumbColor={isDark ? colors.primary : '#f4f3f4'}
          />
        </View>
      </View>
      
      <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>
        Notifications
      </Text>
      
      <View style={[styles.card, dynamicStyles.card]}>
        <View style={styles.settingsRow}>
          <View style={styles.rowLeft}>
            <Bell size={22} color={colors.primary} />
            <Text style={[styles.rowText, dynamicStyles.rowText]}>Expiration Alerts</Text>
          </View>
          <Switch
            value={true}
            trackColor={{ false: '#ccc', true: colors.primaryLight }}
            thumbColor={true ? colors.primary : '#f4f3f4'}
          />
        </View>
        
        <View style={[styles.divider, dynamicStyles.divider]} />
        
        <View style={styles.settingsRow}>
          <View style={styles.rowLeft}>
            <Bell size={22} color={colors.primary} />
            <Text style={[styles.rowText, dynamicStyles.rowText]}>Low Stock Alerts</Text>
          </View>
          <Switch
            value={true}
            trackColor={{ false: '#ccc', true: colors.primaryLight }}
            thumbColor={true ? colors.primary : '#f4f3f4'}
          />
        </View>
      </View>
      
      <Text style={[styles.sectionTitle, dynamicStyles.sectionTitle]}>
        About
      </Text>
      
      <View style={[styles.card, dynamicStyles.card]}>
        <TouchableOpacity style={styles.settingsRow}>
          <View style={styles.rowLeft}>
            <Info size={22} color={colors.primary} />
            <Text style={[styles.rowText, dynamicStyles.rowText]}>About PantryPal</Text>
          </View>
          <ChevronRight size={20} color={colors.textSecondary} />
        </TouchableOpacity>
        
        <View style={[styles.divider, dynamicStyles.divider]} />
        
        <TouchableOpacity style={styles.settingsRow}>
          <View style={styles.rowLeft}>
            <Info size={22} color={colors.primary} />
            <Text style={[styles.rowText, dynamicStyles.rowText]}>Privacy Policy</Text>
          </View>
          <ChevronRight size={20} color={colors.textSecondary} />
        </TouchableOpacity>
        
        <View style={[styles.divider, dynamicStyles.divider]} />
        
        <TouchableOpacity style={styles.settingsRow}>
          <View style={styles.rowLeft}>
            <Info size={22} color={colors.primary} />
            <Text style={[styles.rowText, dynamicStyles.rowText]}>Terms of Service</Text>
          </View>
          <ChevronRight size={20} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>
      
      <TouchableOpacity 
        style={[styles.signOutButton, { borderColor: colors.error }]}
        onPress={handleSignOut}
      >
        <LogOut size={22} color={colors.error} />
        <Text style={[styles.signOutText, dynamicStyles.dangerText]}>Sign Out</Text>
      </TouchableOpacity>
      
      <Text style={[styles.versionText, dynamicStyles.versionText]}>
        Version 1.0.0
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
    paddingBottom: 40,
  },
  profileSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  profileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profileText: {
    marginLeft: 16,
  },
  profileName: {
    fontSize: 18,
    fontFamily: 'Poppins-Bold',
  },
  profileEmail: {
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
  },
  editButton: {
    padding: 8,
  },
  sectionTitle: {
    fontSize: 14,
    fontFamily: 'Poppins-Medium',
    marginBottom: 8,
    marginTop: 16,
  },
  card: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  settingsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  rowLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rowText: {
    fontSize: 16,
    fontFamily: 'Poppins-Regular',
    marginLeft: 16,
  },
  divider: {
    height: 1,
    marginHorizontal: 16,
  },
  signOutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginTop: 32,
    marginBottom: 24,
    borderWidth: 1,
  },
  signOutText: {
    fontSize: 16,
    fontFamily: 'Poppins-Medium',
    marginLeft: 8,
  },
  versionText: {
    textAlign: 'center',
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
  },
});