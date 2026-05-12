from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class LlmMessage(Base):
    __tablename__ = "llm_chats_messages"

    id: Mapped[int_primary_key]
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("llm_chats.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parent_message_id: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    message_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
