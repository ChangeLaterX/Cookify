#!/usr/bin/env python3
"""
Test script for enhanced password validation system.
"""

from shared.utils.password_security import get_password_analysis, PasswordStrength

def test_password_validation():
    """Test various passwords to verify the enhanced validation."""
    
    test_passwords = [
        'password123',  # Common password - should fail
        'P@ssw0rd123',  # Common with substitutions - should fail  
        'qwerty!@#$',   # Keyboard pattern - should fail
        'Abc123!',      # Too short - should fail
        'MySecureP@ssw0rd2024!',  # Strong password - should pass
        'Tr0ub4dor&3',  # XKCD style - should pass if long enough
        'CorrectHorseBatteryStaple!123',  # Very strong - should pass
        'Simple123!@#',  # Should fail - too simple
        'ComplexP4ssw0rd2024!@#',  # Should pass - complex enough
    ]
    
    print('Testing Enhanced Password Validation:')
    print('=' * 60)
    
    for password in test_passwords:
        print(f'Password: "{password}"')
        
        analysis = get_password_analysis(password)
        
        print(f'  Valid: {analysis.is_valid}')
        print(f'  Strength: {analysis.strength.name}')
        print(f'  Score: {analysis.score}/100')
        
        if analysis.errors:
            print(f'  Errors ({len(analysis.errors)}):')
            for error in analysis.errors[:3]:  # Show first 3 errors
                print(f'    - {error}')
                
        if analysis.warnings:
            print(f'  Warnings: {analysis.warnings[:2]}')
            
        if analysis.suggestions:
            print(f'  Suggestions: {analysis.suggestions[:2]}')
            
        print()
    
    # Test with user info
    print('\nTesting with User Information:')
    print('=' * 40)
    
    user_info = {
        'email': 'john.doe@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'user_id': '12345'
    }
    
    personal_passwords = [
        'JohnDoe123!',  # Contains name - should fail
        'john.doe@123',  # Contains email - should fail  
        'MyStrongP4ssw0rd2024!',  # No personal info - should pass
    ]
    
    for password in personal_passwords:
        print(f'Password: "{password}"')
        analysis = get_password_analysis(password, user_info)
        print(f'  Valid: {analysis.is_valid}')
        print(f'  Contains Personal Info: {not analysis.meets_requirements.get("no_personal_info", True)}')
        if analysis.errors:
            personal_errors = [e for e in analysis.errors if 'personal' in e.lower() or 'name' in e.lower() or 'email' in e.lower()]
            if personal_errors:
                print(f'  Personal Info Errors: {personal_errors}')
        print()

if __name__ == '__main__':
    test_password_validation()
