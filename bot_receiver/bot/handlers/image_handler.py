from aiogram import Router, F
from aiogram.types import Message
from bot.tasks import save_request_task
from bot.utils.parser import extract_text_from_image
import aiohttp

router = Router()

@router.message(F.photo)
async def handle_image(message: Message, bot):
    user_id = message.from_user.id
    photo = message.photo[-1]  # самое большое по размеру изображение
    file = await bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status != 200:
                await message.answer("⚠️ Не удалось загрузить изображение.")
                return
            content = await response.read()

    extracted_text = extract_text_from_image(content)

    if not extracted_text.strip():
        await message.answer("⚠️ Текст не распознан.")
        return

    save_request_task.delay(user_id, extracted_text, source_type="image")
    await message.answer("✅ Текст с изображения успешно извлечён и сохранён.")
