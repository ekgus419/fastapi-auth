import pytest
from fastapi import HTTPException

# 사용자 정보 수정 성공 케이스
@pytest.mark.asyncio
async def test_update_user_success():
    # Given: 기존 사용자와 수정 요청 정보 설정
    user = User(id=1, email="old@example.com", name="Old Name", is_active=True, role=Role(name="Member"))
    repo = AsyncMock()
    repo.get_user_with_role.return_value = user
    repo.update_user.return_value = None

    service = UserService(repo)
    update = UserUpdateRequest(name="New Name", email="new@example.com")
    requester = User(id=1, role=Role(name="Member"))  # 본인 요청

    # When: 사용자 정보 수정 요청
    updated = await service.update_user(user_id=1, update=update, current_user=requester)

    # Then: 이름과 이메일이 업데이트되고, 저장 메서드 호출됨
    assert updated.name == "New Name"
    assert updated.email == "new@example.com"
    repo.update_user.assert_called_once()

# 일반 사용자가 is_active 필드를 수정하려고 하면 거부되는 케이스
@pytest.mark.asyncio
async def test_update_user_is_active_rejected_for_member():
    # Given: 일반 사용자(Member)로 로그인, is_active 수정 요청
    user = User(id=1, email="a@example.com", name="a", is_active=True, role=Role(name="Member"))
    repo = AsyncMock()
    repo.get_user_with_role.return_value = user

    service = UserService(repo)
    requester = User(id=1, role=Role(name="Member"))
    update = UserUpdateRequest(is_active=False)

    # When / Then: 수정 시도 시 403 예외 발생
    with pytest.raises(HTTPException) as e:
        await service.update_user(user_id=1, update=update, current_user=requester)

    assert e.value.status_code == 403
    assert "is_active는 Admin만 수정할 수 있습니다." in str(e.value.detail)

# 사용자 리스트 조회 성공 (페이징 처리 포함)
@pytest.mark.asyncio
async def test_get_users_returns_paginated_result():
    # Given: 사용자 목록이 1개 있고, 전체 카운트도 1
    repo = AsyncMock()
    mock_user = User(id=1, email="a@example.com", name="a", is_active=True, role=Role(name="Member"))
    repo.get_users.return_value = [mock_user]
    repo.count_users.return_value = 1

    service = UserService(repo)
    params = UserQueryParams(page=1, size=10)

    # When: 사용자 목록 요청
    result = await service.get_users(params)

    # Then: 총 1명, 페이지 1, 크기 10, 사용자 정보 확인
    assert result.total == 1
    assert result.page == 1
    assert result.size == 10
    assert result.users[0].email == "a@example.com"

# 캐시 미스 시 DB 조회 후 Redis에 저장되는 동작 테스트
@pytest.mark.asyncio
async def test_get_user_cache_miss_then_store():
    # Given: 캐시에는 사용자 정보가 없고, DB에는 존재하는 사용자
    user = User(id=3, email="miss@example.com", name="Miss", role=Role(name="Member"))
    repo = AsyncMock()
    repo.get_user_with_role.return_value = user
    service = UserService(repo)
    current_user = User(id=1, role=Role(name="Admin"))  # 관리자 권한으로 조회

    with patch("app.common.redis.redis_cache.get_json", return_value=None) as mock_get, \
         patch("app.common.redis.redis_cache.set", new_callable=AsyncMock) as mock_set:

        # When: 사용자 조회 요청 (캐시에 없으므로 DB 조회 후 캐시에 저장)
        result = await service.get_user(user_id=3, current_user=current_user)

        # Then: 올바른 사용자 정보가 반환되고, 캐시 조회 및 저장 함수가 호출됨
        assert result["id"] == 3
        assert result["email"] == "miss@example.com"
        mock_get.assert_awaited_once()   # 캐시에서 한 번 조회
        mock_set.assert_awaited_once()   # 캐시에 한 번 저장

import pytest
from unittest.mock import AsyncMock, patch
from app.service.user_service import UserService
from app.db.models.user_model import User, Role
from app.domain.user.user_schema import UserUpdateRequest, UserQueryParams

