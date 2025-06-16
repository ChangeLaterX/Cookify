import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Link, router } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Colors from '@/constants/Colors';
import { Mail, Lock, User, AlertCircle } from 'lucide-react-native';
import { isValidEmail, isStrongPassword } from 'shared/src/utils/validationUtils';

export default function SignupScreen() {
  const { signUp, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSignUp = async () => {
    // Validation
    if (!email || !password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }

    if (!isValidEmail(email)) {
      setError('Please enter a valid email address.');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    
    if (!isStrongPassword(password)) {
      setError('Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.');
      return;
    }
    
    try {
      const { error: signUpError, data } = await signUp(email, password);
      
      if (signUpError) {
        setError(signUpError.message);
      } else {
        // Show confirmation message
        setError(null);
        alert('Sign-up successful! Check your email for verification link.');
        router.replace('/(auth)/login');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      console.error('Signup error:', err);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.container}>
          <View style={styles.logoContainer}>
            <Image
              source={{ uri: 'https://images.pexels.com/photos/616404/pexels-photo-616404.jpeg' }}
              style={styles.logoBackground}
            />
            <View style={styles.logoOverlay} />
            <View style={styles.brandContainer}>
              <Text style={styles.logoText}>Cookify</Text>
              <Text style={styles.tagline}>Join our community today</Text>
            </View>
          </View>

          <View style={styles.formContainer}>
            <Text style={styles.welcomeText}>Create Account</Text>
            <Text style={styles.subtitle}>Sign up to start managing your pantry</Text>

            {error && (
              <View style={styles.errorContainer}>
                <AlertCircle size={18} color={Colors.light.default} />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            <Input
              label="Email Address"
              placeholder="Enter your email"
              keyboardType="email-address"
              value={email}
              onChangeText={setEmail}
              leftIcon={<Mail size={20} color={Colors.neutral[500]} />}
              containerStyle={styles.inputContainer}
            />

            <Input
              label="Password"
              placeholder="Create a password"
              secureTextEntry
              value={password}
              onChangeText={setPassword}
              leftIcon={<Lock size={20} color={Colors.neutral[500]} />}
              hint="Must be at least 6 characters"
              containerStyle={styles.inputContainer}
            />
            
            <Input
              label="Confirm Password"
              placeholder="Confirm your password"
              secureTextEntry
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              leftIcon={<Lock size={20} color={Colors.neutral[500]} />}
              containerStyle={styles.inputContainer}
            />

            <Button
              title="Create Account"
              onPress={handleSignUp}
              loading={loading}
              fullWidth
              style={styles.signupButton}
            />

            <View style={styles.loginContainer}>
              <Text style={styles.haveAccountText}>Already have an account? </Text>
              <Link href="/(auth)/login" asChild>
                <Text style={styles.loginLink}>Sign In</Text>
              </Link>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    flexGrow: 1,
  },
  container: {
    flex: 1,
    backgroundColor: 'white',
  },
  logoContainer: {
    height: 200,
    position: 'relative',
    justifyContent: 'flex-end',
  },
  logoBackground: {
    ...StyleSheet.absoluteFillObject,
    height: 200,
    width: '100%',
  },
  logoOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.4)',
  },
  brandContainer: {
    padding: 24,
  },
  logoText: {
    fontFamily: 'Poppins-Bold',
    fontSize: 36,
    color: 'white',
    textShadowColor: 'rgba(0, 0, 0, 0.5)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 5,
  },
  tagline: {
    fontFamily: 'Inter-Medium',
    fontSize: 16,
    color: 'white',
    marginTop: 4,
  },
  formContainer: {
    padding: 24,
  },
  welcomeText: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 24,
    marginBottom: 8,
    color: Colors.neutral[800],
  },
  subtitle: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
    marginBottom: 24,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.error.light,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    fontFamily: 'Inter-Medium',
    marginLeft: 8,
    color: Colors.light.default,
    fontWeight: 'bold',
    flex: 1,
  },
  inputContainer: {
    marginBottom: 16,
  },
  signupButton: {
    marginTop: 8,
    marginBottom: 24,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  haveAccountText: {
    fontFamily: 'Inter-Regular',
    color: Colors.neutral[600],
  },
  loginLink: {
    fontFamily: 'Inter-SemiBold',
    color: Colors.primary[600],
  },
});