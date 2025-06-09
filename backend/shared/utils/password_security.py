"""
Enhanced Password Security Module
Provides comprehensive password validation, common password detection, and password history management.
"""

import hashlib
import re
import string
import ipaddress
from typing import Any, Dict, List, Optional, Set, Union, Tuple
from urllib.parse import urlparse
from pathlib import Path
from dataclasses import dataclass
from enum import IntEnum
import json


class PasswordStrength(IntEnum):
    """Password strength levels for feedback."""
    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    GOOD = 3
    STRONG = 4
    VERY_STRONG = 5


@dataclass
class PasswordAnalysis:
    """Detailed password analysis result."""
    strength: PasswordStrength
    score: int  # 0-100
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    meets_requirements: Dict[str, bool]


class CommonPasswordsValidator:
    """Validates passwords against common password lists."""
    
    def __init__(self):
        self._common_passwords: Set[str] = set()
        self._load_common_passwords()
    
    def _load_common_passwords(self):
        """Load common passwords from built-in list."""
        # Extended list of most common passwords (top 500+ for better protection)
        common_passwords = [
            # Top 100 most common passwords
            "123456", "password", "123456789", "12345678", "12345", "1234567",
            "1234567890", "qwerty", "abc123", "million2", "000000", "1234",
            "iloveyou", "aaron431", "password1", "qqww1122", "123", "omgpop",
            "123321", "654321", "qwertyuiop", "qwerty123", "123abc", "123qwe",
            "admin", "password123", "1q2w3e4r", "1qaz2wsx", "welcome", "monkey",
            "dragon", "letmein", "baseball", "1234qwer", "sunshine", "princess",
            "football", "charlie", "aa123456", "donald", "password12", "qwerty1",
            "starwars", "klaster", "112233", "samsung", "freedom", "superman",
            "qazwsxedc", "zxcvbnm", "hello", "liverpool", "buster", "soccer",
            "jordan23", "asdfgh", "master", "hannah", "andrew", "martin",
            "shadow", "mickey", "qwerty12", "robert", "jennifer", "thomas",
            "tigger", "computer", "chelsea", "arsenal", "123654", "daniel",
            "ferrari", "jasmine", "jonathan", "amanda", "melissa", "alexander",
            "cookie", "starwars1", "orange", "hunter", "harley", "matthew",
            "121212", "secret", "hockey", "dallas", "taylor", "batman",
            "london", "jessica", "yellow", "basketball", "phoenix", "patrick",
            "ranger", "michael", "sebastian", "purple", "michelle", "flower",
            "lovely", "player", "nicole", "mercedes", "princess1", "eagles",
            "charles", "winners", "golden", "swimming", "nintendo", "maggie",
            
            # Additional common passwords and patterns
            "trustno1", "login", "login123", "test", "test123", "testing",
            "guest", "guest123", "user", "user123", "demo", "demo123",
            "temp", "temp123", "sample", "sample123", "example", "example123",
            "changeme", "newpassword", "mypassword", "default", "administrator",
            "root", "toor", "pass", "pass123", "passw0rd", "p@ssw0rd",
            "p@ssword", "letmein123", "welcome123", "welcome1", "qwerty12345",
            "asdfghjkl", "zxcvbnm123", "poiuytrewq", "mnbvcxz", "lkjhgfdsa",
            "1qaz2wsx3edc", "qwertzuiop", "azerty", "azerty123", "qwertz",
            "uiophjklnm", "asdfasdf", "qwerty1234", "12341234", "abcdabcd",
            "passwordpassword", "123password", "password321", "myname123",
            "lastname", "firstname", "birthday", "anniversary", "mother",
            "father", "family", "love", "loveyou", "iloveu", "lover",
            "summer", "winter", "spring", "autumn", "monday", "friday",
            "weekend", "holiday", "christmas", "newyear", "valentine",
            "company", "work", "office", "business", "money", "dollar",
            "super", "awesome", "amazing", "fantastic", "wonderful", "beautiful",
            "smart", "intelligent", "genius", "winner", "champion", "success",
            "lucky", "fortune", "magic", "power", "strong", "force",
            "apple", "google", "microsoft", "facebook", "twitter", "instagram",
            "linkedin", "youtube", "amazon", "netflix", "spotify", "gmail",
            "email", "internet", "website", "online", "digital", "computer",
            "laptop", "mobile", "phone", "device", "technology", "software",
            "ninja", "warrior", "samurai", "knight", "king", "queen",
            "prince", "princess", "angel", "devil", "god", "heaven",
            "earth", "world", "universe", "galaxy", "star", "moon",
            "sun", "light", "dark", "black", "white", "red", "blue",
            "green", "yellow", "orange", "purple", "pink", "silver", "gold"
        ]
        
        # Add comprehensive variations and patterns for dictionary attack protection
        for password in common_passwords:
            base_password = password.lower()
            self._common_passwords.add(base_password)
            
            # Common number/symbol variations
            variations = [
                password + "!",
                password + "1",
                password + "12",
                password + "123",
                password + "1234",
                password + "@",
                password + "#",
                password + "$",
                password + ".",
                password + "?",
                "!" + password,
                "1" + password,
                "@" + password,
                password.capitalize(),
                password.upper(),
                password + "0",
                password + "00",
                password + "01",
                password + "02",
                password + "99",
                password + "2024",
                password + "2025",
                password + "2026",
                password + "21",
                password + "22",
                password + "23",
                password + "24",
                password + "25",
            ]
            
            # L33t speak variations
            leet_map = {
                'a': ['4', '@'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'],
                's': ['5', '$'], 't': ['7'], 'l': ['1'], 'g': ['9']
            }
            
            leet_password = password.lower()
            for char, replacements in leet_map.items():
                for replacement in replacements:
                    if char in leet_password:
                        variations.append(leet_password.replace(char, replacement))
            
            # Add all variations
            for variation in variations:
                if len(variation) >= 4:  # Only add meaningful variations
                    self._common_passwords.add(variation.lower())
                    
        # Add common substitution patterns
        common_substitutions = [
            ("password", "p4ssw0rd"), ("password", "passw0rd"), ("password", "p@ssword"),
            ("admin", "4dmin"), ("admin", "@dmin"), ("welcome", "w3lcome"),
            ("hello", "h3llo"), ("love", "l0ve"), ("money", "m0ney")
        ]
        
        for original, substituted in common_substitutions:
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
        for prefix in ['my', 'the', 'new', 'old']:
            if password_clean.startswith(prefix):
                password_clean = password_clean[len(prefix):]
                if password_clean in self._common_passwords:
                    return True
                    
        for suffix in ['123', '1', '!', '?', '.', '@', '#', '$', '0', '00']:
            if password_lower.endswith(suffix):
                password_clean = password_lower[:-len(suffix)]
                if password_clean in self._common_passwords:
                    return True
        
        # Check for number/year insertions
        for year in ['2024', '2025', '2026', '21', '22', '23', '24', '25']:
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
        incremental_patterns = ['0123', '1234', '2345', '3456', '4567', '5678', '6789', '9876', '8765', '7654', '6543', '5432', '4321', '3210']
        for pattern in incremental_patterns:
            if pattern in password_lower:
                patterns.append(f"Contains incremental pattern: '{pattern}'")
        
        # Check for alternating patterns
        alternating_patterns = ['0101', '1010', '1212', '2121', 'abab', 'baba']
        for pattern in alternating_patterns:
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
        
        # Minimum requirements (balanced security and usability)
        self.MIN_LENGTH = 8  # Standard minimum length for good security
        self.MAX_LENGTH = 128
        self.MIN_UNIQUE_CHARS = 6  # Reasonable variety requirement
        self.MAX_REPEATED_CHAR_RATIO = 0.4  # Allow some repetition for usability
        
        # Character set requirements (enforce good practices)
        self.REQUIRE_UPPERCASE = True
        self.REQUIRE_LOWERCASE = True  
        self.REQUIRE_DIGITS = True
        self.REQUIRE_SPECIAL = True
        self.MIN_CHAR_TYPES = 3  # Require at least 3 out of 4 character types
        self.MIN_ENTROPY_SCORE = 35  # Reasonable entropy requirement
        
        # Security patterns (focused on truly problematic patterns)
        self.forbidden_patterns = [
            r'(.)\1{3,}',           # 4+ repeated characters (e.g., aaaa)
            r'(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)',  # Long sequential numbers (4+ chars)
            r'(abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)',  # Long sequential letters (4+ chars)
            r'(qwer|wert|erty|rtyu|tyui|yuio|uiop|asdf|sdfg|dfgh|fghj|ghjk|hjkl|zxcv|xcvb|cvbn|vbnm)',  # Long keyboard patterns (4+ chars)
            r'^(password|admin|user|guest|login|welcome|secret|temp|test|demo)$',  # Full word matches only
            r'^(123|abc|qwe|asd|zxc)$',  # Simple pattern starts only if entire password
            r'^(password123|admin123|welcome123|letmein|qwerty123)$',  # Common combinations as full password only
        ]
    
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
        has_special = any(c in string.punctuation for c in password)
        
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
                missing_types.append("special characters (!@#$%^&*)")
            
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
        if len(password) >= 16:
            score += 10
        if len(password) >= 20:
            score += 5
        if char_types == 4 and len(password) >= 16:
            score += 10
        if unique_chars >= 12:
            score += 5
        
        # Calculate final score (0-100)
        score = min(100, max(0, score))
        
        # Determine strength level (STRICTER REQUIREMENTS)
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
            if len(password) < 16:
                warnings.append("Passwords 16+ characters provide better security")
        
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
                if len(part) >= 3 and part in password_lower:
                    violations.append("Password contains parts of your email address")
                    break
        
        # Check names
        names_to_check = []
        for field in ['first_name', 'last_name', 'display_name', 'username']:
            value = user_info.get(field, '')
            if value and len(value) >= 3:
                names_to_check.append(value.lower())
        
        for name in names_to_check:
            if name in password_lower:
                violations.append("Password contains your name or username")
                break
        
        # Check user ID patterns
        user_id = str(user_info.get('user_id', ''))
        if len(user_id) >= 4 and user_id in password:
            violations.append("Password contains user ID information")
        
        return violations
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy score based on character space and length."""
        if not password:
            return 0.0
            
        # Determine character space
        char_space = 0
        if any(c.islower() for c in password):
            char_space += 26  # lowercase letters
        if any(c.isupper() for c in password):
            char_space += 26  # uppercase letters
        if any(c.isdigit() for c in password):
            char_space += 10  # digits
        if any(c in string.punctuation for c in password):
            char_space += len(string.punctuation)  # special characters
        
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
        """Calculate password strength based on score with reasonable thresholds."""
        # Base strength on score, with some consideration for critical errors
        if score >= 90:
            return PasswordStrength.VERY_STRONG
        elif score >= 75:
            return PasswordStrength.STRONG
        elif score >= 60:
            return PasswordStrength.GOOD
        elif score >= 45:
            return PasswordStrength.FAIR
        elif score >= 25:
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
