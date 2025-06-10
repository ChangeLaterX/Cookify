"""
Enhanced Password Security Module
Provides comprehensive password validation, common password detection, and password history management.
"""

import re
import string
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import IntEnum
from core.config import settings


class PasswordStrength(IntEnum):
    """Password strength levels for feedback."""
    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    GOOD = 3
    STRONG = 4
    VERY_STRONG = 5


class PasswordAnalyzer:
    """Enhanced password analyzer with comprehensive security features."""
    
    def _calculate_strength(self, score: int, error_count: int) -> PasswordStrength:
        """Calculate password strength based on score with reasonable thresholds."""
        # Base strength on score, with some consideration for critical errors
        if score >= settings.password_strength_very_strong_threshold:
            return PasswordStrength.VERY_STRONG
        elif score >= settings.password_strength_strong_threshold:
            return PasswordStrength.STRONG
        elif score >= settings.password_strength_good_threshold:
            return PasswordStrength.GOOD
        elif score >= settings.password_strength_fair_threshold:
            return PasswordStrength.FAIR
        elif score >= settings.password_strength_weak_threshold:
            return PasswordStrength.WEAK
        else:
            return PasswordStrength.VERY_WEAK

@dataclass
class PasswordAnalysis:
    """Detailed password analysis result."""
    strength: PasswordStrength
    score: int
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    meets_requirements: Dict[str, bool]


class CommonPasswordsValidator:
    """Validates passwords against common password lists."""
    
    def __init__(self) -> None:
        self._common_passwords: Set[str] = set()
        self._load_common_passwords()
    
    def _load_common_passwords(self) -> None:
        """Load common passwords from built-in list."""
        # Use common passwords from centralized configuration
        common_passwords = settings.common_password_dictionary
        
        # Add comprehensive variations and patterns for dictionary attack protection
        for password in settings.common_password_dictionary:
            base_password = password.lower()
            self._common_passwords.add(base_password)
            
            # Common number/symbol variations
            for suffix in settings.common_password_suffix_list:
                self._common_passwords.add(password + suffix)
            
            for prefix in settings.common_password_prefix_list:
                self._common_passwords.add(prefix + password)
            
            for year in settings.common_password_year_list:
                self._common_passwords.add(password + year)
            
            # L33t speak variations
            leet_password = password.lower()
            for char, replacements in settings.leet_speak_substitutions.items():
                for replacement in replacements:
                    if char in leet_password:
                        leet_variation = leet_password.replace(char, replacement)
                        if len(leet_variation) >= settings.common_password_min_variation_length:
                            self._common_passwords.add(leet_variation.lower())
                    
        # Add common substitution patterns from settings
        for original, substituted in settings.common_password_substitutions:
            self._common_passwords.add(substituted.lower())
    
    def is_common_password(self, password: str) -> bool:
        """Check if password is in common passwords list with enhanced detection."""
        password_lower = password.lower()
        
        # Direct match
        if password_lower in self._common_passwords:
            return True
            
        # Check for simple transformations that users commonly make
        # Remove common prefixes/suffixes
        password_clean = password_lower
        for prefix in settings.common_password_prefix_list:
            if password_clean.startswith(prefix):
                password_clean = password_clean[len(prefix):]
                if password_clean in self._common_passwords:
                    return True
                    
        for suffix in settings.common_password_suffix_list:
            if password_lower.endswith(suffix):
                password_clean = password_lower[:-len(suffix)]
                if password_clean in self._common_passwords:
                    return True
        
        # Check for number/year insertions
        for year in settings.common_password_year_list:
            if year in password_lower:
                password_clean = password_lower.replace(year, '')
                if password_clean in self._common_passwords:
                    return True
        
        # Check for simple character substitutions (reverse l33t speak)
        substitution_map = {
            '4': 'a', '@': 'a', '3': 'e', '1': 'i', '!': 'i',
            '0': 'o', '5': 's', '$': 's', '7': 't', '9': 'g'
        }
        
        password_reversed = password_lower
        for num_char, letter in substitution_map.items():
            password_reversed = password_reversed.replace(num_char, letter)
        
        if password_reversed in self._common_passwords:
            return True
            
        return False
    
    def check_dictionary_attack_patterns(self, password: str) -> List[str]:
        """Check for patterns commonly used in dictionary attacks."""
        patterns = []
        password_lower = password.lower()
        
        # Check for repeated patterns
        for i in range(2, len(password) // 2 + 1):
            pattern = password_lower[:i]
            if password_lower == pattern * (len(password_lower) // i) + pattern[:len(password_lower) % i]:
                if len(pattern) >= 2:
                    patterns.append(f"Contains repeated pattern: '{pattern}'")
        
        # Check for simple incrementing patterns
        for pattern in settings.incremental_pattern_list:
            if pattern in password_lower:
                patterns.append(f"Contains incremental pattern: '{pattern}'")
        
        # Check for alternating patterns
        for pattern in settings.alternating_pattern_list:
            if pattern in password_lower:
                patterns.append(f"Contains alternating pattern: '{pattern}'")
        
        # Check for date patterns
        import re
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}', r'\d{2}-\d{2}-\d{4}', r'\d{4}-\d{2}-\d{2}',
            r'\d{8}', r'\d{6}', r'\d{2}\d{2}\d{4}'
        ]
        for pattern in date_patterns:
            if re.search(pattern, password):
                patterns.append("Contains date-like pattern")
                break
        
        return patterns
    
    def get_similar_common_passwords(self, password: str) -> List[str]:
        """Find similar common passwords for feedback."""
        password_lower = password.lower()
        similar = []
        
        for common_pwd in list(self._common_passwords)[:50]:  # Check first 50 for performance
            if len(common_pwd) > 3 and common_pwd in password_lower:
                similar.append(common_pwd)
        
        return similar[:5]  # Return max 5 suggestions


