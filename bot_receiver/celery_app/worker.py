from celery import Celery
from config import CELERY_BROKER

celery_app = Celery("bot_tasks", broker=CELERY_BROKER)

# Автоматический импорт задач из bot.tasks
celery_app.autodiscover_tasks(["bot.tasks"])