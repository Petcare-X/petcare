from datetime import date
from decimal import Decimal

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.constants import NO_BREED_BUTTON_TEXT
from src.bot.flows import start_add_pet_registration
from src.bot.keyboards import (
    build_animal_breeds_keyboard,
    build_animal_types_keyboard,
    main_menu_keyboard,
    registration_navigation_keyboard,
    yes_no_keyboard,
)
from src.bot.queries import get_animal_breeds, get_animal_types
from src.bot.states import AddPetStates
from src.bot.telegram_media import download_telegram_file_bytes
from src.bot.texts import YES_NO_REQUIRED_TEXT
from src.bot.utils import normalize_text, parse_bool, parse_decimal
from src.core.db import AsyncSessionLocal
from src.pet_measurements import (
    get_pet_measurement_rule,
    validate_pet_measurements_consistency,
    validate_pet_measurement_value,
)
from src.schemas import PetCreate
from src.service import PetsService
from src.service.storage import StorageService


router = Router()
storage_service = StorageService()
pets_service = PetsService()


def _find_by_text(items, attr_name: str, raw_value: str):
    normalized = raw_value.lower()
    return next(
        (
            item
            for item in items
            if getattr(item, attr_name).strip().lower() == normalized
        ),
        None,
    )


async def _ask_next_registration_step(message, state: FSMContext, *, next_state, text: str, reply_markup) -> None:
    await state.set_state(next_state)
    await message.answer(text, reply_markup=reply_markup)


async def _handle_decimal_step(
    message,
    state: FSMContext,
    *,
    field_name: str,
    error_text: str,
    next_state,
    prompt_text: str,
    reply_markup=registration_navigation_keyboard,
) -> None:
    value = parse_decimal(message.text)
    if value is None:
        await message.answer(error_text)
        return

    try:
        validate_pet_measurement_value(field_name, value)
    except ValueError as exc:
        await message.answer(str(exc))
        return

    current_data = await state.get_data()
    next_data = {
        "pet_neck_girth": current_data.get("pet_neck_girth"),
        "pet_breast_girth": current_data.get("pet_breast_girth"),
        field_name: value,
    }
    try:
        validate_pet_measurements_consistency(next_data)
    except ValueError as exc:
        await message.answer(str(exc))
        return

    await state.update_data(**{field_name: str(value)})
    await _ask_next_registration_step(
        message,
        state,
        next_state=next_state,
        text=prompt_text,
        reply_markup=reply_markup,
    )


@router.message(Command("add_pet"))
async def add_pet_handler(message, state: FSMContext) -> None:
    await start_add_pet_registration(message, state)


@router.message(AddPetStates.pet_name)
async def add_pet_name_handler(message, state: FSMContext) -> None:
    pet_name = normalize_text(message.text)
    if len(pet_name) < 2:
        await message.answer("Кличка должна содержать минимум 2 символа. Попробуйте еще раз.")
        return

    await state.update_data(pet_name=pet_name)
    await _ask_next_registration_step(
        message,
        state,
        next_state=AddPetStates.pet_date_of_birth,
        text="Введите дату рождения питомца в формате YYYY-MM-DD.",
        reply_markup=registration_navigation_keyboard,
    )


@router.message(AddPetStates.pet_date_of_birth)
async def add_pet_birth_date_handler(message, state: FSMContext) -> None:
    raw_value = normalize_text(message.text)
    try:
        pet_date_of_birth = date.fromisoformat(raw_value)
    except ValueError:
        await message.answer("Неверный формат даты. Используйте YYYY-MM-DD.")
        return

    animal_types = await get_animal_types()
    await state.update_data(pet_date_of_birth=pet_date_of_birth.isoformat())
    await _ask_next_registration_step(
        message,
        state,
        next_state=AddPetStates.animal_type_id,
        text="Выберите тип животного кнопкой ниже.",
        reply_markup=build_animal_types_keyboard(animal_types),
    )


@router.message(AddPetStates.animal_type_id)
async def add_pet_type_handler(message, state: FSMContext) -> None:
    animal_type_name = normalize_text(message.text)
    animal_types = await get_animal_types()
    animal_type = _find_by_text(animal_types, "animal_name", animal_type_name)
    if animal_type is None:
        await message.answer(
            "Такого типа животного нет. Выберите вариант кнопкой.",
            reply_markup=build_animal_types_keyboard(animal_types),
        )
        return

    breeds = await get_animal_breeds()
    await state.update_data(animal_type_id=animal_type.id)
    await _ask_next_registration_step(
        message,
        state,
        next_state=AddPetStates.animal_breed_id,
        text="Выберите породу кнопкой ниже.",
        reply_markup=build_animal_breeds_keyboard(breeds),
    )


@router.message(AddPetStates.animal_breed_id)
async def add_pet_breed_handler(message, state: FSMContext) -> None:
    animal_breed_name = normalize_text(message.text)
    breeds = await get_animal_breeds()
    animal_breed = _find_by_text(breeds, "animal_breed", animal_breed_name)
    if animal_breed is None:
        await message.answer(
            "Такой породы нет. Выберите вариант кнопкой.",
            reply_markup=build_animal_breeds_keyboard(breeds),
        )
        return

    await state.update_data(animal_breed_id=animal_breed.id)
    if animal_breed.animal_breed.strip().lower() == NO_BREED_BUTTON_TEXT:
        await state.update_data(pedigree=False)
        await _ask_next_registration_step(
            message,
            state,
            next_state=AddPetStates.pet_neck_girth,
            text=_build_measurement_prompt("pet_neck_girth"),
            reply_markup=registration_navigation_keyboard,
        )
        return

    await _ask_next_registration_step(
        message,
        state,
        next_state=AddPetStates.pedigree,
        text="Есть ли родословная? Ответьте: да / нет.",
        reply_markup=yes_no_keyboard,
    )


