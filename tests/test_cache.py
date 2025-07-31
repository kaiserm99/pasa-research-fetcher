"""Test cache functionality"""

import asyncio

import pytest

from pasa_research_fetcher.utils.cache import Cache


class TestCache:
    """Test Cache functionality"""

    @pytest.mark.asyncio
    async def test_cache_disabled(self):
        """Test cache when disabled"""
        cache = Cache(enabled=False)

        await cache.set("key1", "value1")
        result = await cache.get("key1")

        assert result is None

    @pytest.mark.asyncio
    async def test_cache_basic_operations(self):
        """Test basic cache operations"""
        cache = Cache(enabled=True, ttl=10)

        # Test set and get
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

        # Test non-existent key
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        cache = Cache(enabled=True, ttl=1)  # 1 second TTL

        await cache.set("key1", "value1")

        # Should exist immediately
        result = await cache.get("key1")
        assert result == "value1"

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be expired
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_clear(self):
        """Test cache clear operation"""
        cache = Cache(enabled=True, ttl=60)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        # Verify items exist
        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == "value2"

        # Clear cache
        await cache.clear()

        # Verify items are gone
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_cache_complex_objects(self):
        """Test caching complex objects"""
        cache = Cache(enabled=True, ttl=60)

        complex_obj = {"list": [1, 2, 3], "dict": {"nested": "value"}, "string": "test"}

        await cache.set("complex", complex_obj)
        result = await cache.get("complex")

        assert result == complex_obj
        assert result["list"] == [1, 2, 3]
        assert result["dict"]["nested"] == "value"

    @pytest.mark.asyncio
    async def test_cache_cleanup_expired(self):
        """Test cleanup of expired entries"""
        cache = Cache(enabled=True, ttl=1)

        # Add multiple items
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Add new item (shouldn't be expired)
        await cache.set("key3", "value3")

        # Trigger cleanup
        await cache.cleanup_expired()

        # Only key3 should exist
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
        assert await cache.get("key3") == "value3"
