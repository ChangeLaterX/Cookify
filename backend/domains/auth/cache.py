"""
Efficient user caching system with async support and better memory management.
"""
import asyncio
import time
import logging
from typing import Dict, Optional, Set, Any
from contextlib import asynccontextmanager
from dataclasses import dataclass

from domains.auth.schemas import User
from domains.auth.types import IUserCache, CacheOperationResult
from core.config import settings

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    user: User
    created_at: float
    last_accessed: float
    access_count: int = 0
    
    def is_expired(self, ttl: int) -> bool:
        """Check if entry is expired."""
        return time.time() - self.created_at > ttl
    
    def touch(self) -> None:
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1


class AsyncUserCache(IUserCache):
    """High-performance async user cache with automatic cleanup."""
    
    def __init__(self, ttl: Optional[int] = None, max_size: int = 1000, cleanup_interval: int = 300):
        self._cache: Dict[str, CacheEntry] = {}
        self._ttl: int = ttl or settings.user_cache_ttl_seconds
        self._max_size: int = max_size
        self._enabled: bool = settings.enable_user_cache
        self._cleanup_interval: int = cleanup_interval
        self._lock: asyncio.Lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._user_tokens: Dict[str, Set[str]] = {}
        self._initialized: bool = False

        # Don't start cleanup task during init - will be started on first use
    
    def _ensure_initialized(self) -> None:
        """Ensure the cache is initialized with cleanup task."""
        if not self._initialized and self._enabled:
            try:
                # Only start cleanup task if we have a running event loop
                loop = asyncio.get_running_loop()
                if loop and not loop.is_closed():
                    self._start_cleanup_task()
                    self._initialized = True
            except RuntimeError:
                # No running event loop, will initialize later
                pass
    
    def _start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
    
    async def _background_cleanup(self) -> None:
        """Background task to clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background cleanup: {e}")
    
    async def _cleanup_expired(self) -> int:
        """Remove expired entries from cache."""
        if not self._enabled:
            return 0
        
        async with self._lock:
            current_time: float = time.time()
            expired_tokens: list[str] = [
                token for token, entry in self._cache.items()
                if current_time - entry.created_at > self._ttl
            ]
            
            for token in expired_tokens:
                entry: CacheEntry | None = self._cache.pop(token, None)
                if entry:
                    # Remove from user_tokens mapping
                    user_id = entry.user.id
                    if user_id in self._user_tokens:
                        self._user_tokens[user_id].discard(token)
                        if not self._user_tokens[user_id]:
                            del self._user_tokens[user_id]
            
            # Also enforce max size by removing least recently used entries
            if len(self._cache) > self._max_size:
                # Sort by last_accessed time and remove oldest
                sorted_entries: list[tuple[str, CacheEntry]] = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].last_accessed
                )
                
                excess_count: int = len(self._cache) - self._max_size
                for token, entry in sorted_entries[:excess_count]:
                    self._cache.pop(token, None)
                    user_id = entry.user.id
                    if user_id in self._user_tokens:
                        self._user_tokens[user_id].discard(token)
                        if not self._user_tokens[user_id]:
                            del self._user_tokens[user_id]
            
            if expired_tokens:
                logger.debug(f"Cleaned up {len(expired_tokens)} expired cache entries")
            
            return len(expired_tokens)
    
    async def get(self, token: str) -> Optional[User]:
        """Get user from cache if not expired."""
        if not self._enabled:
            return None
        
        self._ensure_initialized()
        
        async with self._lock:
            entry: CacheEntry | None = self._cache.get(token)
            if not entry:
                return None
            
            if entry.is_expired(self._ttl):
                # Remove expired entry
                self._cache.pop(token, None)
                user_id = entry.user.id
                if user_id in self._user_tokens:
                    self._user_tokens[user_id].discard(token)
                    if not self._user_tokens[user_id]:
                        del self._user_tokens[user_id]
                
                logger.debug("Cache entry expired")
                return None
            
            entry.touch()
            email: str | None = entry.user.email
            if email:
                logger.debug(f"Cache hit for user {email[:3]}***")
            else:
                logger.debug("Cache hit for user")
            return entry.user
    
    async def set(self, token: str, user: User) -> None:
        """Store user in cache."""
        if not self._enabled:
            return
        
        self._ensure_initialized()
        
        async with self._lock:
            # Create new cache entry
            entry = CacheEntry(
                user=user,
                created_at=time.time(),
                last_accessed=time.time()
            )
            
            self._cache[token] = entry
            
            # Update user_tokens mapping
            user_id: str = user.id
            if user_id not in self._user_tokens:
                self._user_tokens[user_id] = set()
            self._user_tokens[user_id].add(token)
            
            logger.debug(f"Cached user {user.email[:3] + '***' if user.email else 'unknown'}")
            
            # Check if we need to cleanup to maintain max size
            if len(self._cache) > self._max_size:
                await self._cleanup_expired()
    
    async def invalidate(self, token: str) -> None:
        """Remove user from cache."""
        if not self._enabled:
            return
        
        self._ensure_initialized()
        
        async with self._lock:
            entry: CacheEntry | None = self._cache.pop(token, None)
            if entry:
                user_id: str = entry.user.id
                if user_id in self._user_tokens:
                    self._user_tokens[user_id].discard(token)
                    if not self._user_tokens[user_id]:
                        del self._user_tokens[user_id]
                
                logger.debug(f"Invalidated cache for user {entry.user.email[:3] + '***' if entry.user.email else 'unknown'}")
    
    async def invalidate_user(self, user_id: str) -> None:
        """Remove all cache entries for a specific user."""
        if not self._enabled:
            return
        
        async with self._lock:
            tokens_to_remove: set[str] = self._user_tokens.get(user_id, set()).copy()

            for token in tokens_to_remove:
                self._cache.pop(token, None)
            
            if user_id in self._user_tokens:
                del self._user_tokens[user_id]
            
            if tokens_to_remove:
                logger.debug(f"Invalidated {len(tokens_to_remove)} cache entries for user {user_id}")
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        if not self._enabled:
            return
        
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._user_tokens.clear()
            logger.debug(f"Cleared {count} cache entries")
    
    async def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self._enabled:
            return {"enabled": False, "size": 0, "expired": 0}
        
        async with self._lock:
            current_time: float = time.time()
            expired_count: int = sum(
                1 for entry in self._cache.values()
                if current_time - entry.created_at > self._ttl
            )

            total_accesses: int = sum(entry.access_count for entry in self._cache.values())

            return {
                "enabled": True,
                "size": len(self._cache),
                "expired": expired_count,
                "ttl_seconds": self._ttl,
                "max_size": self._max_size,
                "total_accesses": total_accesses,
                "unique_users": len(self._user_tokens)
            }
    
    async def cleanup(self) -> None:
        """Manual cleanup trigger."""
        await self._cleanup_expired()
    
    def shutdown(self) -> None:
        """Shutdown cache and cleanup resources."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


# Global cache instance
user_cache = AsyncUserCache()


@asynccontextmanager
async def cache_context():
    """Context manager for cache operations with automatic cleanup."""
    try:
        yield user_cache
    finally:
        await user_cache.cleanup()


async def get_cache_stats() -> Dict[str, Any]:
    """Get current cache statistics."""
    return await user_cache.stats()
