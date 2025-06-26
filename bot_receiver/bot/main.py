import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from bot.handlers import text_handler, file_handler, image_handler
from bot.filters.authorized_users import AuthMiddleware
from config import BOT_TOKEN

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Авторизация
    dp.message.middleware(AuthMiddleware())

    # Подключение обработчиков
    dp.include_routers(
        text_handler.router,
        file_handler.router,
        image_handler.router
    )

    print("🤖 Бот запущен. Ожидает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())