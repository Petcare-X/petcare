from io import BytesIO

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from src.bot.constants import (
    ADD_PET_DOCUMENT_BUTTON_TEXT,
    DELETE_PET_DOCUMENT_BUTTON_TEXT,
    DELETE_PET_PHOTO_BUTTON_TEXT,
    RESERVED_MESSAGE_TEXTS,
    SHOW_PET_DOCUMENTS_BUTTON_TEXT,
    UPDATE_PET_PHOTO_BUTTON_TEXT,
)
from src.bot.flows import show_profile
from src.bot.formatters import format_pet_details_message
from src.bot.keyboards import (
    build_document_types_keyboard,
    build_pet_documents_actions_keyboard,
    build_pet_documents_keyboard,
    build_pet_details_keyboard,
    main_menu_keyboard,
    registration_navigation_keyboard,
)
from src.bot.queries import (
    ensure_telegram_user,
    get_document_types,
    get_pet_details_row,
    pet_has_active_shared_users,
)
from src.bot.states import AddPetDocumentStates, DeletePetDocumentStates, UpdatePetPhotoStates
from src.bot.utils import normalize_text, parse_document_row_id
from src.core.db import AsyncSessionLocal
from src.service import PetDocumentsService, PetsService
from src.service.storage import StorageService


router = Router()
pets_service = PetsService()
pet_documents_service = PetDocumentsService()
storage_service = StorageService()


async def _get_document_type_name_map() -> dict[int, str]:
    document_types = await get_document_types()
    return {doc_type.id: doc_type.document_name for doc_type in document_types}


def _document_filename_from_object_key(object_key: str, document_id: int) -> str:
    return object_key.rsplit("/", 1)[-1] or f"document-{document_id}"


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


async def _get_selected_pet_id(message: Message, state: FSMContext) -> int | None:
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    if not selected_pet_id:
        await message.answer("Сначала откройте карточку питомца.", reply_markup=main_menu_keyboard)
        return None
    return int(selected_pet_id)


async def _can_manage_selected_pet_documents(message: Message, state: FSMContext) -> bool:
    user, _ = await ensure_telegram_user(message)
    data = await state.get_data()
    selected_pet_id = data.get("selected_pet_id")
    selected_pet_owner_id = data.get("selected_pet_owner_id")
    return bool(selected_pet_id and selected_pet_owner_id == user.id)


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


@router.message(F.text == SHOW_PET_DOCUMENTS_BUTTON_TEXT)
async def show_pet_documents_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await _get_selected_pet_id(message, state)
    if selected_pet_id is None:
        return
    can_manage_documents = await _can_manage_selected_pet_documents(message, state)

    user, _ = await ensure_telegram_user(message)
    async with AsyncSessionLocal() as db:
        documents = await pet_documents_service.list_for_pet(db, selected_pet_id, user.id)

    if not documents:
        await message.answer(
            "У питомца пока нет документов.",
            reply_markup=build_pet_documents_actions_keyboard(
                can_manage_documents=can_manage_documents,
            ),
        )
        return

    document_type_names = await _get_document_type_name_map()
    sent_count = 0
    failed_count = 0
    for document in documents:
        try:
            payload, _ = await storage_service.download_bytes(document.object_key)
            filename = _document_filename_from_object_key(document.object_key, document.id)
            type_name = document_type_names.get(document.document_type_id, f"Тип #{document.document_type_id}")
            details = [f"Документ #{document.id}", f"Тип: {type_name}", f"Файл: {filename}"]
            if document.size_bytes is not None:
                details.append(f"Размер: {document.size_bytes} байт")
            await message.answer_document(
                document=BufferedInputFile(payload, filename=filename),
                caption="\n".join(details),
            )
            sent_count += 1
        except Exception:
            failed_count += 1

    if sent_count == 0:
        await message.answer(
            "Не удалось получить документы питомца из хранилища.",
            reply_markup=build_pet_documents_actions_keyboard(
                can_manage_documents=can_manage_documents,
            ),
        )
        return

    if failed_count:
        await message.answer(
            f"Отправлено документов: {sent_count}. Не удалось загрузить: {failed_count}.",
            reply_markup=build_pet_documents_actions_keyboard(
                can_manage_documents=can_manage_documents,
            ),
        )
        return

    await message.answer(
        f"Отправлено документов: {sent_count}.",
        reply_markup=build_pet_documents_actions_keyboard(
            can_manage_documents=can_manage_documents,
        ),
    )


@router.message(F.text == ADD_PET_DOCUMENT_BUTTON_TEXT)
async def add_pet_document_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await _get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        return

    document_types = await get_document_types()
    if not document_types:
        await message.answer("В системе пока нет типов документов.", reply_markup=main_menu_keyboard)
        return

    await state.set_state(AddPetDocumentStates.document_type_id)
    await state.update_data(
        pet_document_types={str(doc_type.id): doc_type.document_name for doc_type in document_types}
    )
    await message.answer(
        "Выберите тип документа кнопкой ниже.",
        reply_markup=build_document_types_keyboard(
            [(doc_type.id, doc_type.document_name) for doc_type in document_types]
        ),
    )


