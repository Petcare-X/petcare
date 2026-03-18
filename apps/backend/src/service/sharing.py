from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime, timezone
import uuid

from src.models import PetInfo, PetInvite, SharedUser
from src.schemas import InviteCreate, InviteResponse, SharedUserResponse, AcceptInvite, BasePet

class SharingService:
    async def create_invite(self, 
                            user_id: int, 
                            db: AsyncSession, 
                            payload: InviteCreate) -> InviteResponse:
        
        result = await db.execute(
            select(PetInfo).where(PetInfo.id == payload.pet_id))
        pet = result.scalar_one_or_none()
        if not pet:
            raise HTTPException(status_code=404, 
                                detail="Pet not found")

        if pet.user_id != user_id:
            raise HTTPException(status_code=400, 
                                detail="User is not the owner of the pet")
        
        invite_code = uuid.uuid4().hex[:12]

        new_invite = PetInvite(
            pet_id=payload.pet_id,
            created_by=user_id,
            invite_code=invite_code,
            max_uses=payload.max_uses, 
            uses_count=0,
            is_active=True, 
            expires_at=payload.expires_at
        )

        db.add(new_invite)

        try: 
            await db.commit()
            await db.refresh(new_invite)
            return InviteResponse.model_validate(new_invite)
        
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            msg = str(orig)
            
            raise HTTPException(
                status_code=400,
                detail=f"Database integrity error: {msg}"
            )


    async def accept_invite(self,
                            db: AsyncSession,
                            invite_code: str,
                            shared_user_id: int):
        result = await db.execute(
            select(PetInvite).where(PetInvite.invite_code == invite_code))
        invite = result.scalar_one_or_none()

        if not invite:
            raise HTTPException(status_code=404, 
                                detail="Invite not found")

        # чек is_active
        if not invite.is_active:
            raise HTTPException(status_code=400, 
                                detail="Invite has expired")
        
        # чек expired_at
        if invite.expires_at:
            now_utc = datetime.now(timezone.utc)
            if invite.expires_at < now_utc:
                raise HTTPException(status_code=400, 
                                    detail="Invite has expired")
        
        # чек uses_count
        if invite.max_uses and (invite.max_uses <= invite.uses_count):
            invite.is_active = False

        # чек owner != user
        result = await db.execute(
            select(PetInfo).where(PetInfo.id == invite.pet_id))
        pet = result.scalar_one_or_none()
        if shared_user_id == pet.user_id:
            raise HTTPException(status_code=400,
                                detail="Owner cannot accept the invite")
        
        # чек дубликация доступа
        result = await db.execute(
                select(SharedUser).where(SharedUser.shared_pet_id == invite.pet_id, 
                                        SharedUser.shared_user_id == shared_user_id))
        existing_shared_user = result.scalar_one_or_none()
        if existing_shared_user:
            raise HTTPException(status_code=400,
                                detail="Already have access")

        new_shared_user = SharedUser(
            shared_user_id=shared_user_id,
            shared_pet_id=invite.pet_id,
            sharing_end=invite.expires_at
        )

        db.add(new_shared_user)

        try: 
            invite.uses_count += 1
            await db.commit()
            await db.refresh(invite)
            await db.refresh(new_shared_user)
            return AcceptInvite.model_validate(invite)
        
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            msg = str(orig)

            raise HTTPException(status_code=400,
                                detail=f"Database integrity error: {msg}")


    async def deactivate_invite(self, 
                                db: AsyncSession,
                                invite_code: str,
                                shared_user_id: int):
        result = await db.execute(
            select(PetInvite).where(PetInvite.invite_code == invite_code))
        invite = result.scalar_one_or_none()

        if not invite:
            raise HTTPException(status_code=404, 
                                detail="Invite not found")
        
        result = await db.execute(
            select(PetInfo).where(PetInfo.id == invite.pet_id))
        pet = result.scalar_one_or_none()
        if pet.user_id != shared_user_id:
            raise HTTPException(status_code=403, 
                                detail="Only the owner can deactivate the invite")
        
        invite.is_active = False
        try:
            await db.commit()
            await db.refresh(invite)
            return {
                "msg": f"Invite with invite code {invite.invite_code} is deactivated"
                }
        
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            msg = str(orig)

            raise HTTPException(status_code=400,
                                detail=f"Database integrity error: {msg}")


    async def get_shared_pets(self, 
                            db: AsyncSession, 
                            shared_user_id: int,
                            offset: int = 0,
                            limit: int = 5) -> list[BasePet]:
        result = await db.execute(select(PetInfo).join(
            SharedUser, 
            SharedUser.shared_pet_id == PetInfo.id).where(
            SharedUser.shared_user_id == shared_user_id,
            (SharedUser.sharing_end.is_(None) | (SharedUser.sharing_end > datetime.now(timezone.utc))).offset(
            offset).limit(limit)))
        shared_pets = result.scalars().all()

        if not shared_pets:
            return []
        
        return [BasePet.model_validate(pet) for pet in shared_pets]


    async def revoke_access(self, 
                            db: AsyncSession, 
                            shared_user_id: int, 
                            pet_id: int):
        result = await db.execute(
            select(PetInfo).where(PetInfo.id == pet_id))
        pet = result.scalar_one_or_none()

        if not pet:
            raise HTTPException(status_code=404,
                                detail="Pet not found")
        
        if pet.user_id == shared_user_id:
            raise HTTPException(status_code=403,
                                detail="Cannot revoke access of the owner")
        
        result = await db.execute(select(SharedUser).where(
            SharedUser.shared_pet_id == pet_id, 
            SharedUser.shared_user_id == shared_user_id))
        shared_user = result.scalar_one_or_none()
        
        if not shared_user:
            raise HTTPException(status_code=404,
                                detail="User not found")
        
        try:
            await db.delete(shared_user)
            await db.commit()
            return{
                "msg": "Access revoked"
            }
        
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            msg = str(orig)

            raise HTTPException(status_code=400,
                                detail=f"Database integrity error: {msg}")
        

    async def get_shared_users(self, 
                                db: AsyncSession, 
                                pet_id: int) -> list[SharedUserResponse]:
        result = await db.execute(
            select(PetInfo).where(PetInfo.id == pet_id))
        pet = result.scalar_one_or_none()

        if not pet:
            raise HTTPException(status_code=404,
                                detail="Pet not found")
        
        result = await db.execute(
            select(SharedUser).where(
            SharedUser.shared_pet_id == pet_id))
        shared_users = result.scalars().all()

        if not shared_users:
            return []
        
        return [SharedUserResponse.model_validate(user) for user in shared_users]
    
    async def get_invite(self, 
                        db: AsyncSession, 
                        invite_code: str) -> InviteResponse:
        result = await db.execute(
            select(PetInvite).where(PetInvite.invite_code == invite_code))
        invite = result.scalar_one_or_none()

        if not invite:
            raise HTTPException(status_code=404,
                                detail="Invite not found")
        return InviteResponse.model_validate(invite)