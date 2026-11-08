"""VISIONFORGE X - Adaptive Intelligence Controller."""
import logging
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class AdaptiveMode(Enum):
    QUALITY = "quality"
    BALANCED = "balanced"
    PERFORMANCE = "performance"


@dataclass
class SystemMetrics:
    """Current system metrics for adaptive control."""
    brightness: float = 0.5
    contrast: float = 1.0
    noise_estimate: float = 0.0
    sharpness: float = 0.5
    motion_intensity: float = 0.0
    ai_confidence: float = 0.0
    processing_latency_ms: float = 0.0
    fps: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    current_pipeline: str = ""


@dataclass
class AdaptiveDecision:
    """Decision made by adaptive controller."""
    timestamp: str
    mode: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    reason: str
    triggered: bool


class AdaptiveController:
    """Rule-based adaptive intelligence controller.
    
    Adjusts processing parameters based on measured system state.
    Deterministic and testable - no unverified ML claims.
    """

    def __init__(self, default_mode: str = "balanced"):
        self.enabled = False
        self.mode = default_mode
        self._override: Optional[Dict[str, Any]] = None
        self._decision_log: List[AdaptiveDecision] = []
        self._max_log = 1000
        self._frame_count = 0

    def enable(self):
        self.enabled = True
        logger.info("Adaptive controller enabled")

    def disable(self):
        self.enabled = False
        logger.info("Adaptive controller disabled")

    def set_mode(self, mode: str):
        if mode in [m.value for m in AdaptiveMode]:
            self.mode = mode
            logger.info(f"Adaptive mode set to: {mode}")

    def set_override(self, override: Optional[Dict[str, Any]]):
        """Set manual override. None to clear."""
        self._override = override
        if override:
            logger.info(f"Manual override set: {override}")
        else:
            logger.info("Manual override cleared")

    def evaluate(self, metrics: SystemMetrics) -> AdaptiveDecision:
        """Evaluate system state and make adaptation decision."""
        self._frame_count += 1
        timestamp = datetime.now(timezone.utc).isoformat()

        # If manual override, use it
        if self._override:
            decision = AdaptiveDecision(
                timestamp=timestamp,
                mode=self.mode,
                inputs=vars(metrics),
                outputs=self._override,
                reason="Manual override active",
                triggered=True
            )
            self._log_decision(decision)
            return decision

        # If disabled, no adaptation
        if not self.enabled:
            decision = AdaptiveDecision(
                timestamp=timestamp,
                mode=self.mode,
                inputs=vars(metrics),
                outputs={},
                reason="Adaptive controller disabled",
                triggered=False
            )
            self._log_decision(decision)
            return decision

        # Rule-based adaptation
        outputs = {}
        reason = ""

        # Determine effective mode based on system load
        effective_mode = self.mode
        if metrics.cpu_usage > 80 or metrics.memory_usage > 85:
            effective_mode = "performance"
            reason = "High system load -> performance mode"
        elif metrics.fps < 15 and self.mode == "quality":
            effective_mode = "balanced"
            reason = "Low FPS in quality mode -> balanced"
        elif metrics.fps > 25 and self.mode == "performance":
            effective_mode = "balanced"
            reason = "Good FPS in performance mode -> balanced"

        # Adjust based on lighting
        if metrics.brightness < 0.2:
            outputs['filter'] = 'clahe'
            outputs['filter_params'] = {'clip_limit': 3.0}
            reason += " | Low brightness -> CLAHE enhancement"
        elif metrics.brightness > 0.8:
            outputs['filter'] = 'gamma_correction'
            outputs['filter_params'] = {'gamma': 0.8}
            reason += " | High brightness -> gamma correction"

        # Adjust based on noise
        if metrics.noise_estimate > 0.05:
            outputs['denoise'] = 'bilateral'
            outputs['denoise_params'] = {'d': 9, 'sigma_color': 75, 'sigma_space': 75}
            reason += " | High noise -> bilateral filter"

        # Adjust based on motion
        if metrics.motion_intensity > 0.3:
            outputs['inference_interval'] = max(1, int(30 / max(1, metrics.motion_intensity * 30)))
            reason += f" | High motion -> inference every {outputs['inference_interval']} frames"
        else:
            outputs['inference_interval'] = 1

        # Adjust based on sharpness
        if metrics.sharpness < 0.3:
            outputs['sharpen'] = True
            outputs['sharpen_strength'] = 1.5
            reason += " | Low sharpness -> sharpening"

        decision = AdaptiveDecision(
            timestamp=timestamp,
            mode=effective_mode,
            inputs=vars(metrics),
            outputs=outputs,
            reason=reason or "No adaptation needed",
            triggered=bool(outputs)
        )
        self._log_decision(decision)
        return decision

    def _log_decision(self, decision: AdaptiveDecision):
        self._decision_log.append(decision)
        if len(self._decision_log) > self._max_log:
            self._decision_log = self._decision_log[-self._max_log:]

    def get_decision_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [
            {
                'timestamp': d.timestamp,
                'mode': d.mode,
                'inputs': d.inputs,
                'outputs': d.outputs,
                'reason': d.reason,
                'triggered': d.triggered,
            }
            for d in self._decision_log[-limit:]
        ]

    def get_current_state(self) -> Dict[str, Any]:
        return {
            'enabled': self.enabled,
            'mode': self.mode,
            'override': self._override,
            'frame_count': self._frame_count,
            'recent_decisions': self.get_decision_log(10),
        }

    def export_log(self, path: str) -> bool:
        try:
            with open(path, 'w') as f:
                json.dump(self.get_decision_log(10000), f, indent=2)
            return True
        except (IOError, OSError) as e:
            logger.error(f"Failed to export decision log: {e}")
            return False
