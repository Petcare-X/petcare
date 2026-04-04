from io import BytesIO

from aiogram import Bot


async def download_telegram_file_bytes(bot: Bot, file_id: str) -> bytes:
    tg_file = await bot.get_file(file_id)
    if not tg_file.file_path:
        raise ValueError("Не удалось получить файл из Telegram. Попробуйте снова.")

    destination = BytesIO()
    await bot.download_file(tg_file.file_path, destination=destination)
    payload = destination.getvalue()
    if not payload:
        raise ValueError("Не удалось скачать файл из Telegram. Попробуйте снова.")

    return payload
