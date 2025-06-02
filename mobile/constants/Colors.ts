/**
 * Cookify App Color Palette
 */

// Base colors
export const primary = {
  50: '#E8F5E9',
  100: '#C8E6C9',
  200: '#A5D6A7',
  300: '#81C784',
  400: '#66BB6A',
  500: '#4CAF50', // Primary green
  600: '#43A047',
  700: '#388E3C',
  800: '#2E7D32',
  900: '#1B5E20',
};

export const secondary = {
  50: '#FFF3E0',
  100: '#FFE0B2',
  200: '#FFCC80',
  300: '#FFB74D',
  400: '#FFA726',
  500: '#FF9800', // Secondary orange
  600: '#FB8C00',
  700: '#F57C00',
  800: '#EF6C00',
  900: '#E65100',
};

export const accent = {
  50: '#E1F5FE',
  100: '#B3E5FC',
  200: '#81D4FA',
  300: '#4FC3F7',
  400: '#29B6F6',
  500: '#03A9F4', // Accent blue
  600: '#039BE5',
  700: '#0288D1',
  800: '#0277BD',
  900: '#01579B',
};

export const neutral = {
  50: '#FAFAFA',
  100: '#F5F5F5',
  200: '#EEEEEE',
  300: '#E0E0E0',
  400: '#BDBDBD',
  500: '#9E9E9E',
  600: '#757575',
  700: '#616161',
  800: '#424242',
  900: '#212121',
};

export const success = {
  light: '#81C784',
  main: '#4CAF50',
  dark: '#388E3C',
};

export const warning = {
  light: '#FFD54F',
  main: '#FFC107',
  dark: '#FFA000',
};

export const error = {
  light: '#E57373',
  main: '#F44336',
  dark: '#D32F2F',
};

// Expiration status colors
export const expiration = {
  fresh: '#4CAF50', // Good for a while
  soon: '#FFC107', // Expiring soon
  expired: '#F44336', // Expired
};

// Theme colors
export const light = {
  text: neutral[900],
  background: neutral[50],
  card: 'white',
  border: neutral[200],
  notification: secondary[500],
};

export const dark = {
  text: neutral[50],
  background: neutral[900],
  card: neutral[800],
  border: neutral[700],
  notification: secondary[500],
};

// Default theme
export default {
  light,
  dark,
  primary,
  secondary,
  accent,
  neutral,
  success,
  warning,
  error,
  expiration,
};