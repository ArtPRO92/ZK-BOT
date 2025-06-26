import os
from dotenv import load_dotenv

# Путь к .env относительно этого файла
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_IDS = list(map(int, os.getenv("ALLOWED_IDS", "").split(",")))
CELERY_BROKER = os.getenv("CELERY_BROKER")