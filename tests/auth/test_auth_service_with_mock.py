import pytest
from unittest.mock import AsyncMock
from app.service.auth_service import AuthService
from app.db.models.user_model import User, Role
from app.domain.auth.auth_schema import SignupRequest, SigninRequest
from app.common.security import hash_password

# 회원가입 성공 케이스 테스트
@pytest.mark.asyncio
async def test_signup_success():
    # Given: 사용자 정보가 존재하지 않고, 기본 역할(Role)이 반환됨
    repo = AsyncMock()
    repo.get_user_by_email.return_value = None
    repo.get_member_role.return_value = Role(id=1, name="Member")
    repo.create_user.return_value = None

    service = AuthService(repo)
    signup_data = SignupRequest(
        email="test@example.com",
        password="securepass",
        name="Test User"
    )

    # When: 회원가입 요청
    await service.signup(signup_data)

    # Then: 올바르게 저장 메서드들이 호출되고, 비밀번호는 해시 처리되어야 함
    repo.get_user_by_email.assert_called_once_with("test@example.com")
    repo.get_member_role.assert_called_once()
    repo.create_user.assert_called_once()
    assert repo.create_user.call_args[0][0].password != "securepass"

# 중복 이메일로 회원가입 실패 케이스
@pytest.mark.asyncio
async def test_signup_duplicate_email():
    # Given: 이미 존재하는 이메일이 조회됨
    repo = AsyncMock()
    repo.get_user_by_email.return_value = User(email="test@example.com")

    service = AuthService(repo)
    signup_data = SignupRequest(
        email="test@example.com",
        password="securepass",
        name="Test User"
    )

    # When / Then: 예외 발생 (중복 이메일)
    with pytest.raises(Exception) as e:
        await service.signup(signup_data)

    assert "이미 등록된 이메일입니다." in str(e.value)

# 로그인 성공 케이스
@pytest.mark.asyncio
async def test_signin_success():
    # Given: 올바른 비밀번호를 가진 사용자 정보가 존재함
    raw_password = "mypassword"
    hashed_password = hash_password(raw_password)
    user = User(
        id=1,
        email="loginuser@example.com",
        password=hashed_password,
        name="Test",
        role=Role(name="Member")
    )

    repo = AsyncMock()
    repo.get_user_by_email.return_value = user

    service = AuthService(repo)
    signin_data = SigninRequest(email="loginuser@example.com", password=raw_password)

    # When: 로그인 요청
    result = await service.signin(signin_data)

    # Then: 토큰이 포함된 응답 반환
    assert "access_token" in result.model_dump()
    assert "refresh_token" in result.model_dump()

# 로그인 실패 - 비밀번호 불일치
@pytest.mark.asyncio
async def test_signin_wrong_password():
    # Given: 존재하는 사용자지만 비밀번호는 잘못됨
    hashed_password = "$2b$12$4h3khjkf9gZkU5Yx.A8ghOy5ZVjLOf45MQxgVoOp0IEvL/b9jDK6W"
    user = User(
        id=1,
        email="wrongpass@example.com",
        password=hashed_password,
        name="Wrong",
        role=Role(name="Member")
    )

    repo = AsyncMock()
    repo.get_user_by_email.return_value = user

    service = AuthService(repo)
    signin_data = SigninRequest(
        email="wrongpass@example.com",
        password="wrongpass"
    )

    # When / Then: 로그인 시도 시 예외 발생
    with pytest.raises(Exception) as e:
        await service.signin(signin_data)

    assert "이메일 또는 비밀번호가 일치하지 않습니다." in str(e.value)
