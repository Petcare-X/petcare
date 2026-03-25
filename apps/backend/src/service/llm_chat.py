from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.models import LlmChat, LlmMessage
from src.service import OpenRouterService
from src.schemas import MessageRole


class LLMChatService:
    def __init__(self):
        self.openrouter_service = OpenRouterService()

    async def create_chat(self, db: AsyncSession, user_id: int, title: str) -> LlmChat:
        chat = LlmChat(user_id=user_id, title=title)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat

    async def get_user_chats(self, db: AsyncSession, user_id: int) -> list[LlmChat]:
        result = await db.execute(
            select(LlmChat)
            .where(LlmChat.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_chat_messages(self, db: AsyncSession, user_id: int, chat_id: int) -> list[LlmMessage]:
        chat = await self._get_user_chat(db, user_id, chat_id)

        result = await db.execute(
            select(LlmMessage)
            .where(LlmMessage.chat_id == chat.id)
            .order_by(LlmMessage.message_created_at.asc())
        )
        return list(result.scalars().all())

    async def send_message(self, db: AsyncSession, user_id: int, chat_id: int, content: str) -> tuple[LlmMessage, LlmMessage]:
        chat = await self._get_user_chat(db, user_id, chat_id)

        user_message = LlmMessage(
            chat_id=chat.id,
            role=MessageRole.USER,
            content=content,
        )
        db.add(user_message)
        await db.flush()

        assistant_text = await self.openrouter_service.generate_answer(content)

        assistant_message = LlmMessage(
            chat_id=chat.id,
            role=MessageRole.ASSISTANT,
            content=assistant_text,
        )
        db.add(assistant_message)

        await db.commit()
        await db.refresh(user_message)
        await db.refresh(assistant_message)

        return user_message, assistant_message

    async def _get_user_chat(self, db: AsyncSession, user_id: int, chat_id: int) -> LlmChat:
        result = await db.execute(
            select(LlmChat).where(
                LlmChat.id == chat_id,
                LlmChat.user_id == user_id,
            )
        )
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat