from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.constants import DELETE_PET_BUTTON_TEXT
from src.bot.keyboards import main_menu_keyboard, yes_no_keyboard
from src.bot.queries import ensure_telegram_user
from src.bot.selected_pet import get_selected_owned_pet_id
from src.bot.states import DeletePetStates
from src.bot.texts import YES_NO_REQUIRED_TEXT
from src.bot.utils import parse_bool
from src.core.db import AsyncSessionLocal
from src.service import PetsService
from src.service.storage import StorageService


router = Router()
pets_service = PetsService()
storage_service = StorageService()


@router.message(F.text == DELETE_PET_BUTTON_TEXT)
async def delete_pet_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        return

    await state.set_state(DeletePetStates.confirmation)
    await message.answer(
        "Удалить питомца? Будут удалены карточка питомца, фото и документы. Ответьте: да / нет.",
        reply_markup=yes_no_keyboard,
    )


@router.message(DeletePetStates.confirmation)
async def delete_pet_confirmation_handler(message: Message, state: FSMContext) -> None:
    decision = parse_bool(message.text)
    if decision is None:
        await message.answer(YES_NO_REQUIRED_TEXT, reply_markup=yes_no_keyboard)
        return

    if not decision:
        await state.clear()
        await message.answer("Удаление питомца отменено.", reply_markup=main_menu_keyboard)
        return

    selected_pet_id = await get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        await state.clear()
        return

    user, _ = await ensure_telegram_user(message)
    async with AsyncSessionLocal() as db:
        try:
            object_keys = await pets_service.list_pet_object_keys_for_cleanup(db, selected_pet_id, user.id)
            await pets_service.delete_pet(db, selected_pet_id, user.id)
        except Exception:
            await message.answer("Не удалось удалить питомца. Попробуйте снова позже.", reply_markup=main_menu_keyboard)
            return

    failed_cleanup = await storage_service.delete_objects_quietly(object_keys)

    await state.clear()
    if failed_cleanup:
        await message.answer(
            "Питомец удалён, но часть файлов в хранилище удалить не удалось. Проверьте хранилище позже.",
            reply_markup=main_menu_keyboard,
        )
        return

    await message.answer("Питомец удалён.", reply_markup=main_menu_keyboard)
