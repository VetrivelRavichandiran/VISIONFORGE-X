"""VISIONFORGE X - Event Management System."""
import logging
import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class EventCategory(Enum):
    DEVICE = "device"
    CAMERA = "camera"
    PROCESSING = "processing"
    PIPELINE = "pipeline"
    AI = "ai"
    MOTION = "motion"
    ANOMALY = "anomaly"
    BENCHMARK = "benchmark"
    ERROR = "error"
    SYSTEM = "system"


class EventSeverity(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Event:
    """System event."""
    id: str
    timestamp: str
    category: str
    severity: str
    description: str
    snapshot_path: str = ""
    related_model: str = ""
    related_pipeline: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'category': self.category,
            'severity': self.severity,
            'description': self.description,
            'snapshot_path': self.snapshot_path,
            'related_model': self.related_model,
            'related_pipeline': self.related_pipeline,
            'data': self.data,
            'acknowledged': self.acknowledged,
        }


class EventManager:
    """Manages system events with callbacks and persistence."""

    def __init__(self, db_manager=None, max_buffer: int = 10000):
        self._db = db_manager
        self._buffer: List[Event] = []
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []
        self._counter = 0
        self._max_buffer = max_buffer

    def on_event(self, callback: Callable):
        """Register event callback."""
        self._callbacks.append(callback)

    def emit(self, category: str, severity: str, description: str,
             snapshot_path: str = "", related_model: str = "",
             related_pipeline: str = "", data: Dict = None) -> Event:
        """Create and emit an event."""
        self._counter += 1
        event = Event(
            id=f"evt_{self._counter:06d}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            category=category,
            severity=severity,
            description=description,
            snapshot_path=snapshot_path,
            related_model=related_model,
            related_pipeline=related_pipeline,
            data=data or {},
        )

        with self._lock:
            self._buffer.append(event)
            if len(self._buffer) > self._max_buffer:
                self._buffer = self._buffer[-self._max_buffer:]

        # Persist to database
        if self._db:
            try:
                self._db.insert_event(event.to_dict())
            except Exception as e:
                logger.error(f"Failed to persist event: {e}")

        # Notify callbacks
        for cb in self._callbacks:
            try:
                cb(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")

        return event

    def get_events(self, category: str = None, severity: str = None,
                   limit: int = 100, acknowledged: bool = None) -> List[Event]:
        """Get events with optional filters."""
        with self._lock:
            events = list(self._buffer)

        if category:
            events = [e for e in events if e.category == category]
        if severity:
            events = [e for e in events if e.severity == severity]
        if acknowledged is not None:
            events = [e for e in events if e.acknowledged == acknowledged]

        return events[-limit:]

    def acknowledge(self, event_id: str) -> bool:
        """Acknowledge an event."""
        with self._lock:
            for event in self._buffer:
                if event.id == event_id:
                    event.acknowledged = True
                    if self._db:
                        try:
                            self._db.acknowledge_event(event_id)
                        except Exception:
                            pass
                    return True
        return False

    def clear(self):
        """Clear all events."""
        with self._lock:
            self._buffer.clear()

    def get_buffer_size(self) -> int:
        with self._lock:
            return len(self._buffer)
