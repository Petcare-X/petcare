from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

int_primary_key = Annotated[int, mapped_column(primary_key=True)]


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int_primary_key]
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users_info.id", ondelete="CASCADE"), index=True
    )
    token_jti: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
