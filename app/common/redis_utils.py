from app.common.logger import logger

async def safe_redis_get(redis, key: str):
    try:
        value = await redis.get_json(key)
        if value:
            logger.info(f"✅ Redis 캐시 HIT: {key}")
        return value
    except Exception as e:
        logger.warning(f"❌ Redis 캐시 GET 실패: {e}")
        return None

async def safe_redis_set(redis, key: str, value, ex: int = 300):
    try:
        await redis.set(key, value, ex=ex)
        logger.info(f"✅ Redis 캐시 SET 완료: {key}")
    except Exception as e:
        logger.warning(f"❌ Redis 캐시 SET 실패: {e}")

async def safe_redis_delete(redis, key: str):
    try:
        await redis.delete(key)
        logger.info(f"♻️ Redis 캐시 삭제 완료: {key}")
    except Exception as e:
        logger.warning(f"❌ Redis 캐시 삭제 실패: {e}")

async def safe_redis_delete_pattern(redis, pattern: str):
    try:
        await redis.delete_pattern(pattern)
        logger.info(f"♻️ Redis 캐시 패턴 삭제 완료: {pattern}")
    except Exception as e:
        logger.warning(f"❌ Redis 캐시 패턴 삭제 실패: {e}")
