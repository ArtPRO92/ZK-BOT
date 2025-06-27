from supabase import create_client
from datetime import datetime, timezone
from config import SUPABASE_URL, SUPABASE_KEY  # данные берутся из .env

# Инициализация клиента Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_request(user_id: int, text: str, model: str = "gpt-4", source_type: str = "text"):
    """
    Сохраняет техническое задание в таблицу tz_requests Supabase.

    :param user_id: Telegram ID пользователя
    :param text: Сырой текст технического задания
    :param model: Название модели (по умолчанию gpt-4)
    :param source_type: Тип источника (text, docx, image и т.д.)
    :return: Ответ от Supabase
    """
    data = {
        "user_id": user_id,
        "raw_text": text,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_type": source_type,
        "model_used": model,
        "parse_status": "pending",
        "parsed": {}  # пока пусто — будет заполняться после парсинга
    }

    # Выполняем вставку
    result = supabase.table("tz_requests").insert(data).execute()
    return result
