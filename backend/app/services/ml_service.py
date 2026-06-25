from app.schemas.request_schema import InputData
from app.core.model_loader import get_model
from app.core.model_registry import models
from app.core.preprocessing import textProcess_lr, textProcess_bilstm, textPreprocess_RoBERTa, preprocess_batch_lr, preprocess_batch_bilstm, preprocess_batch_RoBERTa
import time
from app.core.settings import get_settings
from app.core.logging_config import setup_logging

logger=setup_logging()
settings=get_settings()
if not settings.TESTING:
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

    trace = []

    try:
        if model_type == "sklearn":
            logger.debug("inference_preprocessing_started")
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
            logger.debug("inference_preprocessing_completed", processing_length=len(text), duration_ms=round((time.perf_counter() - start)*1000, 4))

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
            logger.debug("inference_model_started")
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
            logger.debug("inference_preprocessing_started")
            start = time.perf_counter()
            text = textProcess_bilstm(text)
            trace.append(
                {
                    "step": "Text Prerocessing",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )
            logger.debug("inference_preprocessing_completed", processing_length=len(text), duration_ms=round((time.perf_counter() - start)*1000, 4))
            
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
            logger.debug("inference_model_started")
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

            logger.debug("inference_preprocessing_started")
            start = time.perf_counter()
            text = textPreprocess_RoBERTa(text)
            trace.append(
                {
                    "step": "Text Prerocessing",
                    "duration_ms": round((time.perf_counter() - start)*1000, 1)
                }
            )
            logger.debug("inference_preprocessing_completed", processing_length=len(text), duration_ms=round((time.perf_counter() - start)*1000, 4))

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
            logger.debug("inference_model_started")
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

    trace = []

    try:
        if model_type == "sklearn":
            start = time.perf_counter()
            texts = preprocess_batch_lr(texts)
            trace.append(
                {
                    "step": "Text Preprocessing",
                    "time_taken": time.perf_counter() - start
                }
            )

            start = time.perf_counter()
            transformed = pipeline["vectorizer"].transform(texts)
            trace.append(
                {
                    "step": "Vectorization",
                    "time_taken": time.perf_counter() - start
                }
            )

            start = time.perf_counter()
            predictions = pipeline["model"].predict(transformed)
            probs = pipeline["model"].predict_proba(transformed)
            trace.append(
                {
                    "step": "Logistic Batch Inference",
                    "time_taken": time.perf_counter() - start
                }
            )

        elif model_type == "keras":
            start = time.perf_counter()
            texts = preprocess_batch_bilstm(texts)
            trace.append(
                {
                    "step": "Text Preprocessing",
                    "time_taken": time.perf_counter() - start
                }
            )

            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            start = time.perf_counter()
            seq = tokenizer.texts_to_sequences(texts)
            trace.append(
                {
                    "step": "Tokenization",
                    "time_taken": time.perf_counter() - start
                }
            )

            start = time.perf_counter()
            pad = pad_sequences(seq, maxlen=maxlen, padding="post")
            trace.append(
                {
                    "step": "Sequence Padding",
                    "time_taken": time.perf_counter() - start
                }
            )
            
            start = time.perf_counter()
            probs = model.predict(pad, verbose=0)
            predictions = np.argmax(probs, axis=1)
            trace.append(
                {
                    "step": "Bi-LSTM Batch Inference",
                    "time_taken": time.perf_counter() - start
                }
            )

        elif model_type == "transformer":
            start = time.perf_counter()
            texts = preprocess_batch_RoBERTa(texts)
            trace.append(
                {
                    "step": "Text Preprocessing",
                    "time_taken": time.perf_counter() - start
                }
            )
            
            tokenizer = pipeline["tokenizer"]
            session = pipeline["session"]   # ← onnx session instead of model
            maxlen = pipeline["maxlen"]

            BATCH_SIZE = 64
            all_probs = []

            tokenization_time = 0
            roberta_inference_time = 0
            for i in range(0, len(texts), BATCH_SIZE):
                batch = texts[i: i + BATCH_SIZE]

                st = time.perf_counter()
                inputs = tokenizer(
                    batch,
                    max_length=maxlen,
                    return_tensors="np",    # ← numpy instead of pt
                    truncation=True,
                    padding=True
                )
                tokenization_time += time.perf_counter() - st

                st = time.perf_counter()
                outputs = session.run(
                    ["logits"],
                    {
                        "input_ids": inputs["input_ids"],
                        "attention_mask": inputs["attention_mask"]
                    }
                )
                batch_probs = softmax(outputs[0], axis=1)
                all_probs.append(batch_probs)

                roberta_inference_time += time.perf_counter() - st

            trace.append(
                {
                    "step": "Tokenization",
                    "time_taken": tokenization_time
                }
            )

            trace.append(
                {
                    "step": "RoBERTa Batch Inference",
                    "time_taken": roberta_inference_time
                }
            )
            
            probs = np.concatenate(all_probs, axis=0)
            predictions = np.argmax(probs, axis=1)

        return (predictions.tolist(), probs.tolist(), trace)

    except Exception as e:
        raise e