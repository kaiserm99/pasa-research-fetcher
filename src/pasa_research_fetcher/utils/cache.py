"""Simple in-memory cache implementation"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class Cache:
    """Simple cache implementation with TTL support"""

    def __init__(self, enabled: bool = True, ttl: int = 3600):
        self.enabled = enabled
        self.ttl = ttl
        self._cache: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        if not self.enabled:
            return None

        async with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            expires_at = entry["expires_at"]

            if datetime.now() > expires_at:
                del self._cache[key]
                return None

            return entry["value"]

    async def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        if not self.enabled:
            return

        async with self._lock:
            expires_at = datetime.now() + timedelta(seconds=self.ttl)
            self._cache[key] = {"value": value, "expires_at": expires_at}

    async def clear(self) -> None:
        """Clear entire cache"""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self) -> None:
        """Remove expired entries"""
        if not self.enabled:
            return

        async with self._lock:
            now = datetime.now()
            expired_keys = [key for key, entry in self._cache.items() if now > entry["expires_at"]]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
