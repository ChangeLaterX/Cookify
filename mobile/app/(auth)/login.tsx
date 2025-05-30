import React, { useState } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView, Image, ActivityIndicator } from 'react-native';
import { Link, useRouter } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react-native';

export default function LoginScreen() {
  const { colors } = useTheme();
  const { signIn, loading } = useAuth();
  const router = useRouter();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please enter your email and password');
      return;
    }
    
    try {
      setError(null);
      const success = await signIn(email, password);
      if (success) {
        router.replace('/(tabs)');
      }
    } catch (err) {
      setError('Invalid email or password');
      console.error(err);
    }
  };

  const dynamicStyles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    inputContainer: {
      borderColor: colors.border,
      backgroundColor: colors.card,
    },
    inputText: {
      color: colors.text,
    },
    button: {
      backgroundColor: colors.primary,
    },
    buttonText: {
      color: colors.white,
    },
    linkText: {
      color: colors.primary,
    },
    errorText: {
      color: colors.error,
    },
    titleText: {
      color: colors.text,
    },
    subtitleText: {
      color: colors.textSecondary,
    },
  });

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={[styles.container, dynamicStyles.container]}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.logoContainer}>
          <Image
            source={require('@/assets/images/logo.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </View>

        <Text style={[styles.title, dynamicStyles.titleText]}>Welcome Back!</Text>
        <Text style={[styles.subtitle, dynamicStyles.subtitleText]}>
          Sign in to manage your pantry and discover recipes
        </Text>

        {error && (
          <Text style={[styles.errorMessage, dynamicStyles.errorText]}>{error}</Text>
        )}

        <View style={styles.formContainer}>
          <View style={[styles.inputWrapper, dynamicStyles.inputContainer]}>
            <Mail size={20} color={colors.textSecondary} />
            <TextInput
              style={[styles.input, dynamicStyles.inputText]}
              placeholder="Email"
              placeholderTextColor={colors.textSecondary}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>

          <View style={[styles.inputWrapper, dynamicStyles.inputContainer]}>
            <Lock size={20} color={colors.textSecondary} />
            <TextInput
              style={[styles.input, dynamicStyles.inputText]}
              placeholder="Password"
              placeholderTextColor={colors.textSecondary}
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
            />
            <TouchableOpacity
              onPress={() => setShowPassword(!showPassword)}
              style={styles.eyeIcon}
            >
              {showPassword ? (
                <EyeOff size={20} color={colors.textSecondary} />
              ) : (
                <Eye size={20} color={colors.textSecondary} />
              )}
            </TouchableOpacity>
          </View>

          <Link href="/forgot-password" asChild>
            <TouchableOpacity style={styles.forgotPassword}>
              <Text style={[styles.forgotPasswordText, dynamicStyles.linkText]}>
                Forgot Password?
              </Text>
            </TouchableOpacity>
          </Link>

          <TouchableOpacity
            style={[styles.button, dynamicStyles.button, loading && styles.disabledButton]}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color={colors.white} />
            ) : (
              <Text style={[styles.buttonText, dynamicStyles.buttonText]}>Sign In</Text>
            )}
          </TouchableOpacity>
        </View>

        <View style={styles.footer}>
          <Text style={dynamicStyles.subtitleText}>Don't have an account? </Text>
          <Link href="/signup" asChild>
            <TouchableOpacity>
              <Text style={dynamicStyles.linkText}>Sign Up</Text>
            </TouchableOpacity>
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContainer: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: 60,
    marginBottom: 40,
  },
  logo: {
    width: 120,
    height: 120,
  },
  title: {
    fontSize: 28,
    fontFamily: 'Poppins-Bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 32,
    fontFamily: 'Poppins-Regular',
  },
  formContainer: {
    width: '100%',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 16,
    height: 56,
  },
  input: {
    flex: 1,
    paddingLeft: 12,
    height: '100%',
    fontFamily: 'Poppins-Regular',
  },
  eyeIcon: {
    padding: 8,
  },
  forgotPassword: {
    alignSelf: 'flex-end',
    marginBottom: 24,
  },
  forgotPasswordText: {
    fontFamily: 'Poppins-Medium',
  },
  button: {
    height: 56,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  disabledButton: {
    opacity: 0.7,
  },
  buttonText: {
    fontSize: 16,
    fontFamily: 'Poppins-Bold',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 'auto',
    paddingVertical: 16,
  },
  errorMessage: {
    marginBottom: 16,
    fontFamily: 'Poppins-Medium',
    textAlign: 'center',
  },
});