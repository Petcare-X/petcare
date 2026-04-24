import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.exceptions import (
    DatabaseIntegrityAppError,
    InviteAlreadyAcceptedError,
    InviteExpiredError,
    InviteNotFoundError,
    InviteOwnerAcceptError,
    PetNotFoundError,
    SharedAccessNotFoundError,
    SharedPetsNotFoundError,
    SharedUsersNotFoundError,
)
from src.models import PetInvite, SharedUser
from src.schemas import InviteCreate, InviteResponse, PetResponse, SharedUserResponse
from src.service.pets import PetsService
from src.repositories import SharingRepository, PetsRepository


class SharingService:
    def __init__(self) -> None:
        self.pets_service = PetsService()
        self.repo_sharing = SharingRepository()
        self.repo_pets = PetsRepository()

    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _invite_to_response(self, invite: PetInvite) -> InviteResponse:
        invite_url = None
        if settings.INVITE_BASE_URL:
            invite_url = f"{settings.INVITE_BASE_URL.rstrip('/')}/{invite.invite_code}"
        return InviteResponse(invite_code=invite.invite_code, invite_url=invite_url)

    @staticmethod
    def _raise_integrity_error(exc: IntegrityError) -> None:
        orig = getattr(exc, "orig", None)
        msg = str(orig)
        raise DatabaseIntegrityAppError(f"Database integrity error: {msg}")

    async def _get_invite(self, db: AsyncSession, invite_code: str) -> PetInvite:
        invite = await self.repo_sharing.get_by_code(db, invite_code)
        if not invite:
            raise InviteNotFoundError()
        return invite

    def _ensure_invite_is_active(self, invite: PetInvite) -> None:
        if invite.is_active is False:
            raise InviteExpiredError()

        if invite.expires_at:
            now_utc = datetime.now(timezone.utc)
            expires_at_utc = self._to_utc(invite.expires_at)
            if expires_at_utc < now_utc:
                raise InviteExpiredError()

    async def create_invite(
        self,
        user_id: int,
        db: AsyncSession,
        payload: InviteCreate,
    ) -> InviteResponse:
        await self.pets_service.ensure_pet_owner(db, payload.pet_id, user_id)
        invite_code = uuid.uuid4().hex[:12]

        new_invite = PetInvite(
            pet_id=payload.pet_id,
            created_by=user_id,
            invite_code=invite_code,
            max_uses=payload.max_uses, 
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
        except IntegrityError as exc:
            await db.rollback()
            self._raise_integrity_error(exc)


    async def accept_invite(self,
                            db: AsyncSession,
                            invite_code: str,
                            user_id: int) -> None:
        invite = await self._get_invite(db, invite_code)
        self._ensure_invite_is_active(invite)

        if invite.max_uses is not None and invite.uses_count >= invite.max_uses:
            invite.is_active = False
            await db.commit()
            raise InviteExpiredError()

        pet = await self.pets_service.get_pet_by_id(db, invite.pet_id)
        if pet is None:
            raise PetNotFoundError()
        if user_id == pet.user_id:
            raise InviteOwnerAcceptError()
        existing_shared_user = self.repo_sharing.existing_shared_user_result(pet_id=invite.pet_id, user_id=user_id)
        if existing_shared_user:
            if (
                existing_shared_user.sharing_end is None
                or existing_shared_user.sharing_end > datetime.now(timezone.utc)
            ):
                raise InviteAlreadyAcceptedError()
            await db.delete(existing_shared_user)
            await db.flush()

        new_shared_user = SharedUser(
            shared_user_id=user_id,
            shared_pet_id=invite.pet_id,
            sharing_start=datetime.now(timezone.utc),
            sharing_end=self._to_utc(invite.expires_at) if invite.expires_at else None,
        )

        db.add(new_shared_user)

        try:
            invite.uses_count += 1
            await db.commit()
            await db.refresh(invite)
            await db.refresh(new_shared_user)
        except IntegrityError as exc:
            await db.rollback()
            self._raise_integrity_error(exc)


    async def deactivate_invite(
        self,
        db: AsyncSession,
        invite_code: str,
        user_id: int,
    ) -> None:
        invite = await self._get_invite(db, invite_code)
        await self.pets_service.ensure_pet_owner(db, invite.pet_id, user_id)
        invite.is_active = False
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            self._raise_integrity_error(exc)


    async def get_shared_pets(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[PetResponse]:
        shared_pets = await self.repo_pets.get_by_user_id(db, user_id)

        if not shared_pets:
            raise SharedPetsNotFoundError()

        return [self.pets_service.to_response(pet, current_user_id=user_id) for pet in shared_pets]


    async def revoke_access(
        self,
        db: AsyncSession,
        user_id: int,
        pet_id: int,
        shared_user_id: int,
    ) -> None:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        shared_user = await self.repo_sharing.existing_shared_user_result(db, pet_id, user_id=shared_user_id)
        if not shared_user:
            raise SharedAccessNotFoundError()

        try:
            await db.delete(shared_user)
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            self._raise_integrity_error(exc)

    async def get_shared_users(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
    ) -> list[SharedUserResponse]:
        pet = await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        shared_users = await self.repo_sharing.get_shared_users(db, pet_id)

        if not shared_users:
            raise SharedUsersNotFoundError()

        return [
            SharedUserResponse(
                pet_id=shared_user.shared_pet_id,
                pet_name=pet.pet_name,
                shared_with_user_id=user.id,
                shared_with_user_name=user.user_name,
                shared_till=shared_user.sharing_end,
            )
            for shared_user, user in shared_users
        ]

    async def get_invite(
        self,
        db: AsyncSession,
        invite_code: str,
    ) -> InviteResponse:
        invite = await self._get_invite(db, invite_code)
        return self._invite_to_response(invite)
