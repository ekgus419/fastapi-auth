from app.common.exception import InvalidEmailOrPasswordException, EmailAlreadyExistsException
from app.domain.auth.auth_schema import SignupRequest, SigninRequest, TokenResponse
from app.common.security import hash_password, verify_password
from app.common.jwt_utils import create_access_token, create_refresh_token
from app.repository.auth_repository import AuthRepository
from app.db.models.user_model import User


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    async def signup(self, data: SignupRequest) -> None:
        if await self.repo.get_user_by_email(data.email):
            raise EmailAlreadyExistsException()

        role = await self.repo.get_member_role()
        user = User(
            email=data.email,
            password=hash_password(data.password),
            name=data.name,
            role_id=role.id
        )
        await self.repo.create_user(user)

    async def signin(self, data: SigninRequest) -> TokenResponse:
        user = await self.repo.get_user_by_email(data.email)
        if not user or not verify_password(data.password, user.password):
            raise InvalidEmailOrPasswordException()

        return TokenResponse(
            access_token=create_access_token({"sub": str(user.id)}),
            refresh_token=create_refresh_token({"sub": str(user.id)})
        )
