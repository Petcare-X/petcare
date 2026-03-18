from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from src.bot.constants import (
    ACCEPT_INVITE_BUTTON_TEXT,
    ADD_PET_BUTTON_TEXT,
    BACK_TO_PROFILE_BUTTON_TEXT,
    PROFILE_BUTTON_TEXT,
    REVOKE_ACCESS_BUTTON_TEXT,
    SHARE_PET_BUTTON_TEXT,
)
from src.bot.flows import show_profile, start_add_pet_registration
from src.bot.keyboards import build_pet_details_keyboard, build_shared_users_keyboard, main_menu_keyboard
from src.bot.queries import ensure_telegram_user, get_shared_users_for_pet, pet_has_active_shared_users, sharing_service
from src.bot.states import AcceptInviteStates, RevokeAccessStates
from src.bot.utils import normalize_text, parse_shared_user_id
from src.core.db import AsyncSessionLocal
from src.exceptions import InviteNotFoundError
from src.schemas.sharing import InviteCreate


router = Router()


@router.message(F.text == SHARE_PET_BUTTON_TEXT)
async def share_pet_button_handler(message, state: FSMContext) -> None:
    user, _ = await ensure_telegram_user(message)
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    selected_pet_owner_id = data.get("selected_pet_owner_id")
    if not selected_pet_id:
        await message.answer("Сначала откройте карточку питомца.", reply_markup=main_menu_keyboard)
        return
    if selected_pet_owner_id != user.id:
        await message.answer("Поделиться можно только своим питомцем.", reply_markup=main_menu_keyboard)
        return

    async with AsyncSessionLocal() as db:
        payload = InviteCreate(
            pet_id=selected_pet_id,
            max_uses=1,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        invite = await sharing_service.create_invite(user.id, db, payload)

    await message.answer(
        "\n".join(
            [
                "Код доступа к питомцу создан.",
                f"Код: {invite.invite_code}",
                "Передайте этот код другому пользователю бота.",
            ]
        ),
        reply_markup=build_pet_details_keyboard(
            can_share=True,
            can_revoke=await pet_has_active_shared_users(selected_pet_id),
        ),
    )


@router.message(F.text == REVOKE_ACCESS_BUTTON_TEXT)
async def revoke_access_button_handler(message, state: FSMContext) -> None:
    user, _ = await ensure_telegram_user(message)
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    selected_pet_owner_id = data.get("selected_pet_owner_id")
    if not selected_pet_id:
        await message.answer("Сначала откройте карточку питомца.", reply_markup=main_menu_keyboard)
        return
    if selected_pet_owner_id != user.id:
        await message.answer("Отзывать доступ может только владелец питомца.", reply_markup=main_menu_keyboard)
        return

    shared_users = await get_shared_users_for_pet(selected_pet_id)
    if not shared_users:
        await message.answer("У этого питомца сейчас нет пользователей с доступом.", reply_markup=main_menu_keyboard)
        return

    await state.set_state(RevokeAccessStates.shared_user)
    await message.answer(
        "Выберите пользователя, у которого нужно отозвать доступ.",
        reply_markup=build_shared_users_keyboard(shared_users),
    )


async def _handle_accept_invite_navigation(message, state: FSMContext, invite_code: str) -> bool:
    if invite_code in {PROFILE_BUTTON_TEXT, BACK_TO_PROFILE_BUTTON_TEXT}:
        await state.clear()
        await show_profile(message)
        return True
    if invite_code == ADD_PET_BUTTON_TEXT:
        await start_add_pet_registration(message, state)
        return True
    if invite_code == ACCEPT_INVITE_BUTTON_TEXT:
        await message.answer("Введите код доступа к питомцу.", reply_markup=main_menu_keyboard)
        return True
    return False


@router.message(AcceptInviteStates.invite_code)
async def accept_invite_handler(message, state: FSMContext) -> None:
    invite_code = normalize_text(message.text)
    if not invite_code:
        await message.answer("Введите код доступа.")
        return
    if await _handle_accept_invite_navigation(message, state, invite_code):
        return

    user, _ = await ensure_telegram_user(message)
    async with AsyncSessionLocal() as db:
        try:
            await sharing_service.accept_invite(db, invite_code, user.id)
        except InviteNotFoundError:
            await message.answer("Такой код не найден. Проверьте код и попробуйте снова.")
            return

    await state.clear()
    await message.answer(
        "Доступ к питомцу успешно получен. Откройте профиль, чтобы увидеть питомца.",
        reply_markup=main_menu_keyboard,
    )


@router.message(RevokeAccessStates.shared_user)
async def revoke_access_handler(message, state: FSMContext) -> None:
    user, _ = await ensure_telegram_user(message)
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    if not selected_pet_id:
        await state.clear()
        await message.answer("Не удалось определить питомца.", reply_markup=main_menu_keyboard)
        return

    shared_user_id = parse_shared_user_id(message.text)
    if shared_user_id is None:
        await message.answer("Выберите пользователя кнопкой.")
        return

    async with AsyncSessionLocal() as db:
        await sharing_service.revoke_access(
            db=db,
            user_id=user.id,
            pet_id=selected_pet_id,
            shared_user_id=shared_user_id,
        )

    await state.clear()
    await message.answer("Доступ к питомцу отозван.", reply_markup=main_menu_keyboard)
