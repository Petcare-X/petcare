from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from src.bot.constants import (
    ACCEPT_INVITE_BUTTON_TEXT,
    ADD_PET_BUTTON_TEXT,
    BACK_TO_PROFILE_BUTTON_TEXT,
    LLM_CHAT_BUTTON_TEXT,
    PROFILE_BUTTON_TEXT,
)
from src.bot.flows import show_profile, start_accept_invite, start_add_pet_registration, start_llm_chat


router = Router()


@router.message(F.text == PROFILE_BUTTON_TEXT)
async def profile_button_handler(message, state: FSMContext) -> None:
    await state.clear()
    await show_profile(message)


@router.message(F.text == BACK_TO_PROFILE_BUTTON_TEXT)
async def back_to_profile_button_handler(message, state: FSMContext) -> None:
    await state.clear()
    await show_profile(message)


@router.message(F.text == ADD_PET_BUTTON_TEXT)
async def add_pet_button_handler(message, state: FSMContext) -> None:
    await start_add_pet_registration(message, state)


@router.message(F.text == ACCEPT_INVITE_BUTTON_TEXT)
async def accept_invite_button_handler(message, state: FSMContext) -> None:
    await start_accept_invite(message, state)


@router.message(F.text == LLM_CHAT_BUTTON_TEXT)
async def llm_chat_button_handler(message, state: FSMContext) -> None:
    await start_llm_chat(message, state)
