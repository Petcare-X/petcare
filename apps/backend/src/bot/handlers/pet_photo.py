from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.constants import DELETE_PET_PHOTO_BUTTON_TEXT, UPDATE_PET_PHOTO_BUTTON_TEXT
from src.bot.keyboards import main_menu_keyboard, registration_navigation_keyboard
from src.bot.queries import ensure_telegram_user
from src.bot.selected_pet import get_selected_owned_pet_id
from src.bot.states import UpdatePetPhotoStates
from src.bot.telegram_media import download_telegram_file_bytes
from src.core.db import AsyncSessionLocal
from src.exceptions import AppError
from src.service import PetPhotoService, PetsService


router = Router()
pets_service = PetsService()
pet_photo_service = PetPhotoService()


@router.message(F.text == UPDATE_PET_PHOTO_BUTTON_TEXT)
async def update_pet_photo_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        return
    await state.set_state(UpdatePetPhotoStates.photo)
    await message.answer(
        "Отправьте новое фото питомца сообщением.",
        reply_markup=registration_navigation_keyboard,
    )


@router.message(F.text == DELETE_PET_PHOTO_BUTTON_TEXT)
async def delete_pet_photo_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        return

    user, _ = await ensure_telegram_user(message)
    async with AsyncSessionLocal() as db:
        pet = await pets_service.ensure_pet_owner(db, selected_pet_id, user.id)
        if pets_service.photo_snapshot(pet) is None:
            await message.answer("У питомца и так нет фото.", reply_markup=main_menu_keyboard)
            return
        try:
            await pet_photo_service.delete_photo(db, pet_id=selected_pet_id, user_id=user.id)
        except AppError:
            await message.answer(
                "Не удалось удалить фото из хранилища. Изменения отменены.",
                reply_markup=main_menu_keyboard,
            )
            return

    await message.answer("Фото питомца удалено.", reply_markup=main_menu_keyboard)


@router.message(UpdatePetPhotoStates.photo)
async def update_pet_photo_handler(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer(
            "Пришлите фото сообщением.",
            reply_markup=registration_navigation_keyboard,
        )
        return

    selected_pet_id = await get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        await state.clear()
        return

    user, _ = await ensure_telegram_user(message)
    try:
        payload = await download_telegram_file_bytes(message.bot, message.photo[-1].file_id)
    except ValueError as exc:
        await message.answer(str(exc))
        return

    content_type = "image/jpeg"
    async with AsyncSessionLocal() as db:
        try:
            await pet_photo_service.replace_photo_with_bytes(
                db,
                pet_id=selected_pet_id,
                user_id=user.id,
                payload=payload,
                content_type=content_type,
            )
        except AppError:
            await message.answer("Не удалось сохранить фото питомца. Изменения отменены.")
            return

    await state.set_state(None)
    await message.answer("Фото питомца обновлено.", reply_markup=main_menu_keyboard)
