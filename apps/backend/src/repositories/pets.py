from typing import List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import PetInfo, SharedUser, PetDocument
from src.service.pets import active_shared_access_clause

class PetsRepository:
    async def get_all(self, db: AsyncSession, offset: int = 0, limit: int = 50) -> List[PetInfo]:
        res = await db.execute(
            select(PetInfo).offset(offset).limit(limit)
        )
        return list(res.scalars().all())
    
    async def get_by_id(self, db: AsyncSession, pet_id: int) -> PetInfo:
        res = await db.execute(
            select(PetInfo).where(PetInfo.id == pet_id)
            )
        return res.scalar_one_or_none()
    
    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> List[PetInfo]:
        user_pet = await db.execute(
            select(PetInfo)
            .outerjoin(SharedUser, SharedUser.shared_pet_id == PetInfo.id)
            .where(
                or_(
                    PetInfo.user_id == user_id,
                    and_(*active_shared_access_clause(user_id)),
                )))
        return list(user_pet.scalars().all())
    
    async def get_docs_keys(self, db: AsyncSession, pet_id: int) -> List[str]:
        res = await db.execute(
            select(PetDocument.object_key).where(PetDocument.pet_id == pet_id)
        )
        return list(res.scalars().all())