from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import PetInvite, PetInfo, UserInfo, SharedUser
from src.sharing_active import active_shared_access_clause

class SharingRepository:
    async def get_by_code(self, db: AsyncSession, invite_code: str) -> PetInvite:
        res = await db.execute(
            select(PetInvite).where(PetInvite.invite_code == invite_code)
        )
        return res.scalar_one_or_none()
    
    async def existing_shared_user_result(self, db: AsyncSession, pet_id: int, user_id: int) -> SharedUser:
        res = await db.execute(
            select(SharedUser).where(
                and_(
                    SharedUser.shared_pet_id == pet_id,
                    SharedUser.shared_user_id == user_id
            )))
        return res.scalar_one_or_none()
    
    async def get_shared_users(self, db: AsyncSession, pet_id: int) -> List[SharedUser]:
        res = await db.execute(
            select(SharedUser, UserInfo)
            .join(UserInfo, UserInfo.id == SharedUser.shared_user_id)
            .where(*active_shared_access_clause(pet_id=pet_id))
        )
        return res.all()