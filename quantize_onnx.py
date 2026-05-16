from onnxruntime.quantization import quantize_dynamic, QuantType

quantize_dynamic(
    "./models/RoBERTa/v1/onnx/model.onnx",
    "./models/RoBERTa/v1/onnx/model_quantized.onnx",
    weight_type=QuantType.QInt8
)