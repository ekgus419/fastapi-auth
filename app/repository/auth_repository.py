from abc import ABC, abstractmethod
from app.db.models.user_model import User, Role

class AuthRepository(ABC):

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_member_role(self) -> Role:
        pass

    @abstractmethod
    async def create_user(self, user: User) -> None:
        pass
