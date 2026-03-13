from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime, timezone
import uuid

from src.models import PetInfo, PetInvite, SharedUser
from src.schemas import InviteCreate, InviteResponse, AcceptInvite, SharedUserResponce, BasePet

class SharingService:
    async def create_invite(self, 
                            user_id: int, 
                            db: AsyncSession, 
                            payload: InviteCreate) -> PetInvite:
        
        pet = self.db.query(PetInfo).filter(PetInfo.id == payload.pet_id).first()
        if not pet or pet.user_id != user_id:
            raise HTTPException(status_code=400, 
                                detail="User is not the owner of the pet")
        
        invite_code = uuid.uuid4().hex[:12]

        new_invite = PetInvite(
            pet_id=payload.pet_id,
            created_by=user_id,
            invite_code=invite_code,
            max_uses=payload.max_uses if payload.max_uses else None, 
            uses_count=0,
            is_active=True, 
            expires_at=payload.expires_at if payload.expires_at else None,
        )

        db.add(new_invite)

        try: 
            await db.commit()
            await db.refresh(new_invite)
            return InviteResponse(**new_invite.dump_model())
        
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
                            invite_code: int,
                            user_id: int,
                            expires_at: datetime | None = None
                            ) -> PetInvite:
        invite = db.query(PetInvite).filter(PetInvite.invite_code == invite_code).first()

        if not invite:
            raise HTTPException(status_code=404, 
                                detail="Invite not found")

        # чек is_active
        if invite.is_active == False:
            raise HTTPException(status_code=400, 
                                detail="Invite has expired")
        
        # чек expired_at
        if invite.expires_at:
            now_utc = datetime.now(timezone.utc)
            if invite.expires_at < now_utc:
                raise HTTPException(status_code=400, 
                                    detail="Invite has expired")
        
        # чек uses_count
        if invite.uses_count and (invite.max_uses <= invite.uses_count):
            invite.is_active = False

        # чек owner != user
        pet = db.query(PetInfo).filter(PetInfo.id == invite.pet_id).first()
        if user_id == pet.user_id:
            raise HTTPException(status_code=400,
                                detail="Owner cannot accept the invite")
        
        # чек дубликация доступа
        existing_shared_user = db.query(SharedUser).filter(SharedUser.pet_id == invite.pet_id, SharedUser.user_id == user_id).first()
        if existing_shared_user:
            raise HTTPException(status_code=400,
                                detail="Already have access")

        new_shared_user = SharedUser(
            shared_user_id=user_id,
            shared_pet_id=invite.pet_id,
            sharing_start=datetime.now(timezone.utc),
            sharing_end=expires_at if expires_at else None
        )

        db.add(new_shared_user)

        try: 
            await db.commit()
            await db.refresh(new_shared_user)
            invite.uses_count += 1
            return AcceptInvite(**new_shared_user.dump_model())
        
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            msg = str(orig)

            raise HTTPException(status_code=400,
                                detail=f"Database integrity error: {msg}")


    async def deactivate_invite(self, 
                                db: AsyncSession,
                                invite_code: str,
                                user_id: int) -> PetInvite:
        invite = db.query(PetInvite).filter(PetInvite.invite_code == invite_code).first()

        if not invite:
            raise HTTPException(status_code=404, 
                                detail="Invite not found")
        
        pet = db.query(PetInfo).filter(PetInfo.id == invite.pet_id).first()
        if pet.user_id != user_id:
            raise HTTPException(status_code=403, 
                                detail="Only the owner can deactivate the invite")
        
        invite.is_active = False
        try:
            db.commit()
            db.refresh(invite)
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
                            user_id: int) -> list[BasePet]:
        shared_pets = db.query(PetInfo).join(
            SharedUser, 
            SharedUser.pet_id == PetInfo.id).filter(
            SharedUser.user_id == user_id,
            (SharedUser.shared_till == None) | (SharedUser.shared_till > datetime.now(timezone.utc))
        ).all()

        if not shared_pets:
            raise HTTPException(status_code=404,
                                detail="Shared pets not found")

        for pet in shared_pets:
            pet = BasePet(**pet.dump_model())
        
        return shared_pets


    async def revoke_access(self, 
                            db: AsyncSession, 
                            user_id: int, 
                            pet_id: int) -> PetInvite:
        pet = db.query(PetInfo).filter(PetInfo.id == pet_id).first()

        if not pet:
            raise HTTPException(status_code=404,
                                detail="Pet not found")
        
        if pet.user_id != user_id:
            raise HTTPException(status_code=403,
                                detail="Access denied")
        
        shared_user = db.query(SharedUser).filter(
            SharedUser.shared_pet_id == pet_id, 
            SharedUser.shared_user_id == user_id).first()
        
        if not shared_user:
            raise HTTPException(status_code=404,
                                detail="User not found")
        
        try:
            db.delete(shared_user)
            db.commit()
            return{
                "msg": "Access revoked"
            }
        
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            msg = str(orig)

            raise HTTPException(status_code=400,
                                detail=f"Database integrity error: {msg}")
