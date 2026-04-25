from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.phone import to_e164
from src.core.security import hash_password
from src.exceptions import (
    UserConflictError,
    UserNotFoundError,
)
from src.models import PetInfo, UserInfo, AuthIdentities
from src.schemas import CreateUser, UpdateUser, UserPrivate
from src.repositories import UsersRepository, PetsRepository

class UsersService:
    def __init__(self):
        self.repo = UsersRepository()
        self.repo_pets = PetsRepository()

    async def to_private_response(self, db: AsyncSession, user: UserInfo):
        auth_identities = await self.repo.get_auth_identities_by_user_id(db, user.id)
        telegram_identity = next((item for item in auth_identities if item.provider == "telegram"), None)
        primary_identity = next((item for item in auth_identities if item.provider), None)

        return UserPrivate(
            id=user.id,
            user_name=user.user_name,
            user_email=user.user_email,
            user_phone_number=user.user_phone_number,
            user_date_of_birth=user.user_date_of_birth,
            user_photo=user.user_photo,
            telegram_id=telegram_identity.user_telegram_id if telegram_identity else None,
            auth_provider=primary_identity.provider if primary_identity else "unknown",
        )

    async def create_user(self, db: AsyncSession, payload: CreateUser) -> UserInfo:
        phone_str = to_e164(payload.user_phone_number) if payload.user_phone_number is not None else None
        photo_str = str(payload.user_photo) if payload.user_photo is not None else None

        user = UserInfo(
            user_name=payload.user_name.strip(),
            user_email=str(payload.user_email),
            user_phone_number=phone_str,
            user_date_of_birth=payload.user_date_of_birth,
            user_photo=photo_str,
        )

        db.add(user)

        await db.commit()
        await db.refresh(user)

        auth_identity = AuthIdentities(
            user_id=user.id,
            provider="email",
            user_email=str(payload.user_email),
            user_password_hash=hash_password(payload.password)
        )

        db.add(auth_identity)
        await db.commit()
        await db.refresh(auth_identity)
        return user
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> UserInfo | None:
        return await self.repo.get_by_id(db, user_id)

    async def get_user_by_email(self, db: AsyncSession, email: str) -> UserInfo | None:
        return await self.repo.get_by_email(db, email)

    async def get_user_by_phone(self, db: AsyncSession, phone: str) -> UserInfo | None:
        return await self.repo.get_by_phone(db, phone)

    async def list_all_users(self, db: AsyncSession, offset: int = 0, limit: int = 50) -> list[UserInfo]:
        return await self.repo.get_all(db, offset, limit)

    async def update_user(self, user_id: int, payload: UpdateUser, db: AsyncSession) -> UserInfo | None:
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        data = payload.model_dump(exclude_unset=True)

        if "user_name" in data and data["user_name"] is not None:
            user.user_name = data["user_name"].strip()

        if "user_photo" in data:
            user.user_photo = str(data["user_photo"]) if data["user_photo"] is not None else None
            
        if "user_email" in data and data["user_email"] is not None:
            user.user_email = str(data["user_email"])

        if "user_phone_number" in data:
            if payload.user_phone_number is not None:
                user.user_phone_number = to_e164(payload.user_phone_number)
            else:
                user.user_phone_number = None

        
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise UserConflictError()

    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        await db.delete(user)
        await db.commit()
        return True
    
    async def list_user_pets(self, db: AsyncSession, user_id: int) -> list[PetInfo]:
        return await self.repo_pets.get_by_user_id(db, user_id)
    
    async def link_telegram_login(self, db: AsyncSession, user_id: int, telegram_id: int) -> UserInfo:
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()
        
        auth_identity = await self.repo.get_auth_by_tg(db, telegram_id)
        if auth_identity:
            raise UserConflictError() # уже привязан
        
        new_auth_identity = AuthIdentities(
            user_id=user.id,
            provider="telegram",
            user_telegram_id=telegram_id,
        )

        db.add(new_auth_identity)
        await db.commit()
        return True

    async def link_email_login(self, db: AsyncSession, user_id: int, email: str) -> UserInfo:
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()
        
        auth_identity = await self.repo.get_auth_by_email(db, email)
        if auth_identity:
            raise UserConflictError() # уже привязан
        
        new_auth_identity = AuthIdentities(
            user_id=user.id,
            provider="email",
            user_email=email,
        )

        if user.user_email is None:
            await self.update_user(user_id=user_id, payload=UpdateUser(user_email=email), db=db)

        db.add(new_auth_identity)
        await db.commit()
        return True
