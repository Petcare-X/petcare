from typing import List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import LlmMessage

class LlmMessageRepository:
    async def get_by_chat_id(self, db: AsyncSession, chat_id: int) -> List[LlmMessage]:
        res = await db.execute(
            select(LlmMessage)
            .where(LlmMessage.chat_id == chat_id)
            .order_by(LlmMessage.message_created_at)
        )
        return list(res.scalars().all())
    
    async def get_by_id(self, db: AsyncSession, message_id: int) -> LlmMessage:
        res = await db.execute(
            select(LlmMessage).where(LlmMessage.id == message_id)
        )
        return res.scalar_one_or_none()
    
    async def get_chat_user(self, db: AsyncSession, user_id: int, chat_id: int) -> List[LlmMessage]:
        res = await db.execute(
            select(LlmMessage).where(
                and_(LlmMessage.chat_id == chat_id, 
                    LlmMessage.user_id == user_id)
        ))
        return list(res.scalars().all())
    
    async def get_chat_assistant(self, db: AsyncSession, chat_id: int) -> List[LlmMessage]:
        res = await db.execute(
            select(LlmMessage).where(
                and_(LlmMessage.chat_id == chat_id, 
                    LlmMessage.user_id == None)
        ))
        return list(res.scalars().all())