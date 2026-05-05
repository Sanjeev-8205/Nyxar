import json
from pathlib import Path
import pandas as pd
import numpy as np
from app.core.model_registry import models
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tensorflow.keras.preprocessing.sequence import pad_sequences
import torch
from datetime import datetime
import time
import tqdm

from app.core.preprocessing import preprocess_batch_lr, textProcess_bilstm, textPreprocess_bert

BASE_DIR = Path(__file__).resolve().parent
METRICS_DIR = BASE_DIR / "metrics"
METRICS_DIR.mkdir(exist_ok=True)

def predict_batch(text, model_name):
    pipeline=models[model_name]["loader"]()
    model_type=models[model_name]["type"]
    try:
        if model_type=="sklearn":
            texts=preprocess_batch_lr(text)

            transformed = pipeline["vectorizer"].transform(texts)
            prediction = pipeline["model"].predict(transformed)

        elif model_type=="keras":
            texts=[textProcess_bilstm(t) for t in text]
            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            seq=tokenizer.texts_to_sequences(texts)
            pad=pad_sequences(seq, maxlen=maxlen, padding="post")

            prob=model.predict(pad, verbose=0)
            prediction=np.argmax(prob, axis=1)

        elif model_type=="transformer":
            texts = [textPreprocess_bert(t) for t in text]

            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            batch_size = 32
            all_preds = []

            for i in tqdm.tqdm(range(0, len(texts), batch_size), desc="Transformer Inference"):
                batch = texts[i:i+batch_size]

                inputs = tokenizer(
                    batch,
                    max_length=maxlen,
                    return_tensors="pt",
                    truncation=True,
                    padding=True
                )

                with torch.no_grad():
                    outputs = model(**inputs)

                probs = torch.nn.functional.softmax(outputs.logits, dim=1)
                preds = torch.argmax(probs, dim=1)

                all_preds.extend(preds.cpu().numpy())

            prediction = np.array(all_preds)

        return prediction

    except Exception as e:
        print("Error: ", e)
        raise e
    
def main():
    start_total = time.perf_counter()
    CSV_DIR = BASE_DIR / "data" / "test.csv"

    if CSV_DIR.exists():
        reviews = pd.read_csv(CSV_DIR)
    else:
        return "CSV Path not found."
    text = reviews["text"]
    labels = reviews["label"]

    model = list(models.keys())

    for m in model:
        print(f"Running Model : {m}")
        start=time.perf_counter()
        preds = predict_batch(text, m)
        end=time.perf_counter()

        model_time = end-start
        print(f"Time taken by {m} = {model_time:.2f} seconds")

        metrics = {
            "model":m,
            "version": "v1",
            "timestamp": datetime.now().isoformat(),
            "accuracy":accuracy_score(labels, preds),
            "precision":precision_score(labels, preds, average="weighted"),
            "recall":recall_score(labels, preds, average="weighted"),
            "f1-score":f1_score(labels, preds, average="weighted")
        }

        if m=="Logistic Regression":
            m="logistic_regression"
        elif m=="Bi-LSTM":
            m="bilstm"
        elif m=="BERT Transformer":
            m="bert_base_uncased"

        with open(METRICS_DIR / f"{m}.json", 'w') as f:
            json.dump(metrics, f, indent=4)

    total_time = time.perf_counter()-start_total
    print(f"Total pipeline time = {total_time:.2f} seconds")
if __name__ == "__main__":
    main()