import redis.asyncio as redis
import json

from app.common.config import settings

# 환경변수에서 Redis 호스트/포트 로드
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT

class RedisCache:
    def __init__(self):
        self._redis = redis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}",
            encoding="utf-8",
            decode_responses=True
        )

    async def get(self, key: str):
        return await self._redis.get(key)

    async def set(self, key: str, value, ex: int = 300):
        val = value if isinstance(value, str) else json.dumps(value)
        await self._redis.set(key, val, ex=ex)

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def delete_pattern(self, pattern: str):
        async for key in self._redis.scan_iter(match=pattern):
            await self._redis.delete(key)

    async def get_json(self, key: str):
        data = await self.get(key)
        return json.loads(data) if data else None

# 전역 인스턴스
redis_cache = RedisCache()
