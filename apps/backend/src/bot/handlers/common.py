from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.keyboards import main_menu_keyboard
from src.bot.queries import ensure_telegram_user, get_animal_breeds, get_animal_types


router = Router()


@router.message(Command("start"))
async def start_handler(message) -> None:
    _, created = await ensure_telegram_user(message)
    text = "Регистрация через Telegram выполнена." if created else "Вы уже зарегистрированы через Telegram."
    await message.answer(text, reply_markup=main_menu_keyboard)


@router.message(Command("login"))
async def login_handler(message) -> None:
    _, created = await ensure_telegram_user(message)
    text = (
        "Пользователь не существовал, я зарегистрировал вас через Telegram.\n"
        if created
        else "Авторизация через Telegram подтверждена.\n"
    )
    await message.answer(text, reply_markup=main_menu_keyboard)


@router.message(Command("types"))
async def types_handler(message) -> None:
    animal_types = await get_animal_types()
    await message.answer(
        "\n".join(
            ["Доступные типы животных:"]
            + [f"{animal_type.id}: {animal_type.animal_name}" for animal_type in animal_types]
        )
    )


@router.message(Command("breeds"))
async def breeds_handler(message) -> None:
    breeds = await get_animal_breeds()
    await message.answer(
        "\n".join(
            ["Доступные породы:"]
            + [f"{breed.id}: {breed.animal_breed}" for breed in breeds]
        )
    )


@router.message(Command("cancel"))
async def cancel_handler(message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Активной регистрации питомца нет.")
        return

    await state.clear()
    await message.answer("Регистрация питомца отменена.")
