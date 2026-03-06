from datetime import date

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class UserInfo(Base):
    __tablename__ = "user_info"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    user_email: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    user_password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    user_phone: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)

    user_photo: Mapped[str] = mapped_column(Text, nullable=False)