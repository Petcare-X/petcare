from datetime import date

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base

class UserInfo(Base):
    __tablename__ = "users_info"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_name: Mapped[str] = mapped_column(String(50))
    user_date_of_birth: Mapped[date] = mapped_column(Date)
    user_email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    user_password_hash: Mapped[str] = mapped_column(Text)
    user_phone: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    user_photo: Mapped[str] = mapped_column(Text)