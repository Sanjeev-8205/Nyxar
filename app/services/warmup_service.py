from app.core.model_loader import get_model
from app.core.model_registry import models
from tensorflow.keras.preprocessing.sequence import pad_sequences
import torch

def preload_models():
    for name in models:
        try:
            get_model(name)
            print(f"{name} loaded")
        except Exception as e:
            print(f"Error loading {name}: {e}")

def warmup():
    dummy = "This is a test"

    for name in models:
        try:
            m = get_model(name)
            t = models[name]["type"]

            if t == "sklearn":
                m["vectorizer"].transform([dummy])

            elif t == "keras":
                seq = m["tokenizer"].texts_to_sequences([dummy])
                pad = pad_sequences(seq, maxlen=m["maxlen"])
                m["model"].predict(pad, verbose=0)

            elif t == "transformer":
                inputs = m["tokenizer"](dummy, return_tensors="pt", max_length=m["maxlen"], truncation=True, padding=True)
                with torch.no_grad():
                    m["model"](**inputs)

            print(f"{name} warmed up")

        except Exception as e:
            print(e)