# VISIONFORGE X - Database Schema

## Tables

### devices
Stores registered hardware devices.
- id (PK), name, board_type, firmware_version, bitstream_version, ip_address, created_at, last_seen

### connection_sessions
Tracks device connection history.
- id (PK), device_id (FK), mode, started_at, ended_at, duration_seconds

### telemetry_samples
Real-time performance measurements.
- id (PK), timestamp, device_name, processing_fps, latency_ms, dropped_frames, cpu_usage, memory_usage, motion_intensity, anomaly_score, ai_inference_ms, pipeline_active, dma_status, is_simulated
- Index: timestamp

### benchmark_sessions
Benchmark run metadata.
- id (PK), name, config_json, started_at, ended_at, mode, is_simulated

### benchmark_metrics
Individual benchmark measurements.
- id (PK), session_id (FK), timestamp, metric_name, metric_value, stage
- Index: session_id

### pipelines
Saved processing pipelines.
- id (PK), name, description, config_json, is_active, created_at, updated_at

### pipeline_stages
Pipeline stage definitions.
- id (PK), pipeline_id (FK), stage_index, stage_type, config_json, enabled, execution_source

### model_registry
AI model metadata.
- id (PK), name, model_type, version, path, input_shape, classes_json, framework, quantized, created_at, metadata_json

### inference_records
AI inference history.
- id (PK), model_id (FK), timestamp, inference_ms, confidence, result_json, device
- Index: timestamp

### datasets
Dataset metadata.
- id (PK), name, path, image_count, class_count, split_json, created_at, validated

### dataset_classes
Class distribution per dataset.
- id (PK), dataset_id (FK), class_name, image_count

### events
System events.
- id (PK), timestamp, category, severity, description, snapshot_path, related_model, related_pipeline, data_json, acknowledged
- Index: timestamp, category

### system_settings
Key-value application settings.
- key (PK), value, updated_at

### experiment_records
Research experiment data.
- id (PK), name, config_json, results_json, created_at

### report_history
Generated report metadata.
- id (PK), report_type, title, file_path, created_at, data_summary

## Schema Version
Current version: 1
Migration: Automatic on first run
