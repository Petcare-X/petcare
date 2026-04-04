from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.keyboards import main_menu_keyboard
from src.bot.queries import ensure_telegram_user
from src.bot.texts import OPEN_PET_CARD_FIRST_TEXT, PET_OWNER_ONLY_TEXT


async def get_selected_owned_pet_id(message: Message, state: FSMContext) -> int | None:
    user, _ = await ensure_telegram_user(message)
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    selected_pet_owner_id = data.get("selected_pet_owner_id")
    if not selected_pet_id:
        await message.answer(OPEN_PET_CARD_FIRST_TEXT, reply_markup=main_menu_keyboard)
        return None
    if selected_pet_owner_id != user.id:
        await message.answer(PET_OWNER_ONLY_TEXT, reply_markup=main_menu_keyboard)
        return None
    return int(selected_pet_id)


async def get_selected_pet_id(message: Message, state: FSMContext) -> int | None:
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    if not selected_pet_id:
        await message.answer(OPEN_PET_CARD_FIRST_TEXT, reply_markup=main_menu_keyboard)
        return None
    return int(selected_pet_id)


async def can_manage_selected_pet_documents(message: Message, state: FSMContext) -> bool:
    user, _ = await ensure_telegram_user(message)
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    selected_pet_owner_id = data.get("selected_pet_owner_id")
    return bool(selected_pet_id and selected_pet_owner_id == user.id)
