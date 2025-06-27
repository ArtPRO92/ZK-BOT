from supabase import create_client
import json
from pathlib import Path
from rubert_trainer.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Абсолютный путь к файлу рядом со скриптом
OUTPUT_PATH = Path(__file__).resolve().parent / "rubert_dataset.jsonl"

def export_to_jsonl(filepath=OUTPUT_PATH):
    print("📡 Подключаемся к Supabase...")
    data = supabase.table("tz_requests") \
                   .select("raw_text, parsed") \
                   .not_.is_("parsed", "null") \
                   .execute()

    rows = data.data
    print(f"🔍 Загружено строк: {len(rows)}")

    saved = 0
    skipped = 0

    with open(filepath, "w", encoding="utf-8") as f:
        for row in rows:
            try:
                json.dumps(row["parsed"])  # проверка сериализуемости
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                saved += 1
            except Exception as e:
                print(f"⚠️ Пропущена строка: {e}")
                skipped += 1

    print(f"✅ Успешно сохранено: {saved} строк → {filepath}")
    if skipped:
        print(f"⚠️ Пропущено {skipped} строк из-за ошибок сериализации")

if __name__ == "__main__":
    export_to_jsonl()
