from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

int_primary_key = Annotated[int, mapped_column(primary_key=True)]


class LlmChat(Base):
    __tablename__ = "llm_chats"

    id: Mapped[int_primary_key]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    chat_title: Mapped[str | None] = mapped_column(String(255))
    chat_custom_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    chat_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())