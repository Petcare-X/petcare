from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import LlmChat, LlmMessage
from src.schemas import MessageRole
from src.service.openrouter import OpenRouterService


class LLMChatService:
    def __init__(self):
        self.openrouter_service = OpenRouterService()

    def _build_openrouter_messages(
        self,
        chat: LlmChat,
        history: list[LlmMessage],
        current_content: str,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if chat.chat_custom_instructions:
            messages.append(
                {
                    "role": MessageRole.SYSTEM.value,
                    "content": chat.chat_custom_instructions,
                }
            )

        for message in history:
            messages.append(
                {
                    "role": str(message.role),
                    "content": message.content,
                }
            )

        messages.append(
            {
                "role": MessageRole.USER.value,
                "content": current_content,
            }
        )
        return messages

    async def create_chat(self, db: AsyncSession, user_id: int, title: str) -> LlmChat:
        chat = LlmChat(user_id=user_id, chat_title=title)
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
        history = await self.get_chat_messages(db, user_id, chat_id)

        user_message = LlmMessage(
            chat_id=chat.id,
            user_id=user_id,
            role=MessageRole.USER,
            content=content,
        )
        db.add(user_message)
        await db.flush()

        assistant_text = await self.openrouter_service.generate_answer(
            self._build_openrouter_messages(chat, history, content)
        )

        assistant_message = LlmMessage(
            chat_id=chat.id,
            user_id=user_id,
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
