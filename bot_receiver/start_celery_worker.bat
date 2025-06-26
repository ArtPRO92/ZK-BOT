@echo off
REM Путь к проекту
cd /d C:\ZK-BOT\bot_receiver

REM Активируем виртуальное окружение
call ..\.venv\Scripts\activate.bat

REM Устанавливаем PYTHONPATH для корректных импортов
set PYTHONPATH=C:\ZK-BOT\bot_receiver

REM Запускаем Celery в режиме solo (для Windows)
python -m celery -A celery_app.worker worker --loglevel=info --pool=solo
