from pathlib import Path
import joblib
import os
from huggingface_hub import snapshot_download
from functools import lru_cache

os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

HF_MODELS= {
    "logistic": "Sanjeev2501/nyxar-logistic-sentiment",
    "bilstm": "Sanjeev2501/nyxar-bilstm-sentiment",
    "roberta": "Sanjeev2501/nyxar-roberta-sentiment"
}

@lru_cache(maxsize=None)
def get_repo_path(model_key):
    local_path=snapshot_download(
        repo_id=HF_MODELS[model_key],
        local_dir_use_symlinks=False
    )

    return local_path

def get_logistic_path():
    return Path(get_repo_path("logistic"))

def get_bilstm_path():
    return Path(get_repo_path("bilstm"))

def get_roberta_path():
    return Path(get_repo_path("roberta"))
 
def load_RoBERTa_model():
    import onnxruntime as ort
    from transformers import AutoTokenizer

    path = get_roberta_path()

    session = ort.InferenceSession(str(path/"model_quantized.onnx"))  # ← onnx session
    tokenizer = AutoTokenizer.from_pretrained(str(path))

    return {
        "session": session,      # ← session not model
        "tokenizer": tokenizer,
        "maxlen": 100
    }

def load_logistic_model():
    path = get_logistic_path()

    return {
        "model": joblib.load(path/"logistic_model_v1.pkl"),
        "vectorizer": joblib.load(path/"tfidf_vectorizer_v1.pkl")
    }

def load_bilstm_model():
    import tensorflow as tf

    path = get_bilstm_path()

    return {
        "model": tf.keras.models.load_model(path/"bilstm_model_v1.keras", compile=False),
        "tokenizer": joblib.load(path/"bilstm_tokenizer_v1.pkl"),
        "maxlen": joblib.load(path/"max_len_v1.pkl")
}

models={
    "Logistic Regression":{
        "type":'sklearn',
        "loader": load_logistic_model
    },
    "Bi-LSTM":{
       "type": 'keras',
        "loader": load_bilstm_model
    },
    "RoBERTa Transformer":{
        "type": "transformer",
        "loader":load_RoBERTa_model
    }
}

