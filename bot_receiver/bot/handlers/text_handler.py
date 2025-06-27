from aiogram import Router, F
from aiogram.types import Message
from bot.tasks import save_request_task

router = Router()

@router.message(F.content_type == "text")
async def handle_text(message: Message):
    user_id = message.from_user.id
    text = message.text
    save_request_task.delay(user_id, text)
    await message.answer("✅ Ваше техническое задание сохранено.")
