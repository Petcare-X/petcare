from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid

from src.exceptions import (
    DatabaseIntegrityAppError,
    InviteAlreadyAcceptedError,
    InviteExpiredError,
    InviteNotFoundError,
    InviteOwnerAcceptError,
    PetNotFoundError,
    PetOwnerOnlyError,
    SharedAccessNotFoundError,
    SharedPetsNotFoundError,
    SharedUsersNotFoundError,
)
from src.models import PetInfo, PetInvite, SharedUser, UserInfo
from src.schemas import InviteCreate, InviteResponse, AcceptInvite, SharedUserResponce, PetResponse
from src.service.pets import active_shared_access_clause

class SharingService:
    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _invite_to_response(self, invite: PetInvite) -> InviteResponse:
        return InviteResponse(invite_code=invite.invite_code)

    async def ensure_pet_owner(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
    ) -> PetInfo:
        pet = await db.get(PetInfo, pet_id)
        if not pet:
            raise PetNotFoundError()
        if pet.user_id != user_id:
            raise PetOwnerOnlyError()
        return pet

    async def create_invite(self, 
                            user_id: int, 
                            db: AsyncSession, 
                            payload: InviteCreate) -> PetInvite:
        await self.ensure_pet_owner(db, payload.pet_id, user_id)
        
        invite_code = uuid.uuid4().hex[:12]

        new_invite = PetInvite(
            pet_id=payload.pet_id,
            created_by=user_id,
            invite_code=invite_code,
            max_uses=payload.max_uses if payload.max_uses else None, 
            uses_count=0,
            is_active=True, 
            expires_at=payload.expires_at if payload.expires_at else None,
            created_at=datetime.now(timezone.utc),
        )

        db.add(new_invite)

        try: 
            await db.commit()
            await db.refresh(new_invite)
            return self._invite_to_response(new_invite)
        
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            msg = str(orig)
            
            raise DatabaseIntegrityAppError(f"Database integrity error: {msg}")


    async def accept_invite(self,
                            db: AsyncSession,
                            invite_code: str,
                            user_id: int) -> AcceptInvite:
        invite_result = await db.execute(
            select(PetInvite).where(PetInvite.invite_code == invite_code)
        )
        invite = invite_result.scalar_one_or_none()

        if not invite:
            raise InviteNotFoundError()

        # чек is_active
        if invite.is_active == False:
            raise InviteExpiredError()
        
        # чек expired_at
        if invite.expires_at:
            now_utc = datetime.now(timezone.utc)
            expires_at_utc = self._to_utc(invite.expires_at)
            if expires_at_utc < now_utc:
                raise InviteExpiredError()
        
        # чек uses_count
        if invite.max_uses is not None and invite.uses_count >= invite.max_uses:
            invite.is_active = False
            await db.commit()
            raise InviteExpiredError()

        # чек owner != user
        pet = await db.get(PetInfo, invite.pet_id)
        if user_id == pet.user_id:
            raise InviteOwnerAcceptError()
        
        # чек дубликация доступа
        existing_shared_user_result = await db.execute(
            select(SharedUser).where(
                SharedUser.shared_pet_id == invite.pet_id,
                SharedUser.shared_user_id == user_id,
            )
        )
        existing_shared_user = existing_shared_user_result.scalar_one_or_none()
        if existing_shared_user:
            if existing_shared_user.sharing_end is None or existing_shared_user.sharing_end > datetime.now(timezone.utc):
                raise InviteAlreadyAcceptedError()
            await db.delete(existing_shared_user)
            await db.flush()

        new_shared_user = SharedUser(
            shared_user_id=user_id,
            shared_pet_id=invite.pet_id,
            sharing_start=datetime.now(timezone.utc),
            sharing_end=self._to_utc(invite.expires_at) if invite.expires_at else None
        )

        db.add(new_shared_user)

        try: 
            invite.uses_count += 1
            await db.commit()
            await db.refresh(new_shared_user)
            return {
                "message": "Invite accepted",
                "invite code": invite.invite_code
            }
        
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            msg = str(orig)

            raise DatabaseIntegrityAppError(f"Database integrity error: {msg}")


    async def deactivate_invite(self, 
                                db: AsyncSession,
                                invite_code: str,
                                user_id: int) -> PetInvite:
        invite_result = await db.execute(
            select(PetInvite).where(PetInvite.invite_code == invite_code)
        )
        invite = invite_result.scalar_one_or_none()

        if not invite:
            raise InviteNotFoundError()
        
        await self.ensure_pet_owner(db, invite.pet_id, user_id)
        
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

            raise DatabaseIntegrityAppError(f"Database integrity error: {msg}")


    async def get_shared_pets(self, 
                            db: AsyncSession, 
                            user_id: int) -> list[PetResponse]:
        shared_pets_result = await db.execute(
            select(PetInfo)
            .join(SharedUser, SharedUser.shared_pet_id == PetInfo.id)
            .where(*active_shared_access_clause(user_id))
        )
        shared_pets = list(shared_pets_result.scalars().all())

        if not shared_pets:
            raise SharedPetsNotFoundError()

        return [
            PetResponse(
                id=pet.id,
                user_id=pet.user_id,
                pet_name=pet.pet_name,
                pet_date_of_birth=pet.pet_date_of_birth,
                animal_type_id=pet.animal_type_id,
                animal_breed_id=pet.animal_breed_id,
                pedigree=bool(pet.pedigree),
                pet_length=float(pet.pet_length),
                pet_neck_girth=float(pet.pet_neck_girth),
                pet_breast_girth=float(pet.pet_breast_girth),
                pet_weight=float(pet.pet_weight),
                pet_is_sterylyzed=pet.pet_is_sterylyzed,
                pet_photo=pet.pet_photo,
                is_shared=True,
            )
            for pet in shared_pets
        ]


    async def revoke_access(self, 
                            db: AsyncSession, 
                            user_id: int,
                            pet_id: int,
                            shared_user_id: int) -> PetInvite:
        await self.ensure_pet_owner(db, pet_id, user_id)
        
        shared_user_result = await db.execute(
            select(SharedUser).where(
                SharedUser.shared_pet_id == pet_id,
                SharedUser.shared_user_id == shared_user_id,
            )
        )
        shared_user = shared_user_result.scalar_one_or_none()
        
        if not shared_user:
            raise SharedAccessNotFoundError()
        
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

            raise DatabaseIntegrityAppError(f"Database integrity error: {msg}")
        

    async def get_shared_users(self, 
                                db: AsyncSession, 
                                pet_id: int,
                                user_id: int) -> list[SharedUserResponce]:
        pet = await self.ensure_pet_owner(db, pet_id, user_id)
        
        shared_users_result = await db.execute(
            select(SharedUser, UserInfo)
            .join(UserInfo, UserInfo.id == SharedUser.shared_user_id)
            .where(*active_shared_access_clause(pet_id=pet_id))
        )
        shared_users = shared_users_result.all()
        
        if not shared_users:
            raise SharedUsersNotFoundError()

        return [
            SharedUserResponce(
                pet_id=shared_user.shared_pet_id,
                pet_name=pet.pet_name,
                shared_with_user_id=user.id,
                shared_with_user_name=user.user_name,
                shared_till=shared_user.sharing_end,
            )
            for shared_user, user in shared_users
        ]
    
    async def get_invite(self, 
                        db: AsyncSession, 
                        invite_code: str) -> PetInvite:
        invite_result = await db.execute(
            select(PetInvite).where(PetInvite.invite_code == invite_code)
        )
        invite = invite_result.scalar_one_or_none()
        if not invite:
            raise InviteNotFoundError()
        return self._invite_to_response(invite)
