"""
Database configuration and initialization.
"""
from shared.database.supabase import get_supabase_client, supabase_service

__all__: list[str] = ["get_supabase_client", "supabase_service"]
