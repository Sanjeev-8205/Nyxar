# save as convert_onnx.py in your NYXAR folder
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

model_path = "./models/RoBERTa/v1"
output_path = "./models/RoBERTa/v1/onnx"

print("Converting...")
model = ORTModelForSequenceClassification.from_pretrained(
    model_path,
    export=True
)
tokenizer = AutoTokenizer.from_pretrained(model_path)

model.save_pretrained(output_path)
tokenizer.save_pretrained(output_path)
print("✅ Done!")