from aiogram.types import Message
from aiogram import BaseMiddleware
from config import ALLOWED_IDS

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user_id = event.from_user.id
        if user_id not in ALLOWED_IDS:
            await event.answer("⛔️ Доступ запрещён")
            return None  # 👈 Явный возврат
        return await handler(event, data)