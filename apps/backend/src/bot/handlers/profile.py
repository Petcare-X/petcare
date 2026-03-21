from io import BytesIO

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from src.bot.constants import (
    DELETE_PET_PHOTO_BUTTON_TEXT,
    RESERVED_MESSAGE_TEXTS,
    UPDATE_PET_PHOTO_BUTTON_TEXT,
)
from src.bot.flows import show_profile
from src.bot.formatters import format_pet_details_message
from src.bot.keyboards import (
    build_pet_details_keyboard,
    main_menu_keyboard,
    registration_navigation_keyboard,
)
from src.bot.queries import (
    ensure_telegram_user,
    get_pet_details_row,
    pet_has_active_shared_users,
)
from src.bot.states import UpdatePetPhotoStates
from src.core.db import AsyncSessionLocal
from src.service import PetsService
from src.service.storage import StorageService


router = Router()
pets_service = PetsService()
storage_service = StorageService()


async def _get_selected_owned_pet_id(message: Message, state: FSMContext) -> int | None:
    user, _ = await ensure_telegram_user(message)
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    selected_pet_owner_id = data.get("selected_pet_owner_id")
    if not selected_pet_id:
        await message.answer("Сначала откройте карточку питомца.", reply_markup=main_menu_keyboard)
        return None
    if selected_pet_owner_id != user.id:
        await message.answer("Эта операция доступна только владельцу питомца.", reply_markup=main_menu_keyboard)
        return None
    return int(selected_pet_id)


@router.message(Command("me"))
async def me_handler(message) -> None:
    await show_profile(message)


@router.message(F.text == UPDATE_PET_PHOTO_BUTTON_TEXT)
async def update_pet_photo_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await _get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        return
    await state.set_state(UpdatePetPhotoStates.photo)
    await message.answer(
        "Отправьте новое фото питомца сообщением.",
        reply_markup=registration_navigation_keyboard,
    )


@router.message(F.text == DELETE_PET_PHOTO_BUTTON_TEXT)
async def delete_pet_photo_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await _get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        return

    user, _ = await ensure_telegram_user(message)
    async with AsyncSessionLocal() as db:
        pet = await pets_service.ensure_pet_owner(db, selected_pet_id, user.id)
        snapshot = pets_service.photo_snapshot(pet)
        await pets_service.clear_pet_photo(db, selected_pet_id, user.id)

    if snapshot is None:
        await message.answer("У питомца и так нет фото.", reply_markup=main_menu_keyboard)
        return

    try:
        await storage_service.delete_object(snapshot.object_key)
    except Exception:
        async with AsyncSessionLocal() as db:
            await pets_service.restore_pet_photo(db, selected_pet_id, user.id, snapshot)
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

    selected_pet_id = await _get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        await state.clear()
        return

    user, _ = await ensure_telegram_user(message)
    tg_photo = message.photo[-1]
    tg_file = await message.bot.get_file(tg_photo.file_id)
    if not tg_file.file_path:
        await message.answer("Не удалось получить файл из Telegram. Попробуйте снова.")
        return

    destination = BytesIO()
    await message.bot.download_file(tg_file.file_path, destination=destination)
    payload = destination.getvalue()
    if not payload:
        await message.answer("Не удалось скачать фото из Telegram. Попробуйте снова.")
        return

    content_type = "image/jpeg"
    object_key = storage_service.build_pet_photo_object_key(
        user_id=user.id,
        pet_id=selected_pet_id,
        content_type=content_type,
    )
    put_result = await storage_service.upload_bytes(
        object_key=object_key,
        payload=payload,
        content_type=content_type,
    )
    etag_raw = put_result.get("ETag")
    etag = str(etag_raw).strip('"') if etag_raw is not None else None

    async with AsyncSessionLocal() as db:
        pet = await pets_service.ensure_pet_owner(db, selected_pet_id, user.id)
        previous_snapshot = pets_service.photo_snapshot(pet)
        previous_key = previous_snapshot.object_key if previous_snapshot else None
        try:
            await pets_service.set_pet_photo_metadata(
                db,
                selected_pet_id,
                user.id,
                object_key=object_key,
                content_type=content_type,
                size_bytes=len(payload),
                etag=etag,
                uploaded_at=storage_service.now_utc(),
            )
        except Exception:
            await storage_service.delete_object(object_key)
            await message.answer("Не удалось сохранить фото питомца. Изменения отменены.")
            return

        if previous_key and previous_key != object_key:
            try:
                await storage_service.delete_object(previous_key)
            except Exception:
                await pets_service.restore_pet_photo(db, selected_pet_id, user.id, previous_snapshot)
                await storage_service.delete_object(object_key)
                await message.answer("Не удалось обновить фото в хранилище. Изменения отменены.")
                return

    await state.set_state(None)
    await message.answer("Фото питомца обновлено.", reply_markup=main_menu_keyboard)


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
    pet_details_text = format_pet_details_message(
        pet,
        animal_type_name=animal_type.animal_name,
        animal_breed_name=animal_breed.animal_breed,
    )
    reply_markup = build_pet_details_keyboard(
        can_share=is_owner,
        can_revoke=can_revoke,
        can_manage_photo=is_owner,
    )

    if pet.pet_photo_object_key:
        try:
            payload, _ = await storage_service.download_bytes(pet.pet_photo_object_key)
            filename = pet.pet_photo_object_key.rsplit("/", 1)[-1] or f"pet-{pet.id}.jpg"
            await message.answer_photo(
                photo=BufferedInputFile(payload, filename=filename),
                caption=pet_details_text,
                reply_markup=reply_markup,
            )
            return
        except Exception:
            pass

    await message.answer(
        pet_details_text,
        reply_markup=reply_markup,
    )
