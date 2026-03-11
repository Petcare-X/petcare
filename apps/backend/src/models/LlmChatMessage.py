from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

int_primary_key = Annotated[int, mapped_column(primary_key=True)]


class LlmChatMessage(Base):
    __tablename__ = "llm_chats_messages"

    id: Mapped[int_primary_key]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    conversation_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(20))
    message_text: Mapped[str] = mapped_column(Text)
    message_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
