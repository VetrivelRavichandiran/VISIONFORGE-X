"""VISIONFORGE X - Adaptive Controller Tests."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.adaptive.controller import (
    AdaptiveController, AdaptiveMode, SystemMetrics, AdaptiveDecision
)


class TestAdaptiveController:
    """Test adaptive intelligence controller."""

    def test_create_controller(self):
        ctrl = AdaptiveController()
        assert ctrl.enabled is False
        assert ctrl.mode == "balanced"

    def test_enable_disable(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        assert ctrl.enabled is True
        ctrl.disable()
        assert ctrl.enabled is False

    def test_set_mode(self):
        ctrl = AdaptiveController()
        ctrl.set_mode("quality")
        assert ctrl.mode == "quality"
        ctrl.set_mode("performance")
        assert ctrl.mode == "performance"
        ctrl.set_mode("invalid")
        assert ctrl.mode == "performance"  # Should not change

    def test_override(self):
        ctrl = AdaptiveController()
        ctrl.set_override({'filter': 'clahe'})
        assert ctrl._override == {'filter': 'clahe'}
        ctrl.set_override(None)
        assert ctrl._override is None

    def test_evaluate_disabled(self):
        ctrl = AdaptiveController()
        metrics = SystemMetrics()
        decision = ctrl.evaluate(metrics)
        assert decision.triggered is False
        assert "disabled" in decision.reason.lower()

    def test_evaluate_with_override(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        ctrl.set_override({'filter': 'clahe'})
        metrics = SystemMetrics()
        decision = ctrl.evaluate(metrics)
        assert decision.triggered is True
        assert decision.outputs == {'filter': 'clahe'}

    def test_evaluate_high_load(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        ctrl.set_mode("quality")
        metrics = SystemMetrics(cpu_usage=85, memory_usage=90)
        decision = ctrl.evaluate(metrics)
        assert decision.mode == "performance"

    def test_evaluate_low_brightness(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        metrics = SystemMetrics(brightness=0.1)
        decision = ctrl.evaluate(metrics)
        assert 'filter' in decision.outputs
        assert decision.outputs['filter'] == 'clahe'

    def test_evaluate_high_noise(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        metrics = SystemMetrics(noise_estimate=0.1)
        decision = ctrl.evaluate(metrics)
        assert 'denoise' in decision.outputs

    def test_evaluate_high_motion(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        metrics = SystemMetrics(motion_intensity=0.5)
        decision = ctrl.evaluate(metrics)
        assert 'inference_interval' in decision.outputs
        assert decision.outputs['inference_interval'] >= 1

    def test_decision_log(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        metrics = SystemMetrics()
        for _ in range(5):
            ctrl.evaluate(metrics)
        log = ctrl.get_decision_log()
        assert len(log) == 5

    def test_decision_log_limit(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        metrics = SystemMetrics()
        for _ in range(150):
            ctrl.evaluate(metrics)
        log = ctrl.get_decision_log(limit=100)
        assert len(log) == 100

    def test_get_current_state(self):
        ctrl = AdaptiveController()
        ctrl.enable()
        ctrl.set_mode("quality")
        state = ctrl.get_current_state()
        assert state['enabled'] is True
        assert state['mode'] == "quality"

    def test_frame_count(self):
        ctrl = AdaptiveController()
        metrics = SystemMetrics()
        ctrl.evaluate(metrics)
        ctrl.evaluate(metrics)
        assert ctrl._frame_count == 2


class TestSystemMetrics:
    """Test system metrics dataclass."""

    def test_default_metrics(self):
        m = SystemMetrics()
        assert m.brightness == 0.5
        assert m.fps == 0.0
        assert m.cpu_usage == 0.0

    def test_custom_metrics(self):
        m = SystemMetrics(brightness=0.8, fps=25.0, cpu_usage=45.0)
        assert m.brightness == 0.8
        assert m.fps == 25.0


class TestAdaptiveDecision:
    """Test adaptive decision dataclass."""

    def test_decision_creation(self):
        d = AdaptiveDecision(
            timestamp="2024-01-01T00:00:00",
            mode="balanced",
            inputs={'fps': 25.0},
            outputs={'filter': 'clahe'},
            reason="Test",
            triggered=True
        )
        assert d.mode == "balanced"
        assert d.triggered is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
