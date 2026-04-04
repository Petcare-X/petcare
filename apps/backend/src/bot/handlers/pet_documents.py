from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from src.bot.constants import ADD_PET_DOCUMENT_BUTTON_TEXT, DELETE_PET_DOCUMENT_BUTTON_TEXT, SHOW_PET_DOCUMENTS_BUTTON_TEXT
from src.bot.keyboards import (
    build_document_types_keyboard,
    build_pet_documents_actions_keyboard,
    build_pet_documents_keyboard,
    main_menu_keyboard,
    registration_navigation_keyboard,
)
from src.bot.queries import ensure_telegram_user, get_document_types
from src.bot.selected_pet import can_manage_selected_pet_documents, get_selected_owned_pet_id, get_selected_pet_id
from src.bot.states import AddPetDocumentStates, DeletePetDocumentStates
from src.bot.telegram_media import download_telegram_file_bytes
from src.bot.utils import normalize_text, parse_document_row_id
from src.core.db import AsyncSessionLocal
from src.exceptions import AppError
from src.service import PetDocumentFilesService, PetDocumentsService
from src.service.storage import StorageService


router = Router()
pet_documents_service = PetDocumentsService()
pet_document_files_service = PetDocumentFilesService()
storage_service = StorageService()


async def _get_document_type_name_map() -> dict[int, str]:
    document_types = await get_document_types()
    return {doc_type.id: doc_type.document_name for doc_type in document_types}


def _document_filename_from_object_key(object_key: str, document_id: int) -> str:
    return object_key.rsplit("/", 1)[-1] or f"document-{document_id}"


@router.message(F.text == SHOW_PET_DOCUMENTS_BUTTON_TEXT)
async def show_pet_documents_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await get_selected_pet_id(message, state)
    if selected_pet_id is None:
        return
    can_manage_documents = await can_manage_selected_pet_documents(message, state)

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
            await message.answer_document(
                document=BufferedInputFile(payload, filename=filename),
                caption=f"Тип: {type_name}",
            )
            sent_count += 1
        except AppError:
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
    selected_pet_id = await get_selected_owned_pet_id(message, state)
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

    selected_pet_id = await get_selected_owned_pet_id(message, state)
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
    try:
        payload = await download_telegram_file_bytes(message.bot, message.document.file_id)
    except ValueError as exc:
        await message.answer(str(exc))
        return

    content_type = message.document.mime_type or "application/octet-stream"

    async with AsyncSessionLocal() as db:
        try:
            doc = await pet_document_files_service.create_from_bytes(
                db,
                pet_id=selected_pet_id,
                user_id=user.id,
                document_type_id=int(document_type_id),
                payload=payload,
                content_type=content_type,
            )
        except AppError:
            await message.answer(
                "Не удалось сохранить документ. Изменения отменены.",
                reply_markup=main_menu_keyboard,
            )
            return

    await state.clear()
    await message.answer(
        f"Документ сохранён.\nТип: {document_types_map.get(str(doc.document_type_id), str(doc.document_type_id))}",
        reply_markup=build_pet_documents_actions_keyboard(can_manage_documents=True),
    )


@router.message(F.text == DELETE_PET_DOCUMENT_BUTTON_TEXT)
async def delete_pet_document_button_handler(message: Message, state: FSMContext) -> None:
    selected_pet_id = await get_selected_owned_pet_id(message, state)
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
    selected_pet_id = await get_selected_owned_pet_id(message, state)
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
        except AppError:
            await message.answer("Не удалось удалить документ. Попробуйте снова позже.", reply_markup=main_menu_keyboard)
            return

    await state.clear()
    await message.answer(
        "Документ удалён.",
        reply_markup=build_pet_documents_actions_keyboard(can_manage_documents=True),
    )
