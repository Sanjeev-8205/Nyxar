from app.schemas.request_schema import InputData
from app.core.model_loader import get_model
from app.core.model_registry import models
from app.core.preprocessing import textProcess_lr, textProcess_bilstm, textPreprocess_RoBERTa, preprocess_batch_lr, preprocess_batch_bilstm, preprocess_batch_RoBERTa
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import torch
import onnxruntime as ort
from scipy.special import softmax

torch.set_num_threads(1)

def predict(text, model_name):

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not available in deployment!")
    pipeline = get_model(model_name)
    model_type = models[model_name]["type"]

    try:
        if model_type == "sklearn":
            text = textProcess_lr(text)
            transformed = pipeline["vectorizer"].transform(text)
            prediction = pipeline["model"].predict(transformed)[0]
            prob = pipeline["model"].predict_proba(transformed)[0]

        elif model_type == "keras":
            text = textProcess_bilstm(text)
            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            seq = tokenizer.texts_to_sequences([text])
            pad = pad_sequences(seq, maxlen=maxlen, padding="post")

            prob = model.predict(pad, verbose=0)[0]
            prediction = int(np.argmax(prob))

        elif model_type == "transformer":
            text = textPreprocess_RoBERTa(text)
            tokenizer = pipeline["tokenizer"]
            session = pipeline["session"]   # ← onnx session instead of model
            maxlen = pipeline["maxlen"]

            inputs = tokenizer(
                text,
                max_length=maxlen,
                return_tensors="np",        # ← numpy instead of pt
                truncation=True,
                padding=True
            )

            outputs = session.run(
                ["logits"],
                {
                    "input_ids": inputs["input_ids"],
                    "attention_mask": inputs["attention_mask"]
                }
            )

            prob = softmax(outputs[0][0])   # ← scipy softmax on numpy
            prediction = int(np.argmax(prob))

        return int(prediction), prob.tolist()

    except Exception as e:
        return {"error": str(e)}


def predict_batch(texts, model_name):

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not available in deployment!")
    pipeline = get_model(model_name)
    model_type = models[model_name]["type"]

    try:
        if model_type == "sklearn":
            texts = preprocess_batch_lr(texts)
            transformed = pipeline["vectorizer"].transform(texts)
            predictions = pipeline["model"].predict(transformed)
            probs = pipeline["model"].predict_proba(transformed)

        elif model_type == "keras":
            texts = preprocess_batch_bilstm(texts)
            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            seq = tokenizer.texts_to_sequences(texts)
            pad = pad_sequences(seq, maxlen=maxlen, padding="post")

            probs = model.predict(pad, verbose=0)
            predictions = np.argmax(probs, axis=1)

        elif model_type == "transformer":
            texts = preprocess_batch_RoBERTa(texts)
            tokenizer = pipeline["tokenizer"]
            session = pipeline["session"]   # ← onnx session instead of model
            maxlen = pipeline["maxlen"]

            BATCH_SIZE = 64
            all_probs = []

            for i in range(0, len(texts), BATCH_SIZE):
                batch = texts[i: i + BATCH_SIZE]

                inputs = tokenizer(
                    batch,
                    max_length=maxlen,
                    return_tensors="np",    # ← numpy instead of pt
                    truncation=True,
                    padding=True
                )

                outputs = session.run(
                    ["logits"],
                    {
                        "input_ids": inputs["input_ids"],
                        "attention_mask": inputs["attention_mask"]
                    }
                )

                batch_probs = softmax(outputs[0], axis=1)
                all_probs.append(batch_probs)

            probs = np.concatenate(all_probs, axis=0)
            predictions = np.argmax(probs, axis=1)

        return (predictions.tolist(), probs.tolist())

    except Exception as e:
        raise e