"""
Test script for ingredient cache and OCR integration.

This script can be run independently to test the ingredient matching functionality.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

async def test_ingredient_integration():
    """Test the ingredient file system."""
    
    print("🔧 Testing Ingredient File System")
    print("=" * 50)
    
    # Import after path setup
    from scripts.ingredient_file_manager import (
        initialize_ingredient_file,
        get_ingredient_names,
        get_ingredient_file_status
    )
    
    # Initialize the ingredient file
    print("📥 Initializing ingredient file...")
    success = await initialize_ingredient_file()
    
    if not success:
        print("❌ Failed to initialize ingredient file")
        return
    
    # Show file stats
    status = get_ingredient_file_status()
    print(f"✅ Ingredient file initialized successfully!")
    print(f"   File path: {status['file_path']}")
    print(f"   Total ingredients: {status['ingredient_count']}")
    print(f"   Last updated: {status['last_updated']}")
    print(f"   Needs update: {status['needs_update']}")
    
    # Test ingredient retrieval
    print("\n📋 Testing ingredient retrieval from file...")
    ingredient_names = get_ingredient_names()
    print(f"   Retrieved {len(ingredient_names)} ingredient names from file")
    print(f"   Sample ingredients: {', '.join(ingredient_names[:5])}...")
    
    # Show some statistics
    print(f"\n📊 File Statistics:")
    print(f"   Total ingredients: {len(ingredient_names)}")
    print(f"   Shortest name: '{min(ingredient_names, key=len)}' ({len(min(ingredient_names, key=len))} chars)")
    print(f"   Longest name: '{max(ingredient_names, key=len)}' ({len(max(ingredient_names, key=len))} chars)")
    
    # Test simple searching (basic implementation)
    print(f"\n🔍 Testing simple ingredient searching...")
    
    search_terms = ["chicken", "tomato", "rice", "oil", "cheese"]
    
    for term in search_terms:
        matches = [name for name in ingredient_names if term.lower() in name.lower()]
        print(f"   '{term}': {len(matches)} matches")
        if matches:
            print(f"     Examples: {', '.join(matches[:3])}")
    
    print("\n🎉 Integration test completed!")


if __name__ == "__main__":
    asyncio.run(test_ingredient_integration())
