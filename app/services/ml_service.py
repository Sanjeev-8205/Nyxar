from app.schemas.request_schema import InputData
from app.core.model_loader import get_model
from app.core.model_registry import models
from app.core.preprocessing import textProcess_lr, textProcess_bilstm, textPreprocess_RoBERTa, preprocess_batch_lr, preprocess_batch_bilstm, preprocess_batch_RoBERTa
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import torch

torch.set_num_threads(1)

def predict(text, model_name):

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not available in deployment!")
    pipeline=get_model(model_name)
    model_type=models[model_name]["type"]

    try:
        if model_type=="sklearn":
            text=textProcess_lr(text)
            transformed = pipeline["vectorizer"].transform(text)
            prediction = pipeline["model"].predict(transformed)[0]
            prob = pipeline["model"].predict_proba(transformed)[0]

        elif model_type=="keras":
            text=textProcess_bilstm(text)
            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            seq=tokenizer.texts_to_sequences([text])
            pad=pad_sequences(seq, maxlen=maxlen, padding="post")

            prob=model.predict(pad, verbose=0)[0]
            prediction=int(np.argmax(prob))

        elif model_type=="transformer":
            text=textPreprocess_RoBERTa(text)
            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            inputs=tokenizer(
                text,
                max_length=maxlen,
                return_tensors="pt",
                truncation=True,
                padding=True
            )

            with torch.no_grad():
                outputs=model(**inputs)
            probs=torch.nn.functional.softmax(outputs.logits, dim=1)

            prob=probs.detach().cpu().numpy()[0]
            prediction=int(np.argmax(prob))

        return int(prediction), prob.tolist()

    except Exception as e:
        return {"error": str(e)}

def predict_batch(texts, model_name):

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not available in deployment!")
    pipeline=get_model(model_name)
    model_type=models[model_name]["type"]

    try:
        if model_type=="sklearn":
            texts=preprocess_batch_lr(texts)
            transformed = pipeline["vectorizer"].transform(texts)
            predictions = pipeline["model"].predict(transformed)
            probs = pipeline["model"].predict_proba(transformed)

        elif model_type=="keras":
            texts=preprocess_batch_bilstm(texts)
            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            seq=tokenizer.texts_to_sequences(texts)
            pad=pad_sequences(seq, maxlen=maxlen, padding="post")

            probs=model.predict(pad, verbose=0)
            predictions=np.argmax(probs, axis=1)

        elif model_type=="transformer":
            texts = preprocess_batch_RoBERTa(texts)
            tokenizer = pipeline["tokenizer"]
            model = pipeline["model"]
            maxlen = pipeline["maxlen"]

            BATCH_SIZE = 64
            all_probs = []

            for i in range(0, len(texts), BATCH_SIZE):
                batch = texts[i : i + BATCH_SIZE]

                inputs = tokenizer(
                    batch,
                    max_length=maxlen,
                    return_tensors="pt",
                    truncation=True,
                    padding=True
                )

                with torch.no_grad():
                    outputs = model(**inputs)

                batch_probs = torch.nn.functional.softmax(
                    outputs.logits, dim=1
                )
                all_probs.append(batch_probs.detach().cpu().numpy())

            probs = np.concatenate(all_probs, axis=0)
            predictions = np.argmax(probs, axis=1)

        return (predictions.tolist(), probs.tolist())

    except Exception as e:
        raise e