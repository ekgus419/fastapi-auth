from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.controller.auth.auth_deps import self_or_admin_required, admin_required
from app.db.models.user_model import User
from app.domain.user.user_schema import UserUpdateRequest, UserQueryParams, UserListResponse
from app.repository.persistence.user_repository_impl import UserRepositoryImpl
from app.service.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(self_or_admin_required),
    db: AsyncSession = Depends(get_db_session),
):
    """
    👁️ 사용자 단건 조회 API

    - 지정된 사용자 ID에 대한 정보를 조회합니다.
    - Admin 또는 본인만 접근 가능합니다.

    🔐 권한:
    - Admin: 모든 사용자 조회 가능
    - Member: 본인만 조회 가능

    ⚙️ 내부 처리:
    - Redis 캐시 우선 조회 (`user:{user_id}`)
    - 캐시 미존재 시 DB 조회 후 캐싱

    📤 Response:
    - 사용자 ID, 이메일, 이름, 역할 등
    """
    repo = UserRepositoryImpl(db)
    service = UserService(repo)
    return await service.get_user(user_id, current_user)


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    update: UserUpdateRequest,
    current_user: User = Depends(self_or_admin_required),
    db: AsyncSession = Depends(get_db_session),
):
    """
    ✏️ 사용자 정보 수정 API

    - 사용자 이름, 이메일, 활성화 여부 등을 수정할 수 있습니다.
    - Admin 또는 본인만 수정 가능합니다.

    🔐 권한:
    - Admin: 모든 사용자 수정 가능
    - Member: 본인만 수정 가능 (단, `is_active`는 수정 불가)

    📥 Request Body:
    - name: 변경할 이름 (선택)
    - email: 변경할 이메일 (선택)
    - is_active: 활성 상태 여부 (Admin만 가능)

    ⚙️ 내부 처리:
    - 수정 후 Redis 캐시 무효화 (`user:{user_id}`, `users:*`)

    📤 Response:
    - 수정된 사용자 정보 반환
    """
    repo = UserRepositoryImpl(db)
    service = UserService(repo)
    updated = await service.update_user(user_id, update, current_user)
    return {
        "id": updated.id,
        "email": updated.email,
        "name": updated.name,
        "is_active": updated.is_active,
        "role": updated.role.name,
    }

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(self_or_admin_required),
    db: AsyncSession = Depends(get_db_session),
):
    """
    ❌ 사용자 탈퇴 API

    - 지정된 사용자 계정을 soft delete 방식으로 탈퇴 처리합니다.
    - Admin 또는 본인만 탈퇴 요청 가능

    🔐 권한:
    - Admin: 모든 사용자 탈퇴 가능
    - Member: 본인만 탈퇴 가능

    ⚙️ 내부 처리:
    - `deleted_at` 및 `is_active` 처리
    - Redis 캐시 무효화 (`user:{user_id}`, `users:*`)
    - MQ 비동기 이벤트 발행 (`publish_user_deleted` → RabbitMQ)

    📤 Response:
    - {"message": "사용자 {user_id} 탈퇴 처리 완료"}
    """
    repo = UserRepositoryImpl(db)
    service = UserService(repo)
    await service.delete_user(user_id, current_user)
    return {"message": f"사용자 {user_id} 탈퇴 처리 완료"}


@router.get("", response_model=UserListResponse)
async def get_users(
    params: UserQueryParams = Depends(),
    current_user: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db_session),
):
    """
    📋 전체 사용자 목록 조회 API

    - 등록된 사용자 목록을 페이지 단위로 조회합니다.
    - Admin만 접근 가능합니다.

    🔐 권한:
    - Admin 전용

    📥 Query Params:
    - page: 페이지 번호
    - size: 페이지 크기

    ⚙️ 내부 처리:
    - Query 파라미터 기준 Redis 캐시 사용 (`users:{md5_hash}`)
    - 미존재 시 DB 조회 후 캐싱

    📤 Response:
    - 사용자 리스트 + total count 포함 (`UserListResponse`)
    """
    repo = UserRepositoryImpl(db)
    service = UserService(repo)
    return await service.get_users(params)
