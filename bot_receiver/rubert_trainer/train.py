import json
import numpy as np
from pathlib import Path
from sklearn.metrics import classification_report
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification,
    EvalPrediction
)
import transformers

print(f"🧪 transformers version: {transformers.__version__}")
print(f"📦 TrainingArguments location: {transformers.TrainingArguments.__module__}")

# === Пути ===
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "bio_dataset.jsonl"
MODEL_DIR = BASE_DIR / "model"
BEST_MODEL_DIR = BASE_DIR / "best_model"
CHECKPOINT_DIR = BASE_DIR / "checkpoints"
LOG_DIR = BASE_DIR / "logs"
DATASET_DIR = BASE_DIR / "dataset"
MODEL_NAME = "DeepPavlov/rubert-base-cased"

# === Загрузка и подготовка данных ===
def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    labels_set = set()
    for sample in data:
        labels_set.update(sample["labels"])
    label_list = sorted(labels_set)
    label2id = {label: i for i, label in enumerate(label_list)}
    id2label = {i: label for label, i in label2id.items()}

    dataset = Dataset.from_list([
        {
            "tokens": s["tokens"],
            "labels": [label2id[tag] for tag in s["labels"]]
        }
        for s in data
    ])

    split = dataset.train_test_split(test_size=0.1, seed=42)
    return split["train"], split["test"], label_list, label2id, id2label

# === Токенизация с выравниванием меток ===
def tokenize_and_align_labels(examples, tokenizer):
    tokenized_inputs = tokenizer(
        examples["tokens"],
        is_split_into_words=True,
        truncation=True,
        padding="max_length",
        max_length=128
    )

    all_labels = examples["labels"]
    new_labels = []

    for i, example_labels in enumerate(all_labels):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = []
        previous_word_idx = None

        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(example_labels[word_idx])
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx

        new_labels.append(label_ids)

    tokenized_inputs["labels"] = new_labels
    return tokenized_inputs

# === Метрики ===
def compute_metrics(p: EvalPrediction, id2label=None):
    preds = np.argmax(p.predictions, axis=2)
    labels = p.label_ids

    true_preds, true_labels = [], []

    for pred, label in zip(preds, labels):
        for p_token, l_token in zip(pred, label):
            if l_token != -100:
                true_preds.append(id2label[p_token])
                true_labels.append(id2label[l_token])

    report = classification_report(true_labels, true_preds, output_dict=True, zero_division=0)
    return {
        "precision": report["weighted avg"]["precision"],
        "recall": report["weighted avg"]["recall"],
        "f1": report["weighted avg"]["f1-score"]
    }

# === Основной запуск ===
def main():
    print("📥 Загружаем данные...")
    train_data, test_data, label_list, label2id, id2label = load_data()
    print(f"✅ Загружено: {len(train_data)} train / {len(test_data)} test")
    print(f"🟢 Метки: {label_list}")

    print("🔠 Загружаем токенизатор...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("✂️ Токенизируем train/test...")
    train_data = train_data.map(lambda x: tokenize_and_align_labels(x, tokenizer), batched=True)
    test_data = test_data.map(lambda x: tokenize_and_align_labels(x, tokenizer), batched=True)

    print("🧠 Загружаем модель...")
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(label_list),
        label2id=label2id,
        id2label=id2label
    )

    print("⚙️ Подготавливаем параметры обучения...")
    args = TrainingArguments(
        output_dir=str(CHECKPOINT_DIR),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        logging_dir=str(LOG_DIR),
        learning_rate=5e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=4,
        weight_decay=0.01,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="f1"
    )

    print("🚀 Запускаем обучение...")
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_data,
        eval_dataset=test_data,
        tokenizer=tokenizer,
        data_collator=DataCollatorForTokenClassification(tokenizer),
        compute_metrics=lambda p: compute_metrics(p, id2label=id2label)
    )

    trainer.train()

    print("💾 Сохраняем датасеты...")
    dataset_dict = DatasetDict({"train": train_data, "test": test_data})
    dataset_dict.save_to_disk(str(DATASET_DIR))
    print(f"✅ Датасеты сохранены в {DATASET_DIR}")

    print("💾 Сохраняем финальную модель...")
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    print(f"✅ Модель сохранена в {MODEL_DIR}")

    print("💾 Сохраняем лучшую модель отдельно...")
    trainer.save_model(str(BEST_MODEL_DIR))
    print(f"✅ Лучшая модель сохранена в {BEST_MODEL_DIR}")

if __name__ == "__main__":
    main()
