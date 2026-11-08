# VISIONFORGE X - AI Model Integration Guide

## Supported Formats
- ONNX (.onnx) - Primary format
- PyTorch (.pt, .pth) - Workstation training
- TensorFlow Lite (.tflite) - Embedded deployment

## Model Types
- Classification - Image categorization
- Detection - Object detection with bounding boxes
- Anomaly - Anomaly scoring and heatmaps

## Model Registry
Models are registered with metadata:
- Name, type, version
- Input shape
- Supported classes
- Framework
- Quantization status

## Import Process
1. Place model file in `ai_models/` directory
2. Import via AI Intelligence Lab page
3. Validation checks format and structure
4. Model registered in database

## Conversion Workflow
```
PyTorch → ONNX → (Optional Quantization) → Embedded Runtime
```

Scripts in `scripts/`:
- `export_onnx.py` - PyTorch to ONNX export
- `quantize.py` - Post-training quantization
- `validate_model.py` - Model validation

## Embedded Deployment
- ONNX Runtime for ARM
- Quantized models for efficiency
- Compatible with Zynq-7010 ARM core

## Compatibility
- Input resolution must match model expectation
- Class labels must be provided
- Framework version compatibility checked
