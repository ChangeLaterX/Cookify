/**
 * Validates a non-empty string
 */
export const isNonEmptyString = (value: unknown): boolean => {
  return typeof value === 'string' && value.trim().length > 0;
};

/**
 * Validates a positive number
 */
export const isPositiveNumber = (value: unknown): boolean => {
  return typeof value === 'number' && !isNaN(value) && value > 0;
};

/**
 * Validates an ISO date string
 */
export const isValidDateString = (value: unknown): boolean => {
  if (typeof value !== 'string') return false;
  return !isNaN(Date.parse(value));
};

/**
 * Validates an email address
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validates password strength
 * - At least 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one number
 */
export const isStrongPassword = (password: string): boolean => {
  return (
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /[0-9]/.test(password)
  );
};