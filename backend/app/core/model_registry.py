from pathlib import Path
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import joblib
import tensorflow as tf

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent.parent/"models"

def load_bert_model():
    path = MODEL_DIR/"bert_base_uncased"/"v1"

    model = AutoModelForSequenceClassification.from_pretrained(path)
    tokenizer = AutoTokenizer.from_pretrained(path)

    model.eval()

    return {
        "model": model,
        "tokenizer": tokenizer,
        "maxlen": 100 
    }

models={
    "Logistic Regression":{
        "type":'sklearn',
        "loader": lambda :{
            "model": joblib.load(MODEL_DIR/"logistic_regression"/"v1"/"logistic_model_3_class.pkl"),
            "vectorizer": joblib.load(MODEL_DIR/"logistic_regression"/"v1"/"tfidf_vectorizer_3_class.pkl")
        }
    },
    "Bi-LSTM":{
        "type": 'keras',
        "loader":lambda :{
            "model": tf.keras.models.load_model(MODEL_DIR/"bilstm"/"v1"/"bilstm_model_3_class.keras", compile=False),
            "tokenizer": joblib.load(MODEL_DIR/"bilstm"/"v1"/"bilstm_tokenizer.pkl"),
            "maxlen": joblib.load(MODEL_DIR/"bilstm"/"v1"/"max_len.pkl")
        }
    },
    "BERT Transformer":{
        "type": "transformer",
        "loader":load_bert_model
    }
}