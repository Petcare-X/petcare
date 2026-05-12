from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserInfo, AuthIdentities

class UsersRepository:
    async def get_all(self, db: AsyncSession, offset: int = 0, limit: int = 50) -> List[UserInfo]:
        res = await db.execute(
            select(UserInfo).offset(offset).limit(limit)
        )
        return list(res.scalars().all())
    
    async def get_by_id(self, db: AsyncSession, user_id: int) -> UserInfo:
        res = await db.execute(
            select(UserInfo).where(UserInfo.id == user_id)
        )
        return res.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> UserInfo:
        res = await db.execute(
            select(UserInfo).where(UserInfo.user_email == email)
        )
        return res.scalar_one_or_none()
    
    async def get_by_phone(self, db: AsyncSession, phone: str) -> UserInfo:
        res = await db.execute(
            select(UserInfo).where(UserInfo.user_phone_number == phone)
            )
        return res.scalar_one_or_none()
    
    async def get_auth_by_tg(self, db: AsyncSession, telegram_id: int) -> AuthIdentities:
        res = await db.execute(
            select(AuthIdentities).where(AuthIdentities.provider == "telegram")
            .where(AuthIdentities.user_id == telegram_id)
        )
        return res.scalar_one_or_none()
    
    async def get_auth_by_email(self, db: AsyncSession, email: str) -> AuthIdentities:
        res = await db.execute(
            select(AuthIdentities).where(AuthIdentities.provider == "email")
            .where(AuthIdentities.user_email == email)
        )
        return res.scalar_one_or_none()

    async def get_auth_identities_by_user_id(self, db: AsyncSession, user_id: int) -> List[AuthIdentities]:
        res = await db.execute(
            select(AuthIdentities).where(AuthIdentities.user_id == user_id)
        )
        return list(res.scalars().all())
