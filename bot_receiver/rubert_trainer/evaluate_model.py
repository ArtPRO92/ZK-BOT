import torch
from transformers import BertTokenizerFast, BertForTokenClassification
from datasets import load_from_disk
from seqeval.metrics import classification_report, f1_score
from pathlib import Path
import json
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "best_model"
DATA_DIR = BASE_DIR / "dataset"
REPORT_PATH = BASE_DIR / "logs" / "eval_metrics.json"

print("🔄 Загружаем модель и токенизатор...")
model = BertForTokenClassification.from_pretrained(MODEL_DIR)
tokenizer = BertTokenizerFast.from_pretrained(MODEL_DIR)
model.eval()

# ✅ Получаем id2label из конфигурации модели без int()
id2label = model.config.id2label  # например: {0: 'O', 1: 'B-ATTR'}

print("📥 Загружаем тестовый датасет...")
dataset = load_from_disk(str(DATA_DIR))["test"]

true_labels = []
pred_labels = []

print("🧠 Предсказываем...")
for example in dataset:
    tokens = example["tokens"]
    labels = example["labels"]

    inputs = tokenizer(
        tokens,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    predictions = torch.argmax(outputs.logits, dim=2).squeeze().tolist()
    word_ids = inputs.word_ids()

    true, pred = [], []
    previous_word_idx = None
    for idx, word_idx in enumerate(word_ids):
        if word_idx is None or word_idx == previous_word_idx:
            continue
        if word_idx < len(labels):
            true_id = labels[word_idx]
            pred_id = predictions[idx]

            if isinstance(true_id, int) and isinstance(pred_id, int):
                true.append(id2label.get(true_id, "O"))
                pred.append(id2label.get(pred_id, "O"))
        previous_word_idx = word_idx

    true_labels.append(true)
    pred_labels.append(pred)

print("\n📊 Результаты оценки:")
report = classification_report(true_labels, pred_labels, output_dict=True, zero_division=0)

# 🔧 Приводим все значения к сериализуемым типам
def to_python_types(obj):
    if isinstance(obj, dict):
        return {str(k): to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_python_types(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

clean_report = to_python_types(report)

# Печать в консоль
try:
    print(json.dumps(clean_report, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ Ошибка при печати JSON: {e}")
    print(f"Тип clean_report: {type(clean_report)}")

# Сохранение в файл
try:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_report, f, ensure_ascii=False, indent=2)
    print(f"✅ Отчёт сохранён в {REPORT_PATH}")
except Exception as e:
    print(f"❌ Ошибка при сохранении JSON: {e}")
    print(f"Тип clean_report: {type(clean_report)}")
print("🎯 F1-Score:", round(f1_score(true_labels, pred_labels), 4))