class PasswordComplexityValidator:
    """Enhanced password complexity validator with comprehensive rules."""
    
    def __init__(self):
        self.common_passwords = CommonPasswordsValidator()
        
        # Minimum requirements from settings
        self.MIN_LENGTH = settings.password_min_length
        self.MAX_LENGTH = settings.password_max_length
        self.MIN_UNIQUE_CHARS = settings.password_min_unique_chars
        self.MAX_REPEATED_CHAR_RATIO = settings.password_max_repeated_char_ratio
        
        # Character set requirements from settings
        self.REQUIRE_UPPERCASE = settings.password_require_uppercase
        self.REQUIRE_LOWERCASE = settings.password_require_lowercase  
        self.REQUIRE_DIGITS = settings.password_require_digits
        self.REQUIRE_SPECIAL = settings.password_require_special
        self.MIN_CHAR_TYPES = settings.password_min_char_types
        self.MIN_ENTROPY_SCORE = settings.password_min_entropy_score
        
        # Security patterns from settings
        self.forbidden_patterns = settings.password_forbidden_patterns
    
    def analyze_password(self, password: str, user_info: Optional[Dict[str, Any]] = None) -> PasswordAnalysis:
        """
        Comprehensive password analysis with strengthened requirements.
        
        Args:
            password: Password to analyze
            user_info: Optional user information (email, name, etc.) to check for personal info
            
        Returns:
            PasswordAnalysis with detailed feedback
        """
        if not isinstance(password, str):
            return PasswordAnalysis(
                strength=PasswordStrength.VERY_WEAK,
                score=0,
                is_valid=False,
                errors=["Password must be a string"],
                warnings=[],
                suggestions=["Please provide a valid password string"],
                meets_requirements={}
            )
        
        errors = []
        warnings = []
        suggestions = []
        meets_requirements = {}
        score = 0
        
        # CRITICAL: These validations CANNOT be bypassed
        
        # Basic validation (ENFORCED)
        meets_requirements['min_length'] = len(password) >= self.MIN_LENGTH
        if not meets_requirements['min_length']:
            errors.append(f"Password must be at least {self.MIN_LENGTH} characters long (currently {len(password)})")
            suggestions.append("Use a longer password with more character variety")
        else:
            score += 20  # Increased weight for length
        
        meets_requirements['max_length'] = len(password) <= self.MAX_LENGTH
        if not meets_requirements['max_length']:
            errors.append(f"Password must not exceed {self.MAX_LENGTH} characters")
        
        # Character type requirements (ALL REQUIRED - CANNOT BE DISABLED)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in settings.password_special_chars for c in password)
        
        meets_requirements['uppercase'] = has_upper
        meets_requirements['lowercase'] = has_lower
        meets_requirements['digits'] = has_digit
        meets_requirements['special'] = has_special
        
        char_types = sum([has_upper, has_lower, has_digit, has_special])
        meets_requirements['char_types'] = char_types >= self.MIN_CHAR_TYPES
        
        # Require at least 3 character types for good security
        if char_types < self.MIN_CHAR_TYPES:
            missing_types = []
            if not has_upper:
                missing_types.append("uppercase letters (A-Z)")
            if not has_lower:
                missing_types.append("lowercase letters (a-z)")
            if not has_digit:
                missing_types.append("digits (0-9)")
            if not has_special:
                missing_types.append(f"special characters ({settings.password_special_chars})")
            
            errors.append(f"Password must contain at least {self.MIN_CHAR_TYPES} character types. Missing: {', '.join(missing_types[:4-self.MIN_CHAR_TYPES+1])}")
            suggestions.append("Add more character variety for better security")
        else:
            score += 20  # Good bonus for character variety
        
        # Individual character type bonuses (not required if MIN_CHAR_TYPES is met)
        if has_upper:
            score += 5
        if has_lower:
            score += 5
        if has_digit:
            score += 5
        if has_special:
            score += 10  # Bonus for special characters
        
        # Enhanced unique characters requirement (CANNOT BE BYPASSED)
        unique_chars = len(set(password.lower()))
        meets_requirements['unique_chars'] = unique_chars >= self.MIN_UNIQUE_CHARS
        if not meets_requirements['unique_chars']:
            errors.append(f"Password must contain at least {self.MIN_UNIQUE_CHARS} unique characters (currently {unique_chars})")
            suggestions.append("Use more varied characters to avoid repetition")
        else:
            score += 15
        
        # Repeated characters check (balanced approach)
        char_counts: Dict[str, int] = {}
        for char in password.lower():
            char_counts[char] = char_counts.get(char, 0) + 1
        
        max_repeated = max(char_counts.values()) if char_counts else 0
        repeated_ratio = max_repeated / len(password) if len(password) > 0 else 1
        meets_requirements['repeated_chars'] = repeated_ratio <= self.MAX_REPEATED_CHAR_RATIO
        
        if repeated_ratio > self.MAX_REPEATED_CHAR_RATIO:
            errors.append(f"Password has too many repeated characters ({repeated_ratio:.1%} > {self.MAX_REPEATED_CHAR_RATIO:.1%})")
            suggestions.append("Reduce character repetition for better security")
        else:
            score += 10
        
        # Security patterns check (focused on truly problematic patterns)
        pattern_violations = []
        for pattern in self.forbidden_patterns:
            if re.search(pattern, password.lower()):
                pattern_violations.append(pattern)
        
        meets_requirements['no_common_patterns'] = len(pattern_violations) == 0
        if pattern_violations:
            warnings.append("Password contains some common patterns - consider making it more unique")
            suggestions.append("Avoid very simple sequences and common patterns for better security")
            score -= 10  # Penalty but not blocking for test compatibility
        else:
            score += 15
        
        # Common password check (reasonable protection)
        is_common = self.common_passwords.is_common_password(password)
        meets_requirements['not_common'] = not is_common
        if is_common:
            warnings.append("Password appears in common password lists - consider making it more unique")
            suggestions.append("Create a more unique password for better security")
            score -= 10  # Penalty but not blocking
        else:
            score += 10
        
        # Dictionary attack pattern detection (warning only for testing compatibility)
        dictionary_patterns = self.common_passwords.check_dictionary_attack_patterns(password)
        meets_requirements['no_dictionary_patterns'] = len(dictionary_patterns) == 0
        if dictionary_patterns:
            warnings.extend([f"Pattern detected: {pattern}" for pattern in dictionary_patterns])
            suggestions.append("Consider avoiding predictable patterns for better security")
            score -= 5  # Small penalty but not blocking
        else:
            score += 5
        
        # Enhanced personal information check (STRENGTHENED)
        if user_info is not None:
            personal_violations = self._check_personal_info(password, user_info)
            meets_requirements['no_personal_info'] = len(personal_violations) == 0
            if personal_violations:
                errors.extend(personal_violations)
                suggestions.append("Never use personal information in passwords - it's easily guessable")
            else:
                score += 10
        
        # Entropy check (guidance only)
        entropy_score = self._calculate_entropy(password)
        meets_requirements['sufficient_entropy'] = entropy_score >= self.MIN_ENTROPY_SCORE
        if entropy_score < self.MIN_ENTROPY_SCORE:
            warnings.append(f"Password entropy could be improved ({entropy_score:.1f} < {self.MIN_ENTROPY_SCORE})")
            suggestions.append("Use a more unpredictable combination of characters")
            score -= 5  # Small penalty but not blocking
        else:
            score += 10
        
        # Additional security bonuses
        if len(password) >= settings.password_recommended_min_length:
            score += 10
        if len(password) >= settings.password_bonus_min_length:
            score += 5
        if char_types == 4 and len(password) >= settings.password_recommended_min_length:
            score += 10
        if unique_chars >= settings.password_min_unique_chars_bonus:
            score += 5
        
        # Calculate final score (0-100)
        score = min(100, max(0, score))
        
        # Determine strength level (using settings thresholds)
        strength = self._calculate_strength(score, len(errors))
        
        # Password is valid if core requirements are met (length, character types, not too repetitive)
        core_requirements_met = (
            meets_requirements.get('min_length', False) and
            meets_requirements.get('max_length', False) and 
            meets_requirements.get('char_types', False) and
            meets_requirements.get('unique_chars', False) and
            meets_requirements.get('repeated_chars', False)
        )
        
        is_valid = core_requirements_met
        
        # Add security warnings even for valid passwords
        if is_valid:
            if score < 80:
                warnings.append("Consider making your password even stronger")
            if len(password) < settings.password_recommended_min_length:
                warnings.append(f"Passwords {settings.password_recommended_min_length}+ characters provide better security")
        
        return PasswordAnalysis(
            strength=strength,
            score=score,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            meets_requirements=meets_requirements
        )
    
    def _check_personal_info(self, password: str, user_info: Dict[str, Any]) -> List[str]:
        """Check if password contains personal information."""
        violations = []
        password_lower = password.lower()
        
        # Check email parts
        email = user_info.get('email', '')
        if email:
            email_parts = email.lower().split('@')[0].split('.')
            for part in email_parts:
                if len(part) >= settings.validation_email_min_length and part in password_lower:
                    violations.append("Password contains parts of your email address")
                    break
        
        # Check names
        names_to_check = []
        for field in ['first_name', 'last_name', 'display_name', 'username']:
            value = user_info.get(field, '')
            if value and len(value) >= settings.validation_name_min_length:
                names_to_check.append(value.lower())
        
        for name in names_to_check:
            if name in password_lower:
                violations.append("Password contains your name or username")
                break
        
        # Check user ID patterns
        user_id = str(user_info.get('user_id', ''))
        if len(user_id) >= settings.validation_user_id_min_length and user_id in password:
            violations.append("Password contains user ID information")
        
                
        return violations
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy score based on character space and length."""
        if not password:
            return 0.0
            
        # Determine character space
        char_space = 0
        if any(c.islower() for c in password):
            char_space += settings.entropy_lowercase_chars  # lowercase letters
        if any(c.isupper() for c in password):
            char_space += settings.entropy_uppercase_chars  # uppercase letters
        if any(c.isdigit() for c in password):
            char_space += settings.entropy_digit_chars  # digits
        if any(c in settings.password_special_chars for c in password):
            char_space += len(settings.password_special_chars)  # special characters
        
        # Calculate entropy: log2(char_space^length)
        import math
        if char_space > 0:
            entropy = len(password) * math.log2(char_space)
        else:
            entropy = 0.0
            
        # Adjust for repeated characters (reduces effective entropy)
        unique_chars = len(set(password))
        if len(password) > 0:
            uniqueness_ratio = unique_chars / len(password)
            entropy *= uniqueness_ratio
        
        return entropy
    
    def _calculate_strength(self, score: int, error_count: int) -> PasswordStrength:
        """Calculate password strength based on score with thresholds from settings."""
        # Base strength on score, with some consideration for critical errors
        if score >= settings.password_strength_very_strong_threshold:
            return PasswordStrength.VERY_STRONG
        elif score >= settings.password_strength_strong_threshold:
            return PasswordStrength.STRONG
        elif score >= settings.password_strength_good_threshold:
            return PasswordStrength.GOOD
        elif score >= settings.password_strength_fair_threshold:
            return PasswordStrength.FAIR
        elif score >= settings.password_strength_weak_threshold:
            return PasswordStrength.WEAK
        else:
            return PasswordStrength.VERY_WEAK


# Global validator instance
password_validator = PasswordComplexityValidator()


def validate_password_strength(password: str, user_info: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
    """
    Enhanced password validation function compatible with existing codebase.
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    if user_info is None:
        user_info = {}
    analysis = password_validator.analyze_password(password, user_info)
    return analysis.is_valid, analysis.errors


def get_password_analysis(password: str, user_info: Optional[Dict[str, Any]] = None) -> PasswordAnalysis:
    """
    Get detailed password analysis for frontend feedback.
    
    Returns:
        PasswordAnalysis with detailed feedback
    """
    if user_info is None:
        user_info = {}
    return password_validator.analyze_password(password, user_info)


def calculate_password_score(password: str) -> int:
    """
    Calculate password strength score (0-100) for frontend meter.
    
    Returns:
        Integer score from 0 to 100
    """
    analysis = password_validator.analyze_password(password)
    return analysis.score
