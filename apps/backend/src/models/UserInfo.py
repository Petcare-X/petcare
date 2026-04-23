from datetime import date

from sqlalchemy import Date, String, Text, BIGINT, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

class UserInfo(Base):
    __tablename__ = "users_info"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_name: Mapped[str] = mapped_column(String(50))
    user_date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    user_phone_number: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=True)
    user_email: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=True)
    user_photo: Mapped[str | None] = mapped_column(Text, nullable=True)