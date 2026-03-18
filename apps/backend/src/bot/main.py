import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError

from src.bot.constants import BOT_RECONNECT_DELAY_SECONDS
from src.bot.handlers import router
from src.core.config import settings


dp = Dispatcher()
dp.include_router(router)
logger = logging.getLogger(__name__)


async def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    while True:
        try:
            await dp.start_polling(bot)
        except TelegramNetworkError as exc:
            logger.warning(
                "Telegram network error while polling: %s. Reconnecting in %s seconds.",
                exc,
                BOT_RECONNECT_DELAY_SECONDS,
            )
            await asyncio.sleep(BOT_RECONNECT_DELAY_SECONDS)
        except Exception:
            await bot.session.close()
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
