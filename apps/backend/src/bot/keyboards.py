from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.models import AnimalBreed, AnimalType

from .constants import (
    ACCEPT_INVITE_BUTTON_TEXT,
    ADD_PET_BUTTON_TEXT,
    BACK_TO_PROFILE_BUTTON_TEXT,
    NO_BREED_BUTTON_TEXT,
    NO_TEXT,
    PROFILE_BUTTON_TEXT,
    REVOKE_ACCESS_BUTTON_TEXT,
    SHARE_PET_BUTTON_TEXT,
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
        [ACCEPT_INVITE_BUTTON_TEXT],
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
        [[breed.animal_breed]]
        for breed in breeds
        if breed.animal_breed.strip().lower() != NO_BREED_BUTTON_TEXT
    )
    rows.append([BACK_TO_PROFILE_BUTTON_TEXT])
    return _keyboard(rows)


def build_profile_keyboard(pet_names: list[str]) -> ReplyKeyboardMarkup:
    rows = [
        [ADD_PET_BUTTON_TEXT],
        [ACCEPT_INVITE_BUTTON_TEXT],
    ]
    rows.extend([[pet_name] for pet_name in pet_names])
    return _keyboard(rows)


def build_pet_details_keyboard(
    *,
    can_share: bool = False,
    can_revoke: bool = False,
) -> ReplyKeyboardMarkup:
    rows = [[PROFILE_BUTTON_TEXT, ADD_PET_BUTTON_TEXT]]
    if can_share:
        rows.append([SHARE_PET_BUTTON_TEXT])
    if can_revoke:
        rows.append([REVOKE_ACCESS_BUTTON_TEXT])
    return _keyboard(rows)


def build_shared_users_keyboard(shared_users: list[tuple[int, str]]) -> ReplyKeyboardMarkup:
    rows = [[f"{shared_user_name} ({shared_user_id})"] for shared_user_id, shared_user_name in shared_users]
    rows.append([PROFILE_BUTTON_TEXT])
    return _keyboard(rows)
