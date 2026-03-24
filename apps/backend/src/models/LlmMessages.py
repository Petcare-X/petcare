from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

int_primary_key = Annotated[int, mapped_column(primary_key=True)]


class LlmMessages(Base):
    __tablename__ = "llm_chats_messages"

    id: Mapped[int_primary_key]
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("llm_chats_messages.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))