from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .formatters import format_profile_message
from .keyboards import (
    build_profile_keyboard,
    llm_chat_keyboard,
    main_menu_keyboard,
    registration_navigation_keyboard,
)
from .queries import ensure_telegram_user, get_shared_pet_names, get_user_pet_names
from .states import AcceptInviteStates, AddPetStates, LlmChatStates


async def show_profile(message: Message) -> None:
    user, _ = await ensure_telegram_user(message)
    pet_names = await get_user_pet_names(user.id)
    shared_pet_names = await get_shared_pet_names(user.id)
    profile_pet_names = pet_names + [
        pet_name for pet_name in shared_pet_names if pet_name not in pet_names
    ]

    await message.answer(
        format_profile_message(
            user_name=user.user_name,
            pet_names=pet_names,
            shared_pet_names=shared_pet_names,
        ),
        reply_markup=build_profile_keyboard(profile_pet_names),
    )


async def start_add_pet_registration(message: Message, state: FSMContext) -> None:
    user, _ = await ensure_telegram_user(message)
    await state.clear()
    await state.update_data(user_id=user.id)
    await state.set_state(AddPetStates.pet_name)
    await message.answer(
        "Начинаем регистрацию питомца.\n"
        "Введите кличку питомца.",
        reply_markup=registration_navigation_keyboard,
    )


async def start_accept_invite(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AcceptInviteStates.invite_code)
    await message.answer("Введите код доступа к питомцу.", reply_markup=main_menu_keyboard)


async def start_llm_chat(message: Message, state: FSMContext) -> None:
    await state.set_state(LlmChatStates.message)
    await message.answer(
        "Напишите сообщение для ИИ.\n"
        "Можно продолжить текущий чат или создать новый кнопкой ниже.",
        reply_markup=llm_chat_keyboard,
    )
