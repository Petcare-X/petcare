from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.models import AnimalBreed, AnimalType

from .constants import (
    ACCEPT_INVITE_BUTTON_TEXT,
    ADD_PET_BUTTON_TEXT,
    ADD_PET_DOCUMENT_BUTTON_TEXT,
    BACK_TO_PROFILE_BUTTON_TEXT,
    DELETE_PET_DOCUMENT_BUTTON_TEXT,
    DELETE_PET_BUTTON_TEXT,
    DELETE_PET_PHOTO_BUTTON_TEXT,
    LLM_CHAT_BUTTON_TEXT,
    NEW_LLM_CHAT_BUTTON_TEXT,
    NO_BREED_BUTTON_TEXT,
    NO_TEXT,
    PROFILE_BUTTON_TEXT,
    REVOKE_ACCESS_BUTTON_TEXT,
    SHOW_PET_DOCUMENTS_BUTTON_TEXT,
    SHARE_PET_BUTTON_TEXT,
    UPDATE_PET_PHOTO_BUTTON_TEXT,
    YES_TEXT,
)


def _button_row(*texts: str) -> list[KeyboardButton]:
    return [KeyboardButton(text=text) for text in texts]


def _keyboard(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[_button_row(*row) for row in rows],
        resize_keyboard=True,
    )


main_menu_keyboard = _keyboard(
    [
        [PROFILE_BUTTON_TEXT, ADD_PET_BUTTON_TEXT],
        [ACCEPT_INVITE_BUTTON_TEXT, LLM_CHAT_BUTTON_TEXT],
    ]
)

yes_no_keyboard = _keyboard(
    [
        [YES_TEXT, NO_TEXT],
        [BACK_TO_PROFILE_BUTTON_TEXT],
    ]
)

registration_navigation_keyboard = _keyboard([[BACK_TO_PROFILE_BUTTON_TEXT]])


def build_animal_types_keyboard(animal_types: list[AnimalType]) -> ReplyKeyboardMarkup:
    rows = [[animal_type.animal_name] for animal_type in animal_types]
    rows.append([BACK_TO_PROFILE_BUTTON_TEXT])
    return _keyboard(rows)


def build_animal_breeds_keyboard(breeds: list[AnimalBreed]) -> ReplyKeyboardMarkup:
    rows = [[NO_BREED_BUTTON_TEXT]]
    rows.extend(
        [breed.animal_breed]
        for breed in breeds
        if breed.animal_breed.strip().lower() != NO_BREED_BUTTON_TEXT
    )
    rows.append([BACK_TO_PROFILE_BUTTON_TEXT])
    return _keyboard(rows)


def build_profile_keyboard(pet_names: list[str]) -> ReplyKeyboardMarkup:
    rows = [
        [ADD_PET_BUTTON_TEXT],
        [ACCEPT_INVITE_BUTTON_TEXT, LLM_CHAT_BUTTON_TEXT],
    ]
    rows.extend([[pet_name] for pet_name in pet_names])
    return _keyboard(rows)


llm_chat_keyboard = _keyboard(
    [
        [NEW_LLM_CHAT_BUTTON_TEXT],
        [BACK_TO_PROFILE_BUTTON_TEXT],
    ]
)


def build_pet_details_keyboard(
    *,
    can_share: bool = False,
    can_revoke: bool = False,
    can_manage_photo: bool = False,
    can_delete_pet: bool = False,
) -> ReplyKeyboardMarkup:
    rows = [[PROFILE_BUTTON_TEXT, ADD_PET_BUTTON_TEXT]]
    rows.append([SHOW_PET_DOCUMENTS_BUTTON_TEXT])
    if can_manage_photo:
        rows.append([UPDATE_PET_PHOTO_BUTTON_TEXT, DELETE_PET_PHOTO_BUTTON_TEXT])
    if can_delete_pet:
        rows.append([DELETE_PET_BUTTON_TEXT])
    if can_share:
        rows.append([SHARE_PET_BUTTON_TEXT])
    if can_revoke:
        rows.append([REVOKE_ACCESS_BUTTON_TEXT])
    return _keyboard(rows)


def build_shared_users_keyboard(shared_users: list[tuple[int, str]]) -> ReplyKeyboardMarkup:
    rows = [[f"{shared_user_name} ({shared_user_id})"] for shared_user_id, shared_user_name in shared_users]
    rows.append([PROFILE_BUTTON_TEXT])
    return _keyboard(rows)


def build_document_types_keyboard(document_types: list[tuple[int, str]]) -> ReplyKeyboardMarkup:
    rows = [[name] for _, name in document_types]
    rows.append([BACK_TO_PROFILE_BUTTON_TEXT])
    return _keyboard(rows)


def build_pet_documents_keyboard(document_rows: list[tuple[int, str]]) -> ReplyKeyboardMarkup:
    rows = [[f"{name} #{document_id}"] for document_id, name in document_rows]
    rows.append([PROFILE_BUTTON_TEXT])
    return _keyboard(rows)


def build_pet_documents_actions_keyboard(*, can_manage_documents: bool = False) -> ReplyKeyboardMarkup:
    rows = []
    if can_manage_documents:
        rows.append([ADD_PET_DOCUMENT_BUTTON_TEXT, DELETE_PET_DOCUMENT_BUTTON_TEXT])
    rows.append([PROFILE_BUTTON_TEXT])
    return _keyboard(rows)
