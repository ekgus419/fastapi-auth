import pytest
from unittest.mock import AsyncMock, patch
from app.service.user_service import UserService
from app.db.models.user_model import User, Role

# 사용자 삭제 시 soft delete 처리 및 이벤트 발행 확인 테스트
@pytest.mark.asyncio
async def test_delete_user_triggers_event():
    # Given: 존재하는 사용자와 요청자(Member), 삭제 관련 의존성 설정
    user = User(id=1, email="x", name="x", is_active=True, role=Role(name="Member"))
    repo = AsyncMock()
    repo.get_user_with_role.return_value = user
    repo.delete_user.return_value = None

    service = UserService(repo)
    requester = User(id=1, role=Role(name="Member"))  # 본인 삭제 요청

    # When: 사용자 삭제 메서드 호출 (이벤트 발행 함수는 패치됨)
    with patch("app.service.user_service.publish_user_deleted", new_callable=AsyncMock) as mock_publish:
        await service.delete_user(user_id=1, current_user=requester)

        # Then: 사용자 is_active가 False로 바뀌고, deleted_at 설정됨, 이벤트 발행됨
        assert user.is_active is False
        assert user.deleted_at is not None
        mock_publish.assert_awaited_once_with(1)
