import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import Colors from '@/constants/Colors';
import { Mail, AlertCircle, ArrowLeft } from 'lucide-react-native';
import { isValidEmail } from 'shared/src/utils/validationUtils';

export default function ForgotPasswordScreen() {
  const { resetPassword } = useAuth();
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleResetPassword = async () => {
    if (!email) {
      setError('Please enter your email address.');
      return;
    }

    if (!isValidEmail(email)) {
      setError('Please enter a valid email address.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const { error: resetError } = await resetPassword(email);

      if (resetError) {
        setError(resetError.message);
      } else {
        setIsSubmitted(true);
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      console.error('Reset password error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.container}>
          <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 24, marginTop: 36 }}>
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => router.back()}
            >
              <ArrowLeft size={32} color={Colors.neutral[800]} />
            </TouchableOpacity>

            <Text style={styles.title}>Reset Password</Text>

          </View>
          {!isSubmitted ? (
            <>
              <Text style={styles.description}>
                {`Enter your email address and we'll send you instructions to reset your password.`}
              </Text>

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

              <Button
                title="Reset Password"
                onPress={handleResetPassword}
                loading={loading}
                fullWidth
                style={styles.resetButton}
              />
            </>
          ) : (
            <View style={styles.successContainer}>
              <Text style={styles.successTitle}>Check your inbox</Text>
              <Text style={styles.successMessage}>
                {`We've sent password reset instructions to {email}. Please check your email.`}
              </Text>

              <Button
                title="Back to Login"
                onPress={() => router.replace('/(auth)/login')}
                variant="outline"
                style={styles.backToLoginButton}
              />
            </View>
          )}
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
    padding: 24,
  },
  backButton: {
    alignSelf: 'flex-start',
    marginTop: 12,
    marginRight: 10,
    marginBottom: 24,
    marginLeft: 0,
  },
  title: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 28,
    marginBottom: 16,
    color: Colors.neutral[800],
  },
  description: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
    marginBottom: 24,
    lineHeight: 24,
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
    color: Colors.light.default,
    flex: 1,
  },
  inputContainer: {
    marginBottom: 24,
  },
  resetButton: {
    marginTop: 8,
  },
  successContainer: {
    marginTop: 24,
    alignItems: 'center',
  },
  successTitle: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 22,
    color: Colors.success.main,
    marginBottom: 16,
    textAlign: 'center',
  },
  successMessage: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
    marginBottom: 32,
    textAlign: 'center',
    lineHeight: 24,
  },
  backToLoginButton: {
    minWidth: 150,
  },
});