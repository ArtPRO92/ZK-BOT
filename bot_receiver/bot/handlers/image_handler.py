from aiogram import Router, types

router = Router()

@router.message(lambda message: message.photo)
async def handle_image(message: types.Message):
    await message.answer("🖼 Изображение получено.")