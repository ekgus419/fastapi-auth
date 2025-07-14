from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_model import User, Role
from app.repository.auth_repository import AuthRepository

class AuthRepositoryImpl(AuthRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_member_role(self) -> Role:
        result = await self.db.execute(select(Role).where(Role.name == "Member"))
        return result.scalar_one()

    async def create_user(self, user: User) -> None:
        self.db.add(user)
        await self.db.commit()
