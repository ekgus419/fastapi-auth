from sqlalchemy import String, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Role(Base, TimestampMixin):
    """
    역할 테이블 (roles)
    - 사용자 권한/등급 정보를 정의합니다.
    - 예: Admin, Member 등
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, comment="PK: 역할 ID")
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="역할 이름 (예: Admin, Member)"
    )
    description: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="역할 설명"
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class User(Base, TimestampMixin):
    """
    사용자 테이블 (users)
    - 시스템 내 사용자 계정 정보 저장
    - 각 사용자에게 역할(Role)이 1개 지정됨
    """
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_name", "name"),
        Index("idx_users_role_id", "role_id"),
        Index("idx_users_is_active", "is_active"),
        Index("idx_users_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="PK: 사용자 ID")
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="로그인용 이메일 주소"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="bcrypt 해시된 로그인 비밀번호"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="사용자 이름 (선택)"
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"), nullable=False, comment="FK: 역할 ID (roles.id)"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="활성 상태 여부"
    )

    role: Mapped["Role"] = relationship("Role", back_populates="users")
