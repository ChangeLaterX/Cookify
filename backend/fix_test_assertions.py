#!/usr/bin/env python3
"""
Script to fix test assertions to use the correct API response format.
Changes "detail" to "message" and adds proper list type checking.
"""
import os
import re
from pathlib import Path

def fix_test_file(file_path):
    """Fix assertions in a single test file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Replace 'assert "detail" in data' with proper message assertion
    pattern1 = r'assert "detail" in data'
    replacement1 = 'assert "message" in data\n        assert isinstance(data["message"], list)'
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: Handle cases where there might be additional assertions after detail
    pattern2 = r'assert "detail" in data\s*\n\s*assert.*"detail".*'
    matches = re.findall(pattern2, content)
    for match in matches:
        new_assertion = 'assert "message" in data\n        assert isinstance(data["message"], list)'
        content = content.replace(match, new_assertion)
    
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Fixed {file_path}")
        return True
    else:
        print(f"⏭️  No changes needed in {file_path}")
        return False

def main():
    """Fix all test files in the auth directory."""
    test_dir = Path("/Users/jannis/Developer/Cookify/backend/tests/auth")
    
    files_fixed = 0
    total_files = 0
    
    for test_file in test_dir.glob("test_*.py"):
        if test_file.name == "test_register.py":
            print(f"⏭️  Skipping {test_file} (already fixed)")
            continue
            
        total_files += 1
        if fix_test_file(test_file):
            files_fixed += 1
    
    print(f"\n📊 Summary:")
    print(f"   Total files processed: {total_files}")
    print(f"   Files fixed: {files_fixed}")
    print(f"   Files unchanged: {total_files - files_fixed}")

if __name__ == "__main__":
    main()
