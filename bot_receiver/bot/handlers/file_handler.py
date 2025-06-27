from aiogram import Router, F
from aiogram.types import Message
from bot.tasks import save_request_task
from bot.utils.parser import (
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_xlsx
)
import aiohttp
from config import CELERY_BROKER

router = Router()

@router.message(F.document)
async def handle_document(message: Message, bot):
    user_id = message.from_user.id
    document = message.document

    # ✅ Разрешённые форматы
    allowed_extensions = ["docx", "pdf", "txt", "xlsx"]
    file_name = document.file_name or ""
    ext = file_name.split(".")[-1].lower()

      # 🔒 Блокируем .doc
    if ext == "doc":
        await message.answer("❌ Файлы .doc (старый формат Word) не поддерживаются. Пожалуйста, отправьте документ в формате .docx.")
        return

    if ext not in allowed_extensions:
        await message.answer("⚠️ Поддерживаются только .docx, .pdf, .txt и .xlsx файлы.")
        return

    # Получаем файл
    file = await bot.get_file(document.file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status != 200:
                await message.answer("⚠️ Не удалось загрузить файл.")
                return
            content = await response.read()

    print(f"📥 Получен файл: {file_name}, расширение: {ext}, размер: {len(content)} байт")

    # Обработка по типу
    if ext == "docx":
        extracted_text = extract_text_from_docx(content)
    elif ext == "pdf":
        extracted_text = extract_text_from_pdf(content)
    elif ext == "xlsx":
        extracted_text = extract_text_from_xlsx(content)
    else:
        extracted_text = content.decode("utf-8", errors="ignore")

    print("📄 Извлечённый текст (начало):", extracted_text[:300])

    if not extracted_text.strip():
        await message.answer("⚠️ Не удалось извлечь текст из файла.")
        return

    # Проверяем, видит ли бот брокер
    print(f"🔌 CELERY_BROKER в боте: {CELERY_BROKER}")

    # Отправляем в Celery
    save_request_task.delay(user_id, extracted_text, source_type=ext)
    await message.answer(f"✅ Файл {file_name} обработан и отправлен.")
