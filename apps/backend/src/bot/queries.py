from typing import Any

from aiogram.types import Message
from sqlalchemy import select

from src.core.db import AsyncSessionLocal
from src.models import AnimalBreed, AnimalType, PetInfo, SharedUser, UserInfo
from src.service.auth import AuthService
from src.service.pets import active_shared_access_clause
from src.service.sharing import SharingService


auth_service = AuthService()
sharing_service = SharingService()


def _build_photo_url(message: Message) -> str | None:
    if message.from_user is None:
        return None
    photo_url = getattr(message.from_user, "photo_url", None)
    if photo_url is None:
        return None
    return str(photo_url)


async def ensure_telegram_user(message: Message) -> tuple[UserInfo, bool]:
    if message.from_user is None:
        raise ValueError("Telegram user is missing from the update")

    async with AsyncSessionLocal() as db:
        return await auth_service.get_or_create_telegram_user(
            db=db,
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            photo_url=_build_photo_url(message),
        )


async def get_user_pet_names(user_id: int) -> list[str]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PetInfo.pet_name)
            .where(PetInfo.user_id == user_id)
            .order_by(PetInfo.id)
        )
        return list(result.scalars().all())


async def get_shared_pet_names(user_id: int) -> list[str]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PetInfo.pet_name)
            .join(SharedUser, SharedUser.shared_pet_id == PetInfo.id)
            .where(*active_shared_access_clause(user_id))
            .order_by(PetInfo.id)
        )
        return list(result.scalars().all())


async def get_shared_users_for_pet(pet_id: int) -> list[tuple[int, str]]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserInfo.id, UserInfo.user_name)
            .join(SharedUser, SharedUser.shared_user_id == UserInfo.id)
            .where(*active_shared_access_clause(pet_id=pet_id))
            .order_by(UserInfo.id)
        )
        return [(row[0], row[1]) for row in result.all()]


async def get_animal_types() -> list[AnimalType]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AnimalType).order_by(AnimalType.id))
        return list(result.scalars().all())


async def get_animal_breeds() -> list[AnimalBreed]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AnimalBreed).order_by(AnimalBreed.id))
        return list(result.scalars().all())


async def get_pet_details_row(user_id: int, pet_name: str) -> Any:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PetInfo, AnimalType, AnimalBreed)
            .join(AnimalType, AnimalType.id == PetInfo.animal_type_id)
            .join(AnimalBreed, AnimalBreed.id == PetInfo.animal_breed_id)
            .where(
                PetInfo.pet_name == pet_name,
                (
                    (PetInfo.user_id == user_id)
                    | (
                        PetInfo.id.in_(
                            select(SharedUser.shared_pet_id).where(
                                *active_shared_access_clause(user_id)
                            )
                        )
                    )
                ),
            )
        )
        return result.first()


async def pet_has_active_shared_users(pet_id: int) -> bool:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SharedUser).where(*active_shared_access_clause(pet_id=pet_id))
        )
        return result.first() is not None
