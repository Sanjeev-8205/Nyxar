import re
import spacy
nlp=spacy.load("en_core_web_sm", disable=["parser", "ner"])

def textProcess_lr(text):
    text=nlp(text.lower())

    tokens=[]
    for token in text:
        if token.is_alpha and not token.is_stop:
            tokens.append(token.lemma_)
        continue

    return [" ".join(tokens)]

def preprocess_batch_lr(texts):
    processed = []

    for doc in nlp.pipe(texts, batch_size=1000):
        tokens = [
            token.lemma_
            for token in doc
            if token.is_alpha and not token.is_stop
        ]
        processed.append(" ".join(tokens))

    return processed

def textProcess_bilstm(text):
    text=text.lower()
    text=re.sub(r'[^a-z0-9\s]', "", text)
    return text

def textPreprocess_bert(text):
    return text.strip()