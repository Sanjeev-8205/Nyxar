from pathlib import Path
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import joblib
import tensorflow as tf

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR/"models"

def load_RoBERTa_model():
    path = MODEL_DIR/"RoBERTa"/"v1"

    model = AutoModelForSequenceClassification.from_pretrained(str(path))
    tokenizer = AutoTokenizer.from_pretrained(str(path))

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
            "model": joblib.load(MODEL_DIR/"logistic_regression"/"v1"/"logistic_model_v1.pkl"),
            "vectorizer": joblib.load(MODEL_DIR/"logistic_regression"/"v1"/"tfidf_vectorizer_v1.pkl")
        }
    },
    "Bi-LSTM":{
       "type": 'keras',
        "loader":lambda :{
            "model": tf.keras.models.load_model(MODEL_DIR/"bilstm"/"v1"/"bilstm_model_v1.keras", compile=False),
            "tokenizer": joblib.load(MODEL_DIR/"bilstm"/"v1"/"bilstm_tokenizer_v1.pkl"),
            "maxlen": joblib.load(MODEL_DIR/"bilstm"/"v1"/"max_len_v1.pkl")
        }
    },
    "BERT Transformer":{
        "type": "transformer",
        "loader":load_bert_model()
    }
}