@router.message(AddPetStates.pedigree)
async def add_pet_pedigree_handler(message, state: FSMContext) -> None:
    pedigree = parse_bool(message.text)
    if pedigree is None:
        await message.answer(YES_NO_REQUIRED_TEXT, reply_markup=yes_no_keyboard)
        return

    await state.update_data(pedigree=pedigree)
    await _ask_next_registration_step(
        message,
        state,
        next_state=AddPetStates.pet_neck_girth,
        text=_build_measurement_prompt("pet_neck_girth"),
        reply_markup=registration_navigation_keyboard,
    )


def _build_measurement_prompt(field_name: str) -> str:
    rule = get_pet_measurement_rule(field_name)
    return f"Введите {rule.label} питомца в {rule.unit}. Допустимый диапазон: {rule.format_range()}."


@router.message(AddPetStates.pet_neck_girth)
async def add_pet_neck_girth_handler(message, state: FSMContext) -> None:
    await _handle_decimal_step(
        message,
        state,
        field_name="pet_neck_girth",
        error_text="Введите число для обхвата шеи в см.",
        next_state=AddPetStates.pet_breast_girth,
        prompt_text=_build_measurement_prompt("pet_breast_girth"),
    )


@router.message(AddPetStates.pet_breast_girth)
async def add_pet_breast_girth_handler(message, state: FSMContext) -> None:
    await _handle_decimal_step(
        message,
        state,
        field_name="pet_breast_girth",
        error_text="Введите число для обхвата груди в см.",
        next_state=AddPetStates.pet_length,
        prompt_text=_build_measurement_prompt("pet_length"),
    )


@router.message(AddPetStates.pet_length)
async def add_pet_length_handler(message, state: FSMContext) -> None:
    await _handle_decimal_step(
        message,
        state,
        field_name="pet_length",
        error_text="Введите число для длины питомца в см.",
        next_state=AddPetStates.pet_weight,
        prompt_text=_build_measurement_prompt("pet_weight"),
    )


@router.message(AddPetStates.pet_weight)
async def add_pet_weight_handler(message, state: FSMContext) -> None:
    await _handle_decimal_step(
        message,
        state,
        field_name="pet_weight",
        error_text="Введите число для веса питомца в кг.",
        next_state=AddPetStates.pet_is_sterylyzed,
        prompt_text="Стерилизован ли питомец? Ответьте: да / нет.",
        reply_markup=yes_no_keyboard,
    )


@router.message(AddPetStates.pet_is_sterylyzed)
async def add_pet_sterylized_handler(message, state: FSMContext) -> None:
    pet_is_sterylyzed = parse_bool(message.text)
    if pet_is_sterylyzed is None:
        await message.answer(YES_NO_REQUIRED_TEXT, reply_markup=yes_no_keyboard)
        return

    await state.update_data(pet_is_sterylyzed=pet_is_sterylyzed)
    await _ask_next_registration_step(
        message,
        state,
        next_state=AddPetStates.pet_photo_object_key,
        text="Отправьте фото питомца (из галереи/камеры) или '-' если фото пока нет.",
        reply_markup=registration_navigation_keyboard,
    )


@router.message(AddPetStates.pet_photo_object_key)
async def add_pet_photo_object_key_handler(message: Message, state: FSMContext) -> None:
    raw_value = normalize_text(message.text)
    no_photo = raw_value == "-"
    has_photo = bool(message.photo)

    if not no_photo and not has_photo:
        await message.answer(
            "Отправьте именно фото сообщением или '-' если хотите сохранить питомца без фото.",
            reply_markup=registration_navigation_keyboard,
        )
        return

    data = await state.get_data()
    photo_bytes: bytes | None = None
    photo_content_type: str | None = None

    if has_photo and message.photo:
        try:
            photo_bytes = await download_telegram_file_bytes(message.bot, message.photo[-1].file_id)
        except ValueError as exc:
            await message.answer(str(exc))
            return
        photo_content_type = "image/jpeg"

    payload = PetCreate(
        pet_name=data["pet_name"],
        pet_date_of_birth=data["pet_date_of_birth"],
        animal_type_id=data["animal_type_id"],
        animal_breed_id=data["animal_breed_id"],
        pedigree=data["pedigree"],
        pet_neck_girth=Decimal(data["pet_neck_girth"]),
        pet_breast_girth=Decimal(data["pet_breast_girth"]),
        pet_length=Decimal(data["pet_length"]),
        pet_weight=Decimal(data["pet_weight"]),
        pet_is_sterylyzed=data["pet_is_sterylyzed"],
        pet_photo_object_key="",
    )

    async with AsyncSessionLocal() as db:
        try:
            pet = await pets_service.create_pet_with_optional_photo(
                db,
                payload,
                data["user_id"],
                photo_bytes=photo_bytes,
                photo_content_type=photo_content_type,
                storage_service=storage_service,
            )
        except Exception:
            await message.answer("Не удалось сохранить питомца с фото. Попробуйте снова позже.")
            return

    await state.clear()
    await message.answer(
        f"{pet.pet_name} добавлен в ваш список питомцев.",
        reply_markup=main_menu_keyboard,
    )
