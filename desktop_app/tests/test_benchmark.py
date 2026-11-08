"""VISIONFORGE X - Benchmark and Analytics Tests."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
from backend.analytics.benchmark import PerformanceTracker, BenchmarkRunner


class TestPerformanceTracker:
    """Test performance tracking."""

    def test_create_tracker(self):
        tracker = PerformanceTracker()
        assert tracker.get_current_fps() == 0.0
        assert tracker.get_avg_latency() == 0.0

    def test_record_frame(self):
        tracker = PerformanceTracker()
        tracker.record_frame(10.0, cpu=30, memory=40)
        assert tracker.get_total_frames() == 1
        assert tracker.get_avg_latency() == 10.0

    def test_record_dropped_frame(self):
        tracker = PerformanceTracker()
        tracker.record_frame(10.0, dropped=True)
        assert tracker.get_dropped_frames() == 1

    def test_latency_stats(self):
        tracker = PerformanceTracker()
        for i in range(100):
            tracker.record_frame(float(i + 1))
        stats = tracker.get_latency_stats()
        assert stats['avg'] > 0
        assert stats['min'] == 1.0
        assert stats['max'] == 100.0
        assert stats['p95'] > stats['median']

    def test_reset(self):
        tracker = PerformanceTracker()
        tracker.record_frame(10.0)
        tracker.reset()
        assert tracker.get_total_frames() == 0
        assert tracker.get_avg_latency() == 0.0

    def test_uptime(self):
        tracker = PerformanceTracker()
        time.sleep(0.1)
        assert tracker.get_uptime() >= 0.1

    def test_history_trimming(self):
        tracker = PerformanceTracker(window_size=10)
        for i in range(20):
            tracker.record_frame(float(i))
        assert len(tracker.get_latency_history()) <= 10


class TestBenchmarkRunner:
    """Test benchmark runner."""

    def test_create_runner(self):
        runner = BenchmarkRunner()
        assert runner.is_running() is False

    def test_start_session(self):
        runner = BenchmarkRunner()
        session_id = runner.start("Test Session", {'res': '640x480'}, 'simulation')
        assert session_id is not None
        assert runner.is_running() is True

    def test_record_metric(self):
        runner = BenchmarkRunner()
        runner.start("S1", {}, 'simulation')
        runner.record_metric('fps', 25.5)
        runner.record_metric('latency_ms', 12.3)
        session = runner.get_current_session()
        assert 'fps' in session.metrics
        assert session.metrics['fps'] == [25.5]

    def test_stop_session(self):
        runner = BenchmarkRunner()
        runner.start("S1", {}, 'simulation')
        runner.record_metric('fps', 25.5)
        session = runner.stop()
        assert session is not None
        assert session.ended_at is not None
        assert runner.is_running() is False

    def test_session_summary(self):
        runner = BenchmarkRunner()
        sid = runner.start("S1", {}, 'simulation')
        for i in range(10):
            runner.record_metric('fps', 20 + i)
        session = runner.stop()
        summary = runner.get_session_results(session.id)
        assert summary['metrics']['fps']['avg'] > 0
        assert summary['metrics']['fps']['count'] == 10
        assert summary['is_simulated'] is True

    def test_multiple_sessions(self):
        runner = BenchmarkRunner()
        runner.start("S1", {}, 'simulation')
        runner.record_metric('fps', 25.0)
        runner.stop()
        runner.start("S2", {}, 'hardware')
        runner.record_metric('fps', 30.0)
        runner.stop()
        sessions = runner.get_sessions()
        assert len(sessions) == 2

    def test_compare_sessions(self):
        runner = BenchmarkRunner()
        sid1 = runner.start("S1", {}, 'simulation')
        runner.record_metric('fps', 25.0)
        runner.stop()
        sid2 = runner.start("S2", {}, 'simulation')
        runner.record_metric('fps', 30.0)
        runner.stop()
        comparison = runner.compare_sessions([sid1, sid2])
        assert comparison['count'] == 2

    def test_no_session_record(self):
        runner = BenchmarkRunner()
        runner.record_metric('fps', 25.0)  # No active session
        assert runner.get_current_session() is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
