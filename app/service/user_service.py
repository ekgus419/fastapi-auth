from datetime import datetime, UTC
from app.common.exception import UserNotFoundException, IsActivePermissionException
from app.common.logger import logger
from app.db.models.user_model import User
from app.domain.user.user_schema import UserUpdateRequest, UserQueryParams, UserListResponse, UserListItem
from app.repository.user_repository import UserRepository
from app.event.user_event.user_publisher import publish_user_deleted
from app.common.redis import redis_cache
import hashlib
import json


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user(self, user_id: int, current_user: User) -> dict:
        cache_key = f"user:{user_id}"
        try:
            cached = await redis_cache.get_json(cache_key)
            if cached:
                logger.info(f"✅ Redis 캐시 HIT: {cache_key}")
                return cached
        except Exception as e:
            logger.warning(f"❌ Redis 캐시 GET 실패: {e}")

        user = await self.repo.get_user_with_role(user_id)
        if not user:
            raise UserNotFoundException()

        user_data = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.name,
        }

        try:
            await redis_cache.set(cache_key, user_data, ex=300)
            logger.info(f"✅ Redis 캐시 SET 완료: {cache_key}")
        except Exception as e:
            logger.warning(f"❌ Redis 캐시 SET 실패: {e}")

        return user_data

    async def update_user(self, user_id: int, update: UserUpdateRequest, current_user: User) -> User:
        user = await self.repo.get_user_with_role(user_id)
        if not user:
            raise UserNotFoundException()

        # 일반 사용자는 is_active 수정 금지
        if update.is_active is not None and current_user.role.name != "Admin":
            raise IsActivePermissionException()

        # 값이 있는 필드만 반영
        if update.name is not None:
            user.name = update.name

        if update.email is not None:
            user.email = update.email

        if update.is_active is not None:
            user.is_active = update.is_active

        await self.repo.update_user(user)

        try:
            await redis_cache.delete(f"user:{user_id}")
            await redis_cache.delete_pattern("users:*")
            logger.info(f"♻️ Redis 캐시 무효화 완료: user:{user_id}, users:*")
        except Exception as e:
            logger.warning(f"❌ Redis 캐시 무효화 실패: {e}")

        return user

    async def delete_user(self, user_id: int, current_user: User) -> None:
        user = await self.repo.get_user_with_role(user_id)
        if not user:
            raise UserNotFoundException()

        user.deleted_at = datetime.now(UTC)
        user.is_active = False

        await self.repo.delete_user(user)

        try:
            await redis_cache.delete(f"user:{user_id}")
            await redis_cache.delete_pattern("users:*")
            logger.info(f"♻️ Redis 캐시 무효화 완료: user:{user_id}, users:*")
        except Exception as e:
            logger.warning(f"❌ Redis 캐시 무효화 실패: {e}")

        await publish_user_deleted(user.id)

    async def get_users(self, params: UserQueryParams) -> UserListResponse:
        # ✅ 파라미터 기반 캐시 키 생성
        query_key = json.dumps(params.model_dump(), sort_keys=True)
        cache_key = f"users:{hashlib.md5(query_key.encode()).hexdigest()}"
        try:
            cached = await redis_cache.get_json(cache_key)
            if cached:
                logger.info(f"✅ Redis 캐시 HIT: {cache_key}")
                return UserListResponse(**cached)
        except Exception as e:
            logger.warning(f"❌ Redis 캐시 GET 실패: {e}")

        users = await self.repo.get_users(params)
        total = await self.repo.count_users(params)

        user_items = [
            UserListItem(
                id=u.id,
                email=u.email,
                name=u.name,
                role=u.role.name,
                is_active=u.is_active,
            )
            for u in users
        ]

        result = UserListResponse(
            total=total,
            page=params.page,
            size=params.size,
            users=user_items,
        )

        try:
            await redis_cache.set(cache_key, result.model_dump(), ex=60)
            logger.info(f"✅ Redis 캐시 SET 완료: {cache_key}")
        except Exception as e:
            logger.warning(f"❌ Redis 캐시 SET 실패: {e}")

        return result
