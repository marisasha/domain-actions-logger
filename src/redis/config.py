import json
from typing import Optional, Any, Union
import redis.asyncio as redis
from redis.asyncio import Redis
from src.config import settings


class RedisService:
    def __init__(self):
        self.redis_client: Optional[Redis] = None

    async def connect(self):
        """Подключение к Redis"""
        self.redis_client = await redis.from_url(
            f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.db}",
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """Получить значение по ключу"""
        if not self.redis_client:
            return None
        value = await self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Установить значение по ключу"""
        if not self.redis_client:
            return False
        expire = expire or settings.cache.expire_seconds
        await self.redis_client.set(key, json.dumps(value, default=str), ex=expire)
        return True

    async def delete(self, key: str) -> bool:
        """Удалить ключ"""
        if not self.redis_client:
            return False
        await self.redis_client.delete(key)
        return True

    async def delete_pattern(self, pattern: str) -> int:
        """Удалить все ключи по паттерну"""
        if not self.redis_client:
            return 0
        keys = await self.redis_client.keys(pattern)
        if keys:
            return await self.redis_client.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        if not self.redis_client:
            return False
        return await self.redis_client.exists(key) > 0


redis_service = RedisService()
