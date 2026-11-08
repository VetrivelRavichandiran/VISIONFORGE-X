# VISIONFORGE X - Testing Guide

## Running Tests

```bash
cd desktop_app
pytest tests/ -v
```

## Test Categories

### Unit Tests
- `test_protocol.py` - Message serialization, frame protocol
- `test_vision.py` - Vision algorithm correctness
- `test_device.py` - Device abstraction, simulation
- `test_database.py` - Persistence, queries
- `test_pipeline.py` - Pipeline validation, execution
- `test_adaptive.py` - Controller logic
- `test_benchmark.py` - Performance tracking

### Integration Tests
- Simulation device connection flow
- Frame processing pipeline
- Telemetry persistence
- Event emission and storage

### GUI Tests (pytest-qt)
- Application launch
- Page navigation
- Control interactions

## Test Requirements
- pytest
- pytest-qt (for GUI tests)
- numpy, opencv-python

## Hardware Tests
Tests requiring physical ZYBO board are marked with:
```python
@pytest.mark.hardware
def test_hardware_connection():
    ...
```

Run hardware tests separately:
```bash
pytest tests/ -v -m hardware
```

## Coverage
Run with coverage:
```bash
pytest tests/ --cov=backend --cov=protocol --cov=adapters
```
