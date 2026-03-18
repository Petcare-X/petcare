from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.models import UserInfo, SharedUser, PetInfo
from src.schemas import CreateUser, UpdateUser, UpdateUserContacts

from fastapi import HTTPException
from datetime import datetime, timezone

from src.core.phone import to_e164

class UsersService:
    # create
    async def create_user(self, db: AsyncSession, payload: CreateUser) -> UserInfo:
        phone_str = to_e164(payload.phone_number)
        photo_str = str(payload.photo_url)

        user = UserInfo(
            user_name=payload.name.strip(),
            user_email=str(payload.email),
            user_phone=phone_str,
            user_password_hash=hash_password(payload.password),
            user_date_of_birth=payload.birth_date,
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

            # duplicate email / phone
            if sqlstate == "23505":
                if constraint and "email" in constraint:
                    raise HTTPException(
                        status_code=409,
                        detail="User with this email already exists"
                    )
                if constraint and "phone" in constraint:
                    raise HTTPException(
                        status_code=409,
                        detail="User with this phone number already exists"
                    )

            # check constraint (например формат телефона)
            if sqlstate == "23514":
                raise HTTPException(
                    status_code=400,
                    detail=f"CHECK constraint failed: {constraint or 'unknown'}"
                )

            raise HTTPException(
                status_code=400,
                detail=f"Database integrity error: {msg}"
            )
    
    # read
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> UserInfo | None:
        return await db.get(UserInfo, user_id)


    async def get_user_by_email(self, db: AsyncSession, email: str) -> UserInfo | None:
        res = await db.execute(select(UserInfo).where(UserInfo.user_email == email))
        return res.scalar_one_or_none()


    async def get_user_by_phone(self, db: AsyncSession, phone: str) -> UserInfo | None:
        res = await db.execute(select(UserInfo).where(UserInfo.user_phone == phone))
        return res.scalar_one_or_none()


    async def list_all_users(self, db: AsyncSession, offset: int = 0, limit: int = 50) -> list[UserInfo]:
        res = await db.execute(select(UserInfo).offset(offset).limit(limit))
        return list(res.scalars().all())

    # update profile data
    async def update_user(self, user_id: int, payload: UpdateUser, db: AsyncSession) -> UserInfo | None:
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None

        data = payload.model_dump(exclude_unset=True)

        if "name" in data and data["name"] is not None:
            user.user_name = data["name"].strip()

        if "photo_url" in data and data["photo_url"] is not None:
            user.user_photo = str(data["photo_url"])
            
        if "email" in data and data["email"] is not None:
            user.user_email = str(data["email"])

        if payload.phone_number is not None:
            user.user_phone = to_e164(payload.phone_number)

        if "password" in data and data["password"] is not None:
            user.user_password_hash = hash_password(data["password"])

        
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise ValueError("Email or phone already exists")

    # delete
    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return False

        await db.delete(user)
        await db.commit()
        return True
    
    # вывод всех питомцев юзера из SharedUsers
    async def list_user_pets(self, db: AsyncSession, user_id: int) -> list[PetInfo]:
        now_utc = datetime.now(timezone.utc)
        user_pet = await db.execute(
                select(PetInfo).join(SharedUser).where(
                    SharedUser.shared_user_id == user_id and 
                    (not SharedUser.sharing_end or SharedUser.sharing_end > now_utc)))
        return list(user_pet.scalars().all())
    
    async def update_user_contacts(
        self,
        user_id: int,
        payload: UpdateUserContacts,
        db: AsyncSession,
    ) -> UserInfo | None:
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None

        data = payload.model_dump(exclude_unset=True)

        if "email" in data and data["email"] is not None:
            user.user_email = str(data["email"])

        if "phone_number" in data and data["phone_number"] is not None:
            user.user_phone = to_e164(data["phone_number"])

        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise ValueError("Email or phone already exists")
