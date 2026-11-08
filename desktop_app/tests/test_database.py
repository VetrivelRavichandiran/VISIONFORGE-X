"""VISIONFORGE X - Database Tests."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.storage.database import DatabaseManager


@pytest.fixture
def db():
    """Create a temporary database for testing."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = DatabaseManager(path)
    yield db
    # Close DB first to release file handles (Windows needs this)
    db.close()
    import time
    time.sleep(0.3)
    for p in [path, path + '-wal', path + '-shm', path + '-journal']:
        for _ in range(15):
            try:
                if os.path.exists(p):
                    os.unlink(p)
                break
            except PermissionError:
                time.sleep(0.2)


class TestDatabaseInit:
    """Test database initialization."""

    def test_create_db(self, db):
        assert os.path.exists(db.db_path)

    def test_tables_exist(self, db):
        tables = db.query("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [t['name'] for t in tables]
        assert 'telemetry_samples' in table_names
        assert 'events' in table_names
        assert 'benchmark_sessions' in table_names
        assert 'pipelines' in table_names
        assert 'model_registry' in table_names
        assert 'datasets' in table_names


class TestTelemetryPersistence:
    """Test telemetry data persistence."""

    def test_insert_telemetry(self, db):
        sample = {
            'device_name': 'TEST',
            'processing_fps': 25.5,
            'latency_ms': 12.3,
            'dropped_frames': 0,
            'cpu_usage': 30.0,
            'memory_usage': 45.0,
            'motion_intensity': 0.1,
            'anomaly_score': 0.05,
            'ai_inference_ms': 35.0,
            'pipeline_active': True,
            'dma_status': 'running',
        }
        row_id = db.insert_telemetry(sample)
        assert row_id > 0

    def test_insert_simulated_telemetry(self, db):
        sample = {'device_name': 'SIM', 'processing_fps': 30.0}
        row_id = db.insert_telemetry(sample, is_simulated=True)
        rows = db.query("SELECT * FROM telemetry_samples WHERE id = ?", (row_id,))
        assert len(rows) == 1
        assert rows[0]['is_simulated'] == 1

    def test_get_telemetry_history(self, db):
        for i in range(10):
            db.insert_telemetry({'device_name': 'TEST', 'processing_fps': 20 + i})
        history = db.get_telemetry_history(limit=5)
        assert len(history) == 5

    def test_telemetry_is_simulated_flag(self, db):
        db.insert_telemetry({'device_name': 'SIM'}, is_simulated=True)
        db.insert_telemetry({'device_name': 'HW'}, is_simulated=False)
        sim = db.query("SELECT * FROM telemetry_samples WHERE is_simulated = 1")
        hw = db.query("SELECT * FROM telemetry_samples WHERE is_simulated = 0")
        assert len(sim) == 1
        assert len(hw) == 1


class TestEventPersistence:
    """Test event persistence."""

    def test_insert_event(self, db):
        event = {
            'category': 'device',
            'severity': 'info',
            'description': 'Test event',
            'data': {'key': 'value'}
        }
        row_id = db.insert_event(event)
        assert row_id > 0

    def test_get_events(self, db):
        for i in range(5):
            db.insert_event({'category': 'test', 'severity': 'info', 'description': f'Event {i}'})
        events = db.get_events(limit=10)
        assert len(events) == 5

    def test_filter_events_by_category(self, db):
        db.insert_event({'category': 'device', 'severity': 'info', 'description': 'D1'})
        db.insert_event({'category': 'ai', 'severity': 'info', 'description': 'A1'})
        device_events = db.get_events(category='device')
        assert len(device_events) == 1
        assert device_events[0]['description'] == 'D1'

    def test_filter_events_by_severity(self, db):
        db.insert_event({'category': 'test', 'severity': 'error', 'description': 'E1'})
        db.insert_event({'category': 'test', 'severity': 'info', 'description': 'I1'})
        errors = db.get_events(severity='error')
        assert len(errors) == 1

    def test_acknowledge_event(self, db):
        row_id = db.insert_event({'category': 'test', 'severity': 'info', 'description': 'Ack test'})
        result = db.acknowledge_event(row_id)
        assert result is True
        events = db.get_events(acknowledged=True)
        assert len(events) == 1

    def test_event_data_json(self, db):
        db.insert_event({
            'category': 'test', 'severity': 'info', 'description': 'JSON test',
            'data': {'nested': {'key': 'value'}, 'list': [1, 2, 3]}
        })
        events = db.get_events(limit=1)
        assert events[0]['data_json'] is not None


class TestBenchmarkPersistence:
    """Test benchmark session persistence."""

    def test_create_session(self, db):
        row_id = db.create_benchmark_session(
            'Test Session', {'resolution': '640x480'}, 'simulation', True
        )
        assert row_id > 0

    def test_insert_metric(self, db):
        session_id = db.create_benchmark_session('S1', {}, 'simulation', True)
        db.insert_benchmark_metric(session_id, 'fps', 25.5, 'main')
        metrics = db.get_benchmark_metrics(session_id)
        assert len(metrics) == 1
        assert metrics[0]['metric_name'] == 'fps'
        assert metrics[0]['metric_value'] == 25.5

    def test_get_sessions(self, db):
        db.create_benchmark_session('S1', {}, 'simulation', True)
        db.create_benchmark_session('S2', {}, 'hardware', False)
        sessions = db.get_benchmark_sessions()
        assert len(sessions) == 2


class TestPipelinePersistence:
    """Test pipeline persistence."""

    def test_save_pipeline(self, db):
        stages = [
            {'type': 'grayscale', 'config': {}, 'enabled': True, 'execution_source': 'HOST'},
            {'type': 'canny', 'config': {'threshold1': 100, 'threshold2': 200}, 'enabled': True, 'execution_source': 'HOST'},
        ]
        row_id = db.save_pipeline('Test Pipeline', 'A test', {'name': 'Test'}, stages)
        assert row_id > 0

    def test_get_pipelines(self, db):
        db.save_pipeline('P1', 'Desc', {}, [])
        db.save_pipeline('P2', 'Desc2', {}, [])
        pipelines = db.get_pipelines()
        assert len(pipelines) == 2

    def test_pipeline_stages(self, db):
        stages = [
            {'type': 'grayscale', 'config': {}, 'enabled': True, 'execution_source': 'HOST'},
        ]
        row_id = db.save_pipeline('P1', 'D', {}, stages)
        pipeline = db.get_pipeline(row_id)
        assert pipeline is not None
        assert len(pipeline['stages']) == 1
        assert pipeline['stages'][0]['stage_type'] == 'grayscale'


class TestModelRegistry:
    """Test model registry persistence."""

    def test_register_model(self, db):
        row_id = db.register_model(
            'test_model', 'classification', '1.0', '/path/model.onnx',
            '(1, 3, 224, 224)', ['cat', 'dog', 'bird'], 'onnx', False,
            {'ir_version': 8}
        )
        assert row_id > 0

    def test_get_models(self, db):
        db.register_model('M1', 'detection', '1.0', '/p1', '(1,3,416,416)',
                         ['obj'], 'onnx', False, {})
        models = db.get_models()
        assert len(models) == 1
        assert models[0]['classes'] == ['obj']


class TestSettings:
    """Test system settings persistence."""

    def test_set_get_setting(self, db):
        db.set_setting('theme', 'dark')
        assert db.get_setting('theme') == 'dark'

    def test_get_default(self, db):
        assert db.get_setting('nonexistent', 'default') == 'default'

    def test_json_setting(self, db):
        db.set_setting('config', {'key': 'value', 'num': 42})
        result = db.get_setting('config')
        assert result['key'] == 'value'
        assert result['num'] == 42


class TestReportHistory:
    """Test report history persistence."""

    def test_log_report(self, db):
        row_id = db.log_report('benchmark', 'Test Report', '/path/report.pdf', 'Summary')
        assert row_id > 0

    def test_get_reports(self, db):
        db.log_report('benchmark', 'R1', '/p1', 'S1')
        db.log_report('system', 'R2', '/p2', 'S2')
        reports = db.query("SELECT * FROM report_history")
        assert len(reports) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
