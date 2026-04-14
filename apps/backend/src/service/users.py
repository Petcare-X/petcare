from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.phone import to_e164
from src.core.security import hash_password
from src.exceptions import (
    DatabaseIntegrityAppError,
    UserConflictError,
    UserNotFoundError,
)
from src.models import PetInfo, SharedUser, UserInfo
from src.schemas import CreateUser, UpdateUser
from src.service.pets import active_shared_access_clause

class UsersService:
    def to_private_response(self, user: UserInfo):
        from src.schemas.users import UserPrivate

        return UserPrivate.model_validate(user)

    async def create_user(self, db: AsyncSession, payload: CreateUser) -> UserInfo:
        phone_str = to_e164(payload.user_phone_number)
        photo_str = str(payload.user_photo) if payload.user_photo is not None else None

        user = UserInfo(
            user_name=payload.user_name.strip(),
            user_email=str(payload.user_email),
            user_phone_number=phone_str,
            user_password_hash=hash_password(payload.password),
            user_date_of_birth=payload.user_date_of_birth,
            user_photo=photo_str,
        )

        db.add(user)

        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError as e:
            await db.rollback()

            orig = getattr(e, "orig", None)
            sqlstate = getattr(orig, "sqlstate", None)
            constraint = getattr(orig, "constraint_name", None)
            msg = str(orig)

            if sqlstate == "23505":
                if constraint and "email" in constraint:
                    raise UserConflictError("User with this email already exists")
                if constraint and "phone" in constraint:
                    raise UserConflictError("User with this phone number already exists")

            if sqlstate == "23514":
                raise DatabaseIntegrityAppError(
                    f"CHECK constraint failed: {constraint or 'unknown'}"
                )

            raise DatabaseIntegrityAppError(f"Database integrity error: {msg}")
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> UserInfo | None:
        return await db.get(UserInfo, user_id)


    async def get_user_by_email(self, db: AsyncSession, email: str) -> UserInfo | None:
        res = await db.execute(select(UserInfo).where(UserInfo.user_email == email))
        return res.scalar_one_or_none()


    async def get_user_by_phone(self, db: AsyncSession, phone: str) -> UserInfo | None:
        res = await db.execute(select(UserInfo).where(UserInfo.user_phone_number == phone))
        return res.scalar_one_or_none()


    async def list_all_users(self, db: AsyncSession, offset: int = 0, limit: int = 50) -> list[UserInfo]:
        res = await db.execute(select(UserInfo).offset(offset).limit(limit))
        return list(res.scalars().all())

    async def update_user(self, user_id: int, payload: UpdateUser, db: AsyncSession) -> UserInfo | None:
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        data = payload.model_dump(exclude_unset=True)

        if "user_name" in data and data["user_name"] is not None:
            user.user_name = data["user_name"].strip()

        if "user_photo" in data:
            user.user_photo = str(data["user_photo"]) if data["user_photo"] is not None else None
            
        if "user_email" in data and data["user_email"] is not None:
            user.user_email = str(data["user_email"])

        if payload.user_phone_number is not None:
            user.user_phone_number = to_e164(payload.user_phone_number)

        if "password" in data and data["password"] is not None:
            user.user_password_hash = hash_password(data["password"])

        
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise UserConflictError()

    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        await db.delete(user)
        await db.commit()
        return True
    
    async def list_user_pets(self, db: AsyncSession, user_id: int) -> list[PetInfo]:
        user_pet = await db.execute(
            select(PetInfo)
            .join(SharedUser, SharedUser.shared_pet_id == PetInfo.id)
            .where(*active_shared_access_clause(user_id))
        )
        return list(user_pet.scalars().all())
