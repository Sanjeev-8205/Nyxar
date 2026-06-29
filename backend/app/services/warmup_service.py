from app.core.model_loader import get_model
from app.core.model_registry import models
from app.core import prometheus_metrics as pm
from app.core.settings import get_settings
import numpy as np

settings=get_settings()
if not settings.TESTING:
    from tensorflow.keras.preprocessing.sequence import pad_sequences

def preload_models():
    print("ENTERED PRELOAD")
    for name in models:
        try:
            get_model(name)
            print(f"{name} loaded")
        except Exception as e:
            print(f"Error loading {name}: {e}")
    
    pm.ACTIVE_MODELS.set(len(models))

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
                inputs = m["tokenizer"](
                    dummy,
                    return_tensors="np",        # ← numpy not pt
                    max_length=m["maxlen"],
                    truncation=True,
                    padding=True
                )
                m["session"].run(
                    ["logits"],
                    {
                        "input_ids": inputs["input_ids"].astype(np.int64),
                        "attention_mask": inputs["attention_mask"].astype(np.int64)
                    }
                )

            print(f"{name} warmed up")

        except Exception as e:
            print(e)