# 단일 사용자 조회 시 캐시 히트 케이스
@pytest.mark.asyncio
async def test_get_user_cache_hit():
    # Given: 캐시에 사용자 데이터가 이미 존재함
    fake_data = {
        "id": 2,
        "email": "cached@example.com",
        "name": "Cached User",
        "role": "Member",
    }
    repo = AsyncMock()
    service = UserService(repo)
    current_user = User(id=99, role=Role(name="Admin"))

    # When: 사용자 조회 요청
    with patch("app.common.redis.redis_cache.get_json", return_value=fake_data) as mock_cache:
        result = await service.get_user(user_id=2, current_user=current_user)

        # Then: 캐시에서 데이터를 받아오고, DB는 호출되지 않음
        assert result == fake_data
        mock_cache.assert_awaited_once()
        repo.get_user_with_role.assert_not_called()

# 사용자 목록 조회 시 캐시 히트 케이스
@pytest.mark.asyncio
async def test_get_users_cache_hit():
    from app.domain.user.user_schema import UserListResponse

    # Given: 사용자 리스트가 캐시에 존재함
    fake_result = UserListResponse(
        total=1,
        page=1,
        size=10,
        users=[{
            "id": 1,
            "email": "cached@example.com",
            "name": "Cached User",
            "role": "Member",
            "is_active": True
        }]
    )

    repo = AsyncMock()
    service = UserService(repo)
    params = UserQueryParams(page=1, size=10)

    # When: 사용자 리스트 조회 요청
    with patch("app.common.redis.redis_cache.get_json", return_value=fake_result.model_dump()) as mock_cache:
        result = await service.get_users(params)

        # Then: 캐시에서 결과가 반환되고, DB는 호출되지 않음
        assert result.total == 1
        assert result.users[0].email == "cached@example.com"
        mock_cache.assert_awaited_once()
        repo.get_users.assert_not_awaited()

# 사용자 정보 업데이트 시 캐시 무효화 확인
@pytest.mark.asyncio
async def test_update_user_cache_invalidation():
    # Given: 기존 사용자와 업데이트 요청 존재
    user = User(id=10, email="u@example.com", name="U", is_active=True, role=Role(name="Member"))
    repo = AsyncMock()
    repo.get_user_with_role.return_value = user
    repo.update_user.return_value = None

    service = UserService(repo)
    update = UserUpdateRequest(name="Updated Name")
    current_user = User(id=10, role=Role(name="Admin"))

    # When: 사용자 정보 업데이트
    with patch("app.common.redis.redis_cache.delete", new_callable=AsyncMock) as mock_delete, \
         patch("app.common.redis.redis_cache.delete_pattern", new_callable=AsyncMock) as mock_delete_pattern:

        await service.update_user(user_id=10, update=update, current_user=current_user)

        # Then: 단일 사용자 및 사용자 목록 캐시 무효화 함수 호출
        mock_delete.assert_awaited_once_with("user:10")
        mock_delete_pattern.assert_awaited_once_with("users:*")

# 사용자 삭제 시 캐시 삭제 및 이벤트 발행이 수행되는지 확인
@pytest.mark.asyncio
async def test_delete_user_cache_invalidation():
    # Given: 삭제 대상 사용자, 삭제 요청자(Admin), Mock Repository 구성
    user = User(id=20, email="x@example.com", name="X", is_active=True, role=Role(name="Member"))
    repo = AsyncMock()
    repo.get_user_with_role.return_value = user
    repo.delete_user.return_value = None

    service = UserService(repo)
    current_user = User(id=1, role=Role(name="Admin"))  # 관리자 권한 요청자

    # When: 사용자 삭제 요청 실행
    with patch("app.common.redis.redis_cache.delete", new_callable=AsyncMock) as mock_delete, \
         patch("app.common.redis.redis_cache.delete_pattern", new_callable=AsyncMock) as mock_delete_pattern, \
         patch("app.service.user_service.publish_user_deleted", new_callable=AsyncMock) as mock_event:

        await service.delete_user(user_id=20, current_user=current_user)

        # Then:
        # - 개별 사용자 캐시 삭제
        # - 사용자 목록 캐시 삭제 (패턴 기반)
        # - 사용자 삭제 이벤트 발행
        mock_delete.assert_awaited_once_with("user:20")
        mock_delete_pattern.assert_awaited_once_with("users:*")
        mock_event.assert_awaited_once_with(20)


