from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.models.user_info import UserInfo
from src.schemas.users import CreateUser, UpdateContactsUser, UpdateDataUser

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from src.core.phone import to_e164

# read
async def get_user_by_id(db: AsyncSession, user_id: int) -> UserInfo | None:
    return await db.get(UserInfo, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> UserInfo | None:
    res = await db.execute(select(UserInfo).where(UserInfo.user_email == email))
    return res.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str) -> UserInfo | None:
    res = await db.execute(select(UserInfo).where(UserInfo.user_phone == phone))
    return res.scalar_one_or_none()


async def list_users(db: AsyncSession, offset: int = 0, limit: int = 50) -> list[UserInfo]:
    res = await db.execute(select(UserInfo).offset(offset).limit(limit))
    return list(res.scalars().all())


# create
async def create_user(db: AsyncSession, payload: CreateUser) -> UserInfo:
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
        return True
    except IntegrityError as e:
        await db.rollback()
        orig = getattr(e, "orig", None)
        sqlstate = getattr(orig, "sqlstate", None)
        constraint = getattr(orig, "constraint_name", None)
        msg = str(orig)

        if sqlstate == "23514":
            raise HTTPException(
                status_code=400,
                detail=f"CHECK constraint failed: {constraint or 'unknown'} | {msg}"
            )
        raise

# update profile data
async def update_user_data(db: AsyncSession, user_id: int, payload: UpdateDataUser) -> UserInfo | None:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    data = payload.model_dump(exclude_unset=True)

    if "name" in data and data["name"] is not None:
        user.user_name = data["name"].strip()

    if "photo_url" in data and data["photo_url"] is not None:
        user.user_photo = str(data["photo_url"])

    await db.commit()
    await db.refresh(user)
    return user


# update contacts
async def update_user_contacts(db: AsyncSession, user_id: int, payload: UpdateContactsUser) -> UserInfo | None:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    data = payload.model_dump(exclude_unset=True)

    if "email" in data and data["email"] is not None:
        user.user_email = str(data["email"])

    if payload.phone_number is not None:
        user.user_phone = to_e164(payload.phone_number)

    if "password" in data and data["password"] is not None:
        user.user_password_hash = hash_password(data["password"])

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("Email or phone already exists")

    await db.refresh(user)
    return user


# delete
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False

    await db.delete(user)
    await db.commit()
    return True