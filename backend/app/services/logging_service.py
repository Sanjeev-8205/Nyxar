from pathlib import Path
import csv
from datetime import datetime

BASE_DIR=Path(__file__).resolve()
log_path = BASE_DIR.parent.parent.parent/ "logs" / "logs.csv"

def log_predictions(text, prediction, prob, model, latency):
        if not log_path.exists():
            with open(log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Text", "Prediction", "Negative", "Neutral", "Positive", "Model", "Latency", "Timestamp"])

        with open(log_path, "a", newline="", encoding="utf-8") as f:
            writer=csv.writer(f)
            writer.writerow([
                text,
                int(prediction),
                prob[0], #negative
                prob[1], #neutral
                prob[2],  #positive
                model,
                latency,
                datetime.now()
            ])