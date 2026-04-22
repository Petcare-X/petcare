from datetime import date

from sqlalchemy import Date, String, Text, BIGINT, text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

class AuthIdentities(Base):
    __tablename__ = "auth_identities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50)) #email or telegram
    user_email: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=True)
    user_password_hash: Mapped[str] = mapped_column(Text, nullable=True)
    user_telegram_id: Mapped[int | None] = mapped_column(BIGINT, unique=True, index=True, nullable=True)