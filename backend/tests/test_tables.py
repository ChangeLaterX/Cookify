#!/usr/bin/env python3
"""
Test script to check available tables in Supabase
"""
import sys
import os
from typing import Dict, Any

from postgrest.base_request_builder import APIResponse
from supabase._sync.client import SyncClient

# Add the app directory to Python path
sys.path.append('/home/cipher/dev/coding/test/backend')

from core.database import supabase_service

def test_tables() -> None:
    """Test available tables and their contents."""
    client: SyncClient = supabase_service.client
    
    # List of tables to test
    tables: list[str] = ['preferences', 'recipes', 'pantry_items', 'meal_plans', 'saved_recipes', 'shopping_lists']
    
    print("🔍 Testing Supabase tables:")
    print("=" * 50)
    
    for table in tables:
        try:
            response: APIResponse[Dict[str, Any]] = client.table(table).select("*").limit(5).execute()
            print(f"✅ {table}: {len(response.data)} entries found")
            if response.data:
                print(f"   First entries: {response.data[:2]}")
            print()
        except Exception as e:
            print(f"❌ {table}: Error - {str(e)}")
            print()

if __name__ == "__main__":
    test_tables()
