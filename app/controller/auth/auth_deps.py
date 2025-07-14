from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exception import AccessDeniedException, UserNotFoundException, InvalidTokenException, \
    AdminPermissionRequiredException
from app.common.jwt_utils import decode_token
from app.db.session import get_db_session
from app.db.models.user_model import User
from sqlalchemy import select

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        raise InvalidTokenException()

    user_id = int(payload["sub"])
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UserNotFoundException()

    return user

def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name != "Admin":
        raise AdminPermissionRequiredException()
    return current_user

def self_or_admin_required(user_id: int, current_user: User = Depends(get_current_user)) -> User:
    role_name = getattr(current_user.role, "name", None)
    if role_name != "Admin" and current_user.id != user_id:
        raise AccessDeniedException()
    return current_user