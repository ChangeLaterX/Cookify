"""
Application-wide dependencies.
"""

from typing import Optional

from fastapi import Depends
from shared.database.supabase import get_supabase_client
from supabase._sync.client import SyncClient


def get_db() -> SyncClient:
    """Get database client dependency."""
    return get_supabase_client()


__all__: list[str] = ["get_db"]
