from celery import Celery
from config import CELERY_BROKER
from db.insert_tz import save_request as insert_request

# ✅ Создаём Celery-приложение вручную и указываем брокер
celery = Celery("bot_tasks", broker=CELERY_BROKER)

@celery.task
def save_request_task(user_id: int, text: str, model: str = "gpt-4", source_type: str = "text"):
    """
    Celery-задача для сохранения ТЗ в Supabase.
    """
    return insert_request(user_id, text, model, source_type)
