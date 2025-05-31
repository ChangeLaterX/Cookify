from supabase import create_client, Client
from core.config import settings
from typing import Optional


class SupabaseService:
    """Service-Klasse für Supabase-Operationen."""
    
    def __init__(self):
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Lazy Loading des Supabase-Clients."""
        if self._client is None:
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
        return self._client
    
    def get_client(self) -> Client:
        """Gibt den Supabase-Client zurück."""
        return self.client


# Globale Service-Instanz
supabase_service = SupabaseService()

# Convenience function for backward compatibility
def get_supabase_client() -> Client:
    """Get the Supabase client instance."""
    return supabase_service.client