@router.message(AddPetDocumentStates.document_type_id)
async def add_pet_document_type_handler(message: Message, state: FSMContext) -> None:
    raw_value = normalize_text(message.text)
    document_types_map = (await state.get_data()).get("pet_document_types", {})
    document_type_id = next(
        (int(doc_id) for doc_id, name in document_types_map.items() if name.strip().lower() == raw_value.lower()),
        None,
    )
    if document_type_id is None:
        await message.answer("Выберите тип документа кнопкой.")
        return

    await state.update_data(selected_document_type_id=document_type_id)
    await state.set_state(AddPetDocumentStates.file)
    await message.answer(
        "Отправьте документ файлом сообщением.",
        reply_markup=registration_navigation_keyboard,
    )


@router.message(AddPetDocumentStates.file)
async def add_pet_document_file_handler(message: Message, state: FSMContext) -> None:
    if not message.document:
        await message.answer(
            "Пришлите документ именно файлом.",
            reply_markup=registration_navigation_keyboard,
        )
        return

    selected_pet_id = await _get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        await state.clear()
        return

    state_data = await state.get_data()
    document_type_id = state_data.get("selected_document_type_id")
    document_types_map = state_data.get("pet_document_types", {})
    if document_type_id is None:
        await state.clear()
        await message.answer("Не удалось определить тип документа. Начните заново.", reply_markup=main_menu_keyboard)
        return

    user, _ = await ensure_telegram_user(message)
    tg_document = message.document
    tg_file = await message.bot.get_file(tg_document.file_id)
    if not tg_file.file_path:
        await message.answer("Не удалось получить файл из Telegram. Попробуйте снова.")
        return

    destination = BytesIO()
    await message.bot.download_file(tg_file.file_path, destination=destination)
    payload = destination.getvalue()
    if not payload:
        await message.answer("Не удалось скачать документ из Telegram. Попробуйте снова.")
        return

    filename = tg_document.file_name or f"document-{tg_document.file_unique_id}"
    content_type = tg_document.mime_type or "application/octet-stream"
    object_key = storage_service.build_pet_document_object_key(
        user_id=user.id,
        pet_id=selected_pet_id,
        document_type_id=int(document_type_id),
        filename=filename,
        content_type=content_type,
    )

    try:
        await storage_service.upload_bytes(
            object_key=object_key,
            payload=payload,
            content_type=content_type,
        )
    except Exception:
        await message.answer("Не удалось загрузить документ в хранилище.", reply_markup=main_menu_keyboard)
        return

    async with AsyncSessionLocal() as db:
        try:
            doc = await pet_documents_service.create_after_upload(
                db,
                selected_pet_id,
                user.id,
                document_type_id=int(document_type_id),
                object_key=object_key,
            )
        except Exception:
            try:
                await storage_service.delete_object(object_key)
            except Exception:
                pass
            await message.answer("Не удалось сохранить документ. Изменения отменены.", reply_markup=main_menu_keyboard)
            return

    await state.clear()
    await message.answer(
        (
            f"Документ сохранён.\n"
            f"ID: {doc.id}\n"
            f"Тип: {document_types_map.get(str(doc.document_type_id), str(doc.document_type_id))}\n"
            f"Файл: {filename}"
        ),
        reply_markup=build_pet_documents_actions_keyboard(can_manage_documents=True),
    )


@router.message(F.text == DELETE_PET_DOCUMENT_BUTTON_TEXT)
async def delete_pet_document_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await _get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        return

    user, _ = await ensure_telegram_user(message)
    async with AsyncSessionLocal() as db:
        documents = await pet_documents_service.list_for_pet(db, selected_pet_id, user.id)

    if not documents:
        await message.answer("У питомца нет документов для удаления.", reply_markup=main_menu_keyboard)
        return

    document_type_names = await _get_document_type_name_map()
    await state.set_state(DeletePetDocumentStates.document_row_id)
    await message.answer(
        "Выберите документ для удаления.",
        reply_markup=build_pet_documents_keyboard(
            [
                (
                    doc.id,
                    f"{document_type_names.get(doc.document_type_id, f'Тип {doc.document_type_id}')}: "
                    f"{_document_filename_from_object_key(doc.object_key, doc.id)}",
                )
                for doc in documents
            ]
        ),
    )


@router.message(DeletePetDocumentStates.document_row_id)
async def delete_pet_document_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await _get_selected_owned_pet_id(message, state)
    if selected_pet_id is None:
        await state.clear()
        return

    document_row_id = parse_document_row_id(message.text)
    if document_row_id is None:
        await message.answer("Выберите документ кнопкой.")
        return

    user, _ = await ensure_telegram_user(message)
    async with AsyncSessionLocal() as db:
        try:
            await pet_documents_service.delete(db, selected_pet_id, document_row_id, user.id)
        except Exception:
            await message.answer("Не удалось удалить документ. Попробуйте снова позже.", reply_markup=main_menu_keyboard)
            return

    await state.clear()
    await message.answer(
        "Документ удалён.",
        reply_markup=build_pet_documents_actions_keyboard(can_manage_documents=True),
    )


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
