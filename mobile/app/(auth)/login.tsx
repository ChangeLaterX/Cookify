import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Link, router } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Colors from '@/constants/Colors';
import { Mail, Lock, AlertCircle } from 'lucide-react-native';

export default function LoginScreen() {
  const { signIn, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }

    try {
      const { error: signInError } = await signIn(email, password);
      
      if (signInError) {
        setError(signInError.message);
      } else {
        // Successfully logged in, will be redirected by root index
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      console.error('Login error:', err);
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
              source={{ uri: 'https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg' }}
              style={styles.logoBackground}
            />
            <View style={styles.logoOverlay} />
            <View style={styles.brandContainer}>
              <Text style={styles.logoText}>Cookify</Text>
              <Text style={styles.tagline}>Smart pantry. Zero waste.</Text>
            </View>
          </View>

          <View style={styles.formContainer}>
            <Text style={styles.welcomeText}>Welcome Back</Text>
            <Text style={styles.subtitle}>Sign in to continue to your account</Text>

            {error && (
              <View style={styles.errorContainer}>
                <AlertCircle size={18} color={Colors.error.main} />
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
              placeholder="Enter your password"
              secureTextEntry
              value={password}
              onChangeText={setPassword}
              leftIcon={<Lock size={20} color={Colors.neutral[500]} />}
              containerStyle={styles.inputContainer}
            />

            <Link href="/(auth)/forgot-password" asChild>
              <Text style={styles.forgotPassword}>Forgot Password?</Text>
            </Link>

            <Button
              title="Sign In"
              onPress={handleLogin}
              loading={loading}
              fullWidth
              style={styles.loginButton}
            />

            <View style={styles.signupContainer}>
              <Text style={styles.noAccountText}>Don't have an account? </Text>
              <Link href="/(auth)/signup" asChild>
                <Text style={styles.signupLink}>Sign Up</Text>
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
    height: 250,
    position: 'relative',
    justifyContent: 'flex-end',
  },
  logoBackground: {
    ...StyleSheet.absoluteFillObject,
    height: 250,
    width: '100%',
  },
  logoOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.3)',
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
    fontFamily: 'Inter-Regular',
    marginLeft: 8,
    color: Colors.error.main,
    flex: 1,
  },
  inputContainer: {
    marginBottom: 16,
  },
  forgotPassword: {
    fontFamily: 'Inter-Medium',
    color: Colors.primary[600],
    textAlign: 'right',
    marginBottom: 24,
  },
  loginButton: {
    marginBottom: 24,
  },
  signupContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  noAccountText: {
    fontFamily: 'Inter-Regular',
    color: Colors.neutral[600],
  },
  signupLink: {
    fontFamily: 'Inter-SemiBold',
    color: Colors.primary[600],
  },
});