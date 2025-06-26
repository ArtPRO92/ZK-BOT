from aiogram import Router, types

router = Router()

@router.message(lambda message: message.document is not None)
async def handle_document(message: types.Message):
    await message.answer("📄 Документ получен.")