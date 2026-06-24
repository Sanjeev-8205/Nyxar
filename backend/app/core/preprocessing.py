import re

#Single Inference
def textProcess_lr(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]+', "", text)
    text = re.sub(r"\s+", " ", text).split()

    return [" ".join(text)]

def textProcess_bilstm(text):
    text=text.lower()
    text=re.sub(r'[^a-z0-9\s]', "", text)
    return text

def textPreprocess_RoBERTa(text):
    return text.strip()

#Batch Inference
def preprocess_batch_lr(df_texts):
    df_texts = (
        df_texts
        .str.lower()
        .str.replace(r'[^a-z0-9\s]+', "", regex=True)
        .str.replace(r'\s+', " ", regex=True)
        .str.strip()
    )

    return df_texts.to_list()

def preprocess_batch_bilstm(df_texts):
    df_texts=(
        df_texts.str.lower()
        .str.replace(r'[^a-z0-9\s]+', "", regex=True)
    )
    return df_texts.to_list()

def preprocess_batch_RoBERTa(df_texts):
    df_texts = df_texts.str.strip()
    return df_texts.to_list()