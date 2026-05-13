from typing import List
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import LlmChat

class LlmChatRepository:
    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> List[LlmChat]:
        res = await db.execute(
            select(LlmChat)
            .where(LlmChat.user_id == user_id)
        )
        return list(res.scalars().all())
    
    async def get_by_id(self, db: AsyncSession, chat_id: int) -> LlmChat:
        res = await db.execute(
            select(LlmChat).where(LlmChat.id == chat_id)
            )
        return res.scalar_one_or_none()
    
    async def get_user_chat(self, db: AsyncSession, user_id: int, chat_id: int) -> LlmChat:
        res = await db.execute(
            select(LlmChat).where(
                and_(LlmChat.id == chat_id, 
                    LlmChat.user_id == user_id)
            ))
        return res.scalar_one_or_none()
    
    async def get_by_user_pet(self, db: AsyncSession, user_id: int, pet_id: int) -> List[LlmChat]:
        res = await db.execute(
            select(LlmChat).where(
                and_(LlmChat.user_id == user_id, 
                LlmChat.pet_id == pet_id)))
        return list(res.scalars().all())
    
    async def delete_by_id(self, db: AsyncSession, chat_id: int) -> bool:
        await db.execute(
            delete(LlmChat).where(LlmChat.id == chat_id))
        await db.commit()
        return True