import json
from pathlib import Path
from razdel import tokenize

# Пути к файлам
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "rubert_dataset.jsonl"
OUTPUT_FILE = BASE_DIR / "bio_dataset.jsonl"

def normalize_label(label: str) -> str:
    """
    Приводит ключ фильтра к допустимому виду для BIO-тегов.
    """
    return label.upper().replace(" ", "_").replace("-", "_")

def tag_tokens(text: str, entities: list):
    """
    Токенизирует текст и присваивает BIO-теги.
    """
    tokens = [_.text for _ in tokenize(text)]
    labels = ["O"] * len(tokens)

    for ent_text, tag in entities:
        ent_tokens = [_.text for _ in tokenize(ent_text)]
        ent_len = len(ent_tokens)

        for i in range(len(tokens) - ent_len + 1):
            if tokens[i:i + ent_len] == ent_tokens:
                labels[i] = f"B-{tag}"
                for j in range(1, ent_len):
                    labels[i + j] = f"I-{tag}"
                break

    return tokens, labels

def prepare_bio():
    count = 0
    with open(INPUT_FILE, "r", encoding="utf-8") as f_in, open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for line in f_in:
            item = json.loads(line)
            raw_text = item.get("raw_text", "")
            parsed = item.get("parsed", {})

            if not raw_text or not parsed:
                continue

            entities = []

            # Добавим category
            if "category" in parsed and parsed["category"]:
                entities.append((parsed["category"], "CATEGORY"))

            # Добавим filters
            filters = parsed.get("filters", {})
            for key, value in filters.items():
                if value:
                    label = normalize_label(key)
                    entities.append((value, label))

            tokens, labels = tag_tokens(raw_text, entities)

            if len(tokens) != len(labels):
                continue

            json.dump({"tokens": tokens, "labels": labels}, f_out, ensure_ascii=False)
            f_out.write("\n")
            count += 1

    print(f"✅ BIO-разметка завершена: {count} примеров сохранено в {OUTPUT_FILE}")

if __name__ == "__main__":
    prepare_bio()
