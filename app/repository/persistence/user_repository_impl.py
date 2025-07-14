from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.models.user_model import User
from app.domain.user.user_schema import UserQueryParams
from app.repository.user_repository import UserRepository

class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self, params: UserQueryParams) -> list[User]:
        offset = (params.page - 1) * params.size
        stmt = (
            select(User)
            .options(selectinload(User.role))
            .where(User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(params.size)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_users(self, params: UserQueryParams) -> int:
        count_stmt = select(func.count()).select_from(
            select(User).where(User.deleted_at.is_(None)).subquery()
        )
        result = await self.db.execute(count_stmt)
        return result.scalar_one()

    async def get_user_with_role(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user: User) -> None:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

    async def delete_user(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
