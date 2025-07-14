from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.auth.auth_schema import SignupRequest, SigninRequest, TokenResponse
from app.db.session import get_db_session
from app.repository.persistence.auth_repository_impl import AuthRepositoryImpl
from app.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", status_code=201)
async def signup(
    data: SignupRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    👤 회원가입 API

    - 이메일, 비밀번호, 이름을 입력받아 신규 사용자를 등록합니다.
    - 이메일 중복 시 409 Conflict 예외를 반환합니다.
    - 가입 후 토큰은 발급하지 않으며, `/signin`을 통해 로그인해야 합니다.

    📥 Request Body:
    - email: 사용자 이메일 (필수)
    - password: 비밀번호 (bcrypt 해시되어 저장됨)
    - name: 사용자 이름 (선택)

    📤 Response:
    - 201 Created
    - {"message": "회원가입이 완료되었습니다."}
    """
    repo = AuthRepositoryImpl(db)
    service = AuthService(repo)
    await service.signup(data)
    return {"message": "회원가입이 완료되었습니다."}


@router.post("/signin", response_model=TokenResponse)
async def signin(
    data: SigninRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    🔐 로그인 API

    - 이메일/비밀번호를 기반으로 로그인 후 JWT 토큰을 발급합니다.
    - 비밀번호 불일치 또는 존재하지 않는 이메일일 경우 401 Unauthorized 반환합니다.

    📥 Request Body:
    - email: 사용자 이메일
    - password: 비밀번호

    📤 Response:
    - 200 OK
    - {
        "access_token": "...",
        "refresh_token": "..."
      }
    """
    repo = AuthRepositoryImpl(db)
    service = AuthService(repo)
    return await service.signin(data)
