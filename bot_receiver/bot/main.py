import asyncio
from bot.loader import bot, dp
from bot.handlers import text_handler, file_handler, image_handler
from bot.filters.authorized_users import AuthMiddleware

async def main():
    # 🔐 Авторизация
    dp.message.middleware(AuthMiddleware())

    # 🤖 Подключаем обработчики
    dp.include_routers(
        text_handler.router,
        file_handler.router,
        image_handler.router
    )

    print("🤖 Бот запущен. Ожидает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
