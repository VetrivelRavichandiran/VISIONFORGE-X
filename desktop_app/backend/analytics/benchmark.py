"""VISIONFORGE X - Performance Analytics and Benchmarking."""
import time
import logging
import threading
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkSession:
    """A benchmark session."""
    id: int
    name: str
    config: Dict[str, Any]
    mode: str
    is_simulated: bool
    started_at: str
    ended_at: Optional[str] = None
    metrics: Dict[str, List[float]] = field(default_factory=dict)
    stage_times: Dict[str, List[float]] = field(default_factory=dict)


class PerformanceTracker:
    """Tracks real-time performance metrics."""

    def __init__(self, window_size: int = 300):
        self._window_size = window_size
        self._fps_history: List[float] = []
        self._latency_history: List[float] = []
        self._cpu_history: List[float] = []
        self._memory_history: List[float] = []
        self._frame_times: List[float] = []
        self._dropped_frames = 0
        self._total_frames = 0
        self._lock = threading.Lock()
        self._start_time = time.time()

    def record_frame(self, processing_time_ms: float, dropped: bool = False,
                     cpu: float = 0, memory: float = 0):
        """Record a processed frame's metrics."""
        with self._lock:
            now = time.time()
            self._total_frames += 1
            if dropped:
                self._dropped_frames += 1
            self._frame_times.append(now)
            self._latency_history.append(processing_time_ms)
            if cpu:
                self._cpu_history.append(cpu)
            if memory:
                self._memory_history.append(memory)

            # Trim to window
            self._latency_history = self._latency_history[-self._window_size:]
            self._cpu_history = self._cpu_history[-self._window_size:]
            self._memory_history = self._memory_history[-self._window_size:]

            # FPS calculation
            cutoff = now - 1.0
            self._frame_times = [t for t in self._frame_times if t > cutoff]
            self._fps_history.append(len(self._frame_times))
            self._fps_history = self._fps_history[-self._window_size:]

    def get_current_fps(self) -> float:
        with self._lock:
            return float(np.mean(self._fps_history[-30:])) if self._fps_history else 0.0

    def get_avg_latency(self) -> float:
        with self._lock:
            return float(np.mean(self._latency_history)) if self._latency_history else 0.0

    def get_latency_stats(self) -> Dict[str, float]:
        with self._lock:
            if not self._latency_history:
                return {'avg': 0, 'min': 0, 'max': 0, 'median': 0, 'p95': 0}
            arr = np.array(self._latency_history)
            return {
                'avg': float(np.mean(arr)),
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'median': float(np.median(arr)),
                'p95': float(np.percentile(arr, 95)),
            }

    def get_uptime(self) -> float:
        return time.time() - self._start_time

    def get_total_frames(self) -> int:
        with self._lock:
            return self._total_frames

    def get_dropped_frames(self) -> int:
        with self._lock:
            return self._dropped_frames

    def get_fps_history(self, limit: int = 100) -> List[float]:
        with self._lock:
            return list(self._fps_history[-limit:])

    def get_latency_history(self, limit: int = 100) -> List[float]:
        with self._lock:
            return list(self._latency_history[-limit:])

    def get_cpu_history(self, limit: int = 100) -> List[float]:
        with self._lock:
            return list(self._cpu_history[-limit:])

    def get_memory_history(self, limit: int = 100) -> List[float]:
        with self._lock:
            return list(self._memory_history[-limit:])

    def reset(self):
        with self._lock:
            self._fps_history.clear()
            self._latency_history.clear()
            self._cpu_history.clear()
            self._memory_history.clear()
            self._frame_times.clear()
            self._dropped_frames = 0
            self._total_frames = 0
            self._start_time = time.time()


class BenchmarkRunner:
    """Runs performance benchmarks."""

    def __init__(self, db_manager=None, event_manager=None):
        self._db = db_manager
        self._event_mgr = event_manager
        self._sessions: List[BenchmarkSession] = []
        self._current_session: Optional[BenchmarkSession] = None
        self._running = False
        self._counter = 0
        self._lock = threading.Lock()

    def start(self, name: str, config: Dict = None, mode: str = "simulation") -> Optional[int]:
        """Start a new benchmark session."""
        with self._lock:
            self._counter += 1
            session = BenchmarkSession(
                id=self._counter,
                name=name or f"Benchmark {self._counter}",
                config=config or {},
                mode=mode,
                is_simulated=(mode == "simulation"),
                started_at=datetime.now(timezone.utc).isoformat(),
            )
            self._sessions.append(session)
            self._current_session = session
            self._running = True

            if self._db:
                try:
                    self._db.create_benchmark_session(
                        session.name, session.config, session.mode, session.is_simulated
                    )
                except Exception as e:
                    logger.error(f"Failed to persist benchmark session: {e}")

            if self._event_mgr:
                self._event_mgr.emit(
                    'benchmark', 'info',
                    f'Benchmark started: {session.name} ({mode})'
                )

            return session.id

    def stop(self) -> Optional[BenchmarkSession]:
        """Stop current benchmark session."""
        with self._lock:
            if not self._current_session:
                return None
            self._current_session.ended_at = datetime.now(timezone.utc).isoformat()
            self._running = False
            session = self._current_session
            self._current_session = None

            if self._event_mgr:
                self._event_mgr.emit(
                    'benchmark', 'info',
                    f'Benchmark completed: {session.name}',
                    data={'metrics': session.metrics}
                )
            return session

    def record_metric(self, name: str, value: float, stage: str = ""):
        """Record a metric during benchmark."""
        if self._current_session and self._running:
            with self._lock:
                if name not in self._current_session.metrics:
                    self._current_session.metrics[name] = []
                self._current_session.metrics[name].append(value)
                if stage:
                    if stage not in self._current_session.stage_times:
                        self._current_session.stage_times[stage] = []
                    self._current_session.stage_times[stage].append(value)

                if self._db:
                    try:
                        self._db.insert_benchmark_metric(
                            self._current_session.id, name, value, stage
                        )
                    except Exception:
                        pass

    def get_current_session(self) -> Optional[BenchmarkSession]:
        return self._current_session

    def is_running(self) -> bool:
        return self._running

    def get_sessions(self) -> List[BenchmarkSession]:
        return list(self._sessions)

    def get_session_results(self, session_id: int) -> Optional[Dict[str, Any]]:
        for s in self._sessions:
            if s.id == session_id:
                return self._summarize(s)
        return None

    def _summarize(self, session: BenchmarkSession) -> Dict[str, Any]:
        """Summarize benchmark session results."""
        summary = {
            'id': session.id,
            'name': session.name,
            'mode': session.mode,
            'is_simulated': session.is_simulated,
            'started_at': session.started_at,
            'ended_at': session.ended_at,
            'duration_seconds': None,
            'metrics': {},
        }

        if session.ended_at:
            start = datetime.fromisoformat(session.started_at)
            end = datetime.fromisoformat(session.ended_at)
            summary['duration_seconds'] = (end - start).total_seconds()

        for name, values in session.metrics.items():
            arr = np.array(values)
            summary['metrics'][name] = {
                'avg': float(np.mean(arr)),
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'median': float(np.median(arr)),
                'p95': float(np.percentile(arr, 95)),
                'count': len(values),
            }

        return summary

    def compare_sessions(self, session_ids: List[int]) -> Dict[str, Any]:
        """Compare multiple benchmark sessions."""
        comparisons = []
        for sid in session_ids:
            result = self.get_session_results(sid)
            if result:
                comparisons.append(result)

        return {
            'sessions': comparisons,
            'count': len(comparisons),
        }
