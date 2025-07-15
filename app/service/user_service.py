from datetime import datetime, UTC
from app.common.exception import UserNotFoundException, IsActivePermissionException
from app.common.logger import logger
from app.db.models.user_model import User
from app.domain.user.user_schema import UserUpdateRequest, UserQueryParams, UserListResponse, UserListItem
from app.repository.user_repository import UserRepository
from app.event.user_event.user_publisher import publish_user_deleted
from app.common.redis import redis_cache
from app.common.redis_utils import (
    safe_redis_get,
    safe_redis_set,
    safe_redis_delete,
    safe_redis_delete_pattern,
)
import hashlib
import json


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user(self, user_id: int, current_user: User) -> dict:
        cache_key = f"user:{user_id}"
        cached = await safe_redis_get(redis_cache, cache_key)
        if cached:
            return cached

        user = await self.repo.get_user_with_role(user_id)
        if not user:
            raise UserNotFoundException()

        user_data = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.name,
        }

        await safe_redis_set(redis_cache, cache_key, user_data, ex=300)
        return user_data

    async def update_user(self, user_id: int, update: UserUpdateRequest, current_user: User) -> User:
        user = await self.repo.get_user_with_role(user_id)
        if not user:
            raise UserNotFoundException()

        if update.is_active is not None and current_user.role.name != "Admin":
            raise IsActivePermissionException()

        if update.name is not None:
            user.name = update.name
        if update.email is not None:
            user.email = update.email
        if update.is_active is not None:
            user.is_active = update.is_active

        await self.repo.update_user(user)
        await safe_redis_delete(redis_cache, f"user:{user_id}")
        await safe_redis_delete_pattern(redis_cache, "users:*")
        return user

    async def delete_user(self, user_id: int, current_user: User) -> None:
        user = await self.repo.get_user_with_role(user_id)
        if not user:
            raise UserNotFoundException()

        user.deleted_at = datetime.now(UTC)
        user.is_active = False

        await self.repo.delete_user(user)
        await safe_redis_delete(redis_cache, f"user:{user_id}")
        await safe_redis_delete_pattern(redis_cache, "users:*")
        await publish_user_deleted(user.id)

    async def get_users(self, params: UserQueryParams) -> UserListResponse:
        query_key = json.dumps(params.model_dump(), sort_keys=True)
        cache_key = f"users:{hashlib.md5(query_key.encode()).hexdigest()}"
        cached = await safe_redis_get(redis_cache, cache_key)
        if cached:
            return UserListResponse(**cached)

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

        await safe_redis_set(redis_cache, cache_key, result.model_dump(), ex=60)
        return result
