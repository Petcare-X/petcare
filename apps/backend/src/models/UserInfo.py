from datetime import date

from sqlalchemy import Date, String, Text, BIGINT, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

class UserInfo(Base):
    __tablename__ = "users_info"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_name: Mapped[str] = mapped_column(String(50))
    user_date_of_birth: Mapped[date] = mapped_column(Date)
    user_email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    user_password_hash: Mapped[str] = mapped_column(Text)
    user_phone_number: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    user_photo: Mapped[str] = mapped_column(Text)
    telegram_id: Mapped[int | None] = mapped_column(BIGINT, unique=True, index=True, nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(20), server_default=text("'email'"), nullable=False)
