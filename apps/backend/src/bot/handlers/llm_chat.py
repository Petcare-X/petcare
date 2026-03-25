from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from fastapi import HTTPException

from src.bot.constants import (
    BACK_TO_PROFILE_BUTTON_TEXT,
    LLM_CHAT_BUTTON_TEXT,
    NEW_LLM_CHAT_BUTTON_TEXT,
)
from src.bot.flows import show_profile, start_llm_chat
from src.bot.keyboards import llm_chat_keyboard
from src.bot.queries import ensure_telegram_user
from src.bot.states import LlmChatStates
from src.bot.utils import normalize_text
from src.core.db import AsyncSessionLocal
from src.service import LLMChatService


router = Router()
chat_service = LLMChatService()


async def _ensure_active_chat_id(message, state: FSMContext, *, force_new: bool = False) -> int:
    user, _ = await ensure_telegram_user(message)
    state_data = await state.get_data()
    active_chat_id = state_data.get("active_llm_chat_id")

    async with AsyncSessionLocal() as db:
        if not force_new and active_chat_id is not None:
            try:
                chat = await chat_service._get_user_chat(db, user.id, int(active_chat_id))
                return chat.id
            except HTTPException:
                await state.update_data(active_llm_chat_id=None)

        if not force_new:
            chats = await chat_service.get_user_chats(db, user.id)
            if chats:
                chat = max(chats, key=lambda item: item.id)
                await state.update_data(active_llm_chat_id=chat.id)
                return chat.id

        chat = await chat_service.create_chat(db, user.id, "Telegram Chat")
        await state.update_data(active_llm_chat_id=chat.id)
        return chat.id


@router.message(Command("ai"))
async def ai_command_handler(message, state: FSMContext) -> None:
    await start_llm_chat(message, state)


@router.message(F.text == NEW_LLM_CHAT_BUTTON_TEXT)
async def new_llm_chat_button_handler(message, state: FSMContext) -> None:
    await state.set_state(LlmChatStates.message)
    await _ensure_active_chat_id(message, state, force_new=True)
    await message.answer(
        "Новый чат с ИИ создан. Напишите сообщение.",
        reply_markup=llm_chat_keyboard,
    )


@router.message(LlmChatStates.message)
async def llm_chat_message_handler(message, state: FSMContext) -> None:
    text = normalize_text(getattr(message, "text", None))

    if text in {BACK_TO_PROFILE_BUTTON_TEXT}:
        await state.clear()
        await show_profile(message)
        return

    if text == LLM_CHAT_BUTTON_TEXT:
        await start_llm_chat(message, state)
        return

    if text == NEW_LLM_CHAT_BUTTON_TEXT:
        await new_llm_chat_button_handler(message, state)
        return

    if not text:
        await message.answer(
            "Отправьте текстовое сообщение для ИИ.",
            reply_markup=llm_chat_keyboard,
        )
        return

    user, _ = await ensure_telegram_user(message)
    thinking_message = await message.answer(
        "думаю над вашим вопросом...",
        reply_markup=llm_chat_keyboard,
    )

    try:
        chat_id = await _ensure_active_chat_id(message, state)
        async with AsyncSessionLocal() as db:
            _user_message, assistant_message = await chat_service.send_message(
                db=db,
                user_id=user.id,
                chat_id=chat_id,
                content=text,
            )
    except Exception:
        try:
            await thinking_message.delete()
        except Exception:
            pass
        await message.answer(
            "Не удалось получить ответ от ИИ. Попробуйте ещё раз.",
            reply_markup=llm_chat_keyboard,
        )
        return

    try:
        await thinking_message.delete()
    except Exception:
        pass

    await message.answer(
        assistant_message.content,
        reply_markup=llm_chat_keyboard,
    )
