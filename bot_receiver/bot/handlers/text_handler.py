from aiogram import Router, types
from bot.tasks import process_text_task  # 👈 импорт из bot.tasks

router = Router()

@router.message(lambda msg: msg.text)
async def handle_text(message: types.Message):
    await message.answer("✅ Текст получен. Обработка запущена...")
    process_text_task.delay(message.from_user.id, message.text)  # 👈 ключевая строка