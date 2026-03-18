from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.constants import RESERVED_MESSAGE_TEXTS
from src.bot.flows import show_profile
from src.bot.formatters import format_pet_details_message
from src.bot.keyboards import build_pet_details_keyboard
from src.bot.queries import ensure_telegram_user, get_pet_details_row, pet_has_active_shared_users


router = Router()


@router.message(Command("me"))
async def me_handler(message) -> None:
    await show_profile(message)


@router.message()
async def pet_details_handler(message, state: FSMContext) -> None:
    if not message.text or message.text in RESERVED_MESSAGE_TEXTS:
        return

    user, _ = await ensure_telegram_user(message)
    pet_row = await get_pet_details_row(user.id, message.text)
    if pet_row is None:
        return

    pet, animal_type, animal_breed = pet_row
    is_owner = pet.user_id == user.id
    can_revoke = is_owner and await pet_has_active_shared_users(pet.id)

    await state.update_data(selected_pet_id=pet.id, selected_pet_owner_id=pet.user_id)
    await message.answer(
        format_pet_details_message(
            pet,
            animal_type_name=animal_type.animal_name,
            animal_breed_name=animal_breed.animal_breed,
        ),
        reply_markup=build_pet_details_keyboard(
            can_share=is_owner,
            can_revoke=can_revoke,
        ),
    )
