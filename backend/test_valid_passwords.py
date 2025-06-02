#!/usr/bin/env python3
"""
Test script for finding valid passwords under the enhanced validation system.
"""

from shared.utils.password_security import get_password_analysis, PasswordStrength

def test_valid_passwords():
    """Test passwords that should pass the enhanced validation."""
    
    # Try passwords that avoid common patterns
    test_passwords = [
        'Thunder#Mountain$Sky9',   # Should pass - no obvious patterns
        'Zebra$Cloud@Wave7',       # Should pass - random words
        'Phoenix&River%Moon4',     # Should pass - nature words
        'Galaxy$Forest@Stone8',    # Should pass - diverse words
        'Diamond&Ocean%Fire3',     # Should pass - element words
        'Quantum$Bridge@Dream6',   # Should pass - abstract words
        'Crimson&Valley%Light2',   # Should pass - color + nature
        'Falcon$Garden@Storm5',    # Should pass - animal + nature
        'Silver&Cosmos%Wind1',     # Should pass - metal + space
        'Mystic$Harbor@Flame0',    # Should pass - mystical + place
    ]
    
    print('Testing for Valid Passwords:')
    print('=' * 50)
    
    valid_count = 0
    
    for password in test_passwords:
        print(f'Password: "{password}"')
        
        analysis = get_password_analysis(password)
        
        print(f'  Valid: {analysis.is_valid}')
        print(f'  Strength: {analysis.strength.name}')
        print(f'  Score: {analysis.score}/100')
        
        if analysis.is_valid:
            valid_count += 1
            print('  ✅ PASSES VALIDATION!')
        else:
            print('  ❌ Failed validation')
            if analysis.errors:
                print(f'  Errors: {analysis.errors[:2]}')
                
        print()
    
    print(f'Summary: {valid_count}/{len(test_passwords)} passwords passed validation')
    
    # Test the API endpoint format
    if valid_count > 0:
        print('\nTesting API Response Format:')
        print('=' * 40)
        
        sample_password = 'Thunder#Mountain$Sky9'
        analysis = get_password_analysis(sample_password)
        
        print(f'Sample API response for "{sample_password}":')
        print(f'  strength: {int(analysis.strength)}')
        print(f'  score: {analysis.score}')
        print(f'  is_valid: {analysis.is_valid}')
        print(f'  strength_label: {analysis.strength.name}')
        print(f'  requirements_met: {sum(analysis.meets_requirements.values())}/{len(analysis.meets_requirements)}')

if __name__ == '__main__':
    test_valid_passwords()
