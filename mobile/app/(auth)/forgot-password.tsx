import React, { useState } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView, Image, ActivityIndicator } from 'react-native';
import { Link, useRouter } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Mail, ArrowLeft } from 'lucide-react-native';
import { isValidEmail } from 'shared';

export default function ForgotPasswordScreen() {
  const { colors } = useTheme();
  const { resetPassword, loading } = useAuth();
  const router = useRouter();
  
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleResetPassword = async () => {
    if (!email) {
      setError('Please enter your email address');
      return;
    }
    
    if (!isValidEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    try {
      setError(null);
      await resetPassword(email);
      setSuccess(true);
    } catch (err) {
      setError('Failed to send reset email. Please try again.');
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
    successText: {
      color: colors.success,
    },
    titleText: {
      color: colors.text,
    },
    subtitleText: {
      color: colors.textSecondary,
    },
    backButton: {
      color: colors.text,
    }
  });

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={[styles.container, dynamicStyles.container]}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <ArrowLeft size={24} color={colors.text} />
        </TouchableOpacity>
        
        <View style={styles.logoContainer}>
          <Image
            source={require('@/assets/images/logo.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </View>

        <Text style={[styles.title, dynamicStyles.titleText]}>Reset Password</Text>
        <Text style={[styles.subtitle, dynamicStyles.subtitleText]}>
          Enter your email address and we'll send you instructions to reset your password
        </Text>

        {error && (
          <Text style={[styles.message, dynamicStyles.errorText]}>{error}</Text>
        )}
        
        {success && (
          <Text style={[styles.message, dynamicStyles.successText]}>
            Password reset email sent! Check your inbox for further instructions.
          </Text>
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
              editable={!success}
            />
          </View>

          {!success ? (
            <TouchableOpacity
              style={[styles.button, dynamicStyles.button, loading && styles.disabledButton]}
              onPress={handleResetPassword}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color={colors.white} />
              ) : (
                <Text style={[styles.buttonText, dynamicStyles.buttonText]}>Send Reset Link</Text>
              )}
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={[styles.button, dynamicStyles.button]}
              onPress={() => router.push('/login')}
            >
              <Text style={[styles.buttonText, dynamicStyles.buttonText]}>Back to Login</Text>
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.footer}>
          <Text style={dynamicStyles.subtitleText}>Remember your password? </Text>
          <Link href="/login" asChild>
            <TouchableOpacity>
              <Text style={dynamicStyles.linkText}>Sign In</Text>
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
  backButton: {
    marginTop: 48,
    marginBottom: 8,
    padding: 8,
    alignSelf: 'flex-start',
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: 20,
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
  message: {
    marginBottom: 16,
    fontFamily: 'Poppins-Medium',
    textAlign: 'center',
    fontSize: 14,
    padding: 8,
  },
});