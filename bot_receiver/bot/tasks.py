from celery_app.worker import celery_app

@celery_app.task
def process_text_task(user_id: int, text: str):
    print(f"[CELERY] Обработка текста от {user_id}: {text}")