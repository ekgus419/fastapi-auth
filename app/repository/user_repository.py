from abc import ABC, abstractmethod
from app.db.models.user_model import User
from app.domain.user.user_schema import UserQueryParams
from typing import Optional

class UserRepository(ABC):

    @abstractmethod
    async def get_users(self, params: UserQueryParams) -> list[User]:
        pass

    @abstractmethod
    async def count_users(self, params: UserQueryParams) -> int:
        pass

    @abstractmethod
    async def get_user_with_role(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def update_user(self, user: User) -> None:
        pass

    @abstractmethod
    async def delete_user(self, user: User) -> None:
        pass
