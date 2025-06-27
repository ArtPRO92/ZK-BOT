import os
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_IDS = list(map(int, os.getenv("ALLOWED_IDS", "").split(","))) if os.getenv("ALLOWED_IDS") else []

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Celery
CELERY_BROKER = os.getenv("CELERY_BROKER", "redis://localhost:6379/0")
