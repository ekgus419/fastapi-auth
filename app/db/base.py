from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func

class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """
    모든 테이블에 공통으로 포함될 컬럼 정의
    - created_at: 생성 시각
    - updated_at: 수정 시각
    - deleted_at: 삭제 시각 (Soft Delete 용)
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="생성 시각"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="수정 시각"
    )
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="Soft Delete 시각 (null이면 유효)"
    )
