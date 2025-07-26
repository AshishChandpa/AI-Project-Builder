import json
import asyncio
from typing import Optional, Any, Dict
from datetime import timedelta
import logging

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from config.settings import settings

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Fallback in-memory cache when Redis is not available"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        logger.info("Using in-memory cache (Redis not available)")

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        import time

        if key in self._expiry and time.time() > self._expiry[key]:
            # Key expired
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
            return None

        return self._cache.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in cache"""
        self._cache[key] = value

        if ex:
            import time
            self._expiry[key] = time.time() + ex

        return True

    async def setex(self, key: str, time: int, value: str) -> bool:
        """Set value with expiration"""
        return await self.set(key, value, ex=time)

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        return True

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        value = await self.get(key)
        return value is not None

    async def flushdb(self) -> bool:
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
        return True


class RedisClient:
    """Redis client with automatic fallback to in-memory cache"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.fallback_cache = InMemoryCache()
        self.use_redis = False

        # Only try Redis if explicitly enabled and available
        if REDIS_AVAILABLE and settings.REDIS_ENABLED and settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    retry_on_timeout=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                self.use_redis = True
                logger.info(f"Redis client initialized: {settings.REDIS_URL}")
            except Exception as e:
                logger.warning(f"Redis initialization failed, using in-memory cache: {e}")
                self.use_redis = False
        else:
            logger.info("Redis disabled or not configured, using in-memory cache")

    async def _ensure_connection(self) -> bool:
        """Ensure Redis connection is working"""
        if not self.use_redis or not self.redis_client:
            return False

        try:
            await asyncio.wait_for(self.redis_client.ping(), timeout=2.0)
            return True
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to in-memory: {e}")
            self.use_redis = False  # Disable Redis for this session
            return False

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if await self._ensure_connection():
            try:
                return await self.redis_client.get(key)
            except Exception as e:
                logger.error(f"Redis GET error: {e}")

        # Fallback to in-memory cache
        return await self.fallback_cache.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in cache"""
        if await self._ensure_connection():
            try:
                result = await self.redis_client.set(key, value, ex=ex)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis SET error: {e}")

        # Fallback to in-memory cache
        return await self.fallback_cache.set(key, value, ex=ex)

    async def setex(self, key: str, time: int, value: str) -> bool:
        """Set value with expiration"""
        if await self._ensure_connection():
            try:
                result = await self.redis_client.setex(key, time, value)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis SETEX error: {e}")

        # Fallback to in-memory cache
        return await self.fallback_cache.setex(key, time, value)

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if await self._ensure_connection():
            try:
                result = await self.redis_client.delete(key)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis DELETE error: {e}")

        # Fallback to in-memory cache
        return await self.fallback_cache.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if await self._ensure_connection():
            try:
                result = await self.redis_client.exists(key)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis EXISTS error: {e}")

        # Fallback to in-memory cache
        return await self.fallback_cache.exists(key)

    async def flushdb(self) -> bool:
        """Clear all cache (use with caution)"""
        if await self._ensure_connection():
            try:
                await self.redis_client.flushdb()
                return True
            except Exception as e:
                logger.error(f"Redis FLUSHDB error: {e}")

        # Fallback to in-memory cache
        return await self.fallback_cache.flushdb()

    async def health_check(self) -> Dict[str, Any]:
        """Health check for cache system"""
        if await self._ensure_connection():
            try:
                await self.redis_client.ping()
                return {
                    "cache_type": "redis",
                    "status": "healthy",
                    "redis_available": True,
                    "redis_url": settings.REDIS_URL
                }
            except Exception as e:
                return {
                    "cache_type": "in_memory",
                    "status": "healthy_fallback",
                    "redis_available": False,
                    "error": str(e)
                }

        return {
            "cache_type": "in_memory",
            "status": "healthy",
            "redis_available": False,
            "redis_enabled": settings.REDIS_ENABLED
        }
