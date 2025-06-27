import json
from supabase import create_client
from rubert_trainer.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_parsed():
    print("📡 Подключаемся к Supabase...")
    data = supabase.table("tz_requests") \
                   .select("id, parsed") \
                   .not_.is_("parsed", "null") \
                   .execute()

    rows = data.data
    print(f"🔍 Загружено строк: {len(rows)}")

    if not rows:
        print("⚠️ Нет строк с заполненным полем parsed.")
        return

    invalid_rows = []

    for row in rows:
        try:
            # проверяем корректность JSON
            if isinstance(row["parsed"], str):
                json.loads(row["parsed"])
            else:
                json.dumps(row["parsed"])
        except Exception as e:
            invalid_rows.append({"id": row["id"], "error": str(e)})

    if invalid_rows:
        print(f"❌ Найдено {len(invalid_rows)} невалидных строк:")
        for r in invalid_rows:
            print(f" - ID: {r['id']}, ошибка: {r['error']}")
    else:
        print("✅ Все строки parsed валидные.")

if __name__ == "__main__":
    check_parsed()
