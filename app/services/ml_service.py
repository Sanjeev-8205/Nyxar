from app.schemas.request_schema import InputData
from app.core.model_loader import get_model
from app.core.model_registry import models
from app.core.preprocessing import textProcess_lr, textProcess_bilstm, textPreprocess_RoBERTa, preprocess_batch_lr, preprocess_batch_bilstm, preprocess_batch_RoBERTa
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import torch
import onnxruntime as ort
from scipy.special import softmax
import time

torch.set_num_threads(1)

def predict(text, model_name):

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not available in deployment!")
    pipeline = get_model(model_name)
    model_type = models[model_name]["type"]

    trace = []

    try:
        if model_type == "sklearn":
            pipeline_start = time.perf_counter()

            #Preprocessing
            start = time.perf_counter()
            text = textProcess_lr(text)
            trace.append(
                {
                    "step": "Text Preprocessing",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            #Vectorization
            start = time.perf_counter()
            transformed = pipeline["vectorizer"].transform(text)
            trace.append(
                {
                    "step": "TF-IDF Vectorization",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            #Prediciton
            start = time.perf_counter()
            prediction = pipeline["model"].predict(transformed)[0]
            prob = pipeline["model"].predict_proba(transformed)[0]
            trace.append(
                {
                    "step": "Logistic Prediction",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            total_time = round((time.perf_counter() - pipeline_start)*1000, 1)

        elif model_type == "keras":
            pipeline_start = time.perf_counter()

            #Preprocessing
            start = time.perf_counter()
            text = textProcess_bilstm(text)
            trace.append(
                {
                    "step": "Text Prerocessing",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )
            
            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            #Tokenization
            start = time.perf_counter()
            seq = tokenizer.texts_to_sequences([text])
            trace.append(
                {
                    "step": "Tokenization",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            #Sequence Padding
            start = time.perf_counter()
            pad = pad_sequences(seq, maxlen=maxlen, padding="post")
            trace.append(
                {
                    "step": "Sequence Padding",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            #Prediction
            start = time.perf_counter()
            prob = model.predict(pad, verbose=0)[0]
            prediction = int(np.argmax(prob))
            trace.append(
                {
                    "step": "Bi-LSTM Inference",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            total_time = round((time.perf_counter() - pipeline_start)*1000, 1)

        elif model_type == "transformer":
            pipeline_start = time.perf_counter()

            start = time.perf_counter()
            text = textPreprocess_RoBERTa(text)
            trace.append(
                {
                    "step": "Text Prerocessing",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            tokenizer = pipeline["tokenizer"]
            session = pipeline["session"]   # ← onnx session instead of model
            maxlen = pipeline["maxlen"]

            start = time.perf_counter()
            inputs = tokenizer(
                text,
                max_length=maxlen,
                return_tensors="np",        # ← numpy instead of pt
                truncation=True,
                padding=True
            )
            trace.append(
                {
                    "step": "Tokenization",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            start = time.perf_counter()
            outputs = session.run(
                ["logits"],
                {
                    "input_ids": inputs["input_ids"],
                    "attention_mask": inputs["attention_mask"]
                }
            )

            prob = softmax(outputs[0][0])   # ← scipy softmax on numpy
            prediction = int(np.argmax(prob))

            trace.append(
                {
                    "step": "Onnx Inference",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )

            total_time = round((time.perf_counter() - pipeline_start)*1000, 1)

        return int(prediction), prob.tolist(), trace, total_time

    except Exception as e:
        raise RuntimeError(str(e))

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