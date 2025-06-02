import React from 'react';
import { 
  TouchableOpacity, 
  Text, 
  StyleSheet, 
  ActivityIndicator, 
  TouchableOpacityProps, 
  ViewStyle, 
  TextStyle 
} from 'react-native';
import Colors from '@/constants/Colors';

interface ButtonProps extends TouchableOpacityProps {
  title: string;
  variant?: 'primary' | 'secondary' | 'outline' | 'text';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  fullWidth = false,
  style,
  textStyle,
  leftIcon,
  rightIcon,
  ...props
}) => {
  const getButtonStyle = (): ViewStyle => {
    let buttonStyle: ViewStyle = {
      ...styles.button,
      ...styles[`button${size.charAt(0).toUpperCase() + size.slice(1)}`]
    };

    // Add variant styling
    switch (variant) {
      case 'primary':
        buttonStyle = {
          ...buttonStyle,
          backgroundColor: Colors.primary[500],
        };
        break;
      case 'secondary':
        buttonStyle = {
          ...buttonStyle,
          backgroundColor: Colors.secondary[500],
        };
        break;
      case 'outline':
        buttonStyle = {
          ...buttonStyle,
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderColor: Colors.primary[500],
        };
        break;
      case 'text':
        buttonStyle = {
          ...buttonStyle,
          backgroundColor: 'transparent',
          elevation: 0,
          shadowOpacity: 0,
        };
        break;
    }

    // Add fullWidth if needed
    if (fullWidth) {
      buttonStyle.width = '100%';
    }

    // Add disabled styling
    if (disabled || loading) {
      buttonStyle.opacity = 0.6;
    }

    return buttonStyle;
  };

  const getTextStyle = (): TextStyle => {
    let finalTextStyle: TextStyle = { ...styles.buttonText };

    // Add variant text styling
    switch (variant) {
      case 'outline':
      case 'text':
        finalTextStyle = {
          ...finalTextStyle,
          color: Colors.primary[500],
        };
        break;
      default:
        finalTextStyle = {
          ...finalTextStyle,
          color: 'white',
        };
    }

    // Add size-specific text styling
    switch (size) {
      case 'small':
        finalTextStyle = {
          ...finalTextStyle,
          fontSize: 14,
        };
        break;
      case 'large':
        finalTextStyle = {
          ...finalTextStyle,
          fontSize: 18,
        };
        break;
      default:
        finalTextStyle = {
          ...finalTextStyle,
          fontSize: 16,
        };
    }

    return { ...finalTextStyle, ...textStyle };
  };

  return (
    <TouchableOpacity
      {...props}
      disabled={disabled || loading}
      style={[getButtonStyle(), style]}
    >
      {loading ? (
        <ActivityIndicator 
          size="small" 
          color={variant === 'outline' || variant === 'text' ? Colors.primary[500] : 'white'} 
        />
      ) : (
        <React.Fragment>
          {leftIcon && <Text style={styles.iconContainer}>{leftIcon}</Text>}
          <Text style={getTextStyle()}>{title}</Text>
          {rightIcon && <Text style={styles.iconContainer}>{rightIcon}</Text>}
        </React.Fragment>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
    paddingHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  buttonSmall: {
    paddingVertical: 8,
  },
  buttonMedium: {
    paddingVertical: 12,
  },
  buttonLarge: {
    paddingVertical: 16,
  },
  buttonText: {
    fontWeight: '600',
    textAlign: 'center',
  },
  iconContainer: {
    marginHorizontal: 4,
  },
});

export default Button;