"""VISIONFORGE X - Motion Intelligence Module."""
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MotionDetectionResult:
    """Result of motion detection."""
    motion_mask: np.ndarray
    motion_intensity: float
    contours: List
    centroids: List[Tuple[int, int]]
    bounding_boxes: List[Tuple[int, int, int, int]]
    processing_time_ms: float
    tracked_objects: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TrackedObject:
    """A tracked object with trajectory."""
    track_id: int
    centroid: Tuple[int, int]
    bbox: Tuple[int, int, int, int]
    history: List[Tuple[int, int]] = field(default_factory=list)
    age: int = 0
    confidence: float = 1.0


class MotionDetector:
    """Motion detection using frame differencing and background subtraction."""

    def __init__(self, threshold: int = 25, min_area: int = 500):
        self.threshold = threshold
        self.min_area = min_area
        self._prev_frame: Optional[np.ndarray] = None
        self._bg_model: Optional[np.ndarray] = None
        self._bg_initialized = False
        self._bg_alpha = 0.02  # Running average learning rate

    def set_threshold(self, threshold: int):
        self.threshold = max(1, min(255, threshold))

    def set_min_area(self, min_area: int):
        self.min_area = max(10, min_area)

    def reset(self):
        self._prev_frame = None
        self._bg_model = None
        self._bg_initialized = False

    def detect_frame_diff(self, frame: np.ndarray) -> MotionDetectionResult:
        """Frame differencing motion detection."""
        t0 = time.perf_counter()
        import cv2

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if self._prev_frame is None:
            self._prev_frame = gray.copy()
            motion_mask = np.zeros_like(gray)
        else:
            diff = cv2.absdiff(gray, self._prev_frame)
            _, motion_mask = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
            motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE,
                                           cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
            motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN,
                                           cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

        self._prev_frame = gray.copy()

        contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid_contours = [c for c in contours if cv2.contourArea(c) > self.min_area]
        centroids = [cv2.moments(c) for c in valid_contours]
        centroids = [(int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
                     for m in centroids if m['m00'] != 0]
        bboxes = [cv2.boundingRect(c) for c in valid_contours]

        intensity = float(np.count_nonzero(motion_mask)) / motion_mask.size

        elapsed = (time.perf_counter() - t0) * 1000
        return MotionDetectionResult(
            motion_mask=motion_mask,
            motion_intensity=intensity,
            contours=valid_contours,
            centroids=centroids,
            bounding_boxes=bboxes,
            processing_time_ms=elapsed,
        )

    def detect_background_sub(self, frame: np.ndarray) -> MotionDetectionResult:
        """Background subtraction with running average."""
        t0 = time.perf_counter()
        import cv2

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if not self._bg_initialized:
            self._bg_model = gray.astype(np.float32).copy()
            self._bg_initialized = True
            motion_mask = np.zeros_like(gray)
        else:
            diff = cv2.absdiff(gray, self._bg_model.astype(np.uint8))
            _, motion_mask = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
            motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE,
                                           cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
            # Update background
            self._bg_model = (1 - self._bg_alpha) * self._bg_model + self._bg_alpha * gray.astype(np.float32)

        contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid_contours = [c for c in contours if cv2.contourArea(c) > self.min_area]
        centroids = []
        for c in valid_contours:
            m = cv2.moments(c)
            if m['m00'] != 0:
                centroids.append((int(m['m10'] / m['m00']), int(m['m01'] / m['m00'])))
        bboxes = [cv2.boundingRect(c) for c in valid_contours]
        intensity = float(np.count_nonzero(motion_mask)) / motion_mask.size

        elapsed = (time.perf_counter() - t0) * 1000
        return MotionDetectionResult(
            motion_mask=motion_mask,
            motion_intensity=intensity,
            contours=valid_contours,
            centroids=centroids,
            bounding_boxes=bboxes,
            processing_time_ms=elapsed,
        )

    def compute_optical_flow(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute Lucas-Kanade optical flow."""
        import cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if self._prev_frame is None:
            self._prev_frame = gray.copy()
            return np.zeros_like(gray), np.zeros((100, 1, 2), dtype=np.float32)

        p0 = cv2.goodFeaturesToTrack(self._prev_frame, maxCorners=100,
                                     qualityLevel=0.01, minDistance=10, blockSize=7)
        if p0 is None:
            self._prev_frame = gray.copy()
            return np.zeros_like(gray), np.zeros((0, 1, 2), dtype=np.float32)

        try:
            p1, st, _ = cv2.calcOpticalFlowPyrLK(self._prev_frame, gray, p0, None,
                                                  maxLevel=2,
                                                  criteria=(cv2.TERM_CRITERIA_EPS |
                                                            cv2.TERM_CRITERIA_COUNT, 30, 0.01))
            if p1 is not None and st is not None:
                good_new = p1[st == 1]
                good_old = p0[st == 1]
                flow = good_new - good_old
                mag, _ = cv2.phase(np.zeros_like(flow[:, :, 0]), flow[:, :, 0],
                                   cyclic=True) if flow.shape[0] > 0 else (np.array([]), np.array([]))
                if len(flow) > 0:
                    mag = np.sqrt(np.sum(flow ** 2, axis=2))
                else:
                    mag = np.array([])
                self._prev_frame = gray.copy()
                return mag, good_new
        except Exception:
            pass

        self._prev_frame = gray.copy()
        return np.zeros_like(gray), np.zeros((0, 1, 2), dtype=np.float32)


class ObjectTracker:
    """Simple centroid-based object tracker."""

    def __init__(self, max_displacement: int = 50, max_age: int = 30):
        self.max_displacement = max_displacement
        self.max_age = max_age
        self._objects: Dict[int, TrackedObject] = {}
        self._next_id = 0
        self._centroids: List[Tuple[int, int]] = []

    def update(self, centroids: List[Tuple[int, int]], bboxes: List[Tuple[int, int, int, int]]
               ) -> List[TrackedObject]:
        """Update tracker with new detections."""
        if not centroids:
            # Age all objects
            for obj in self._objects.values():
                obj.age += 1
            self._centroids = []
            return [o for o in self._objects.values() if o.age <= self.max_age]

        if not self._centroids:
            # First frame - create new objects
            for i, (cx, cy) in enumerate(centroids):
                bbox = bboxes[i] if i < len(bboxes) else (0, 0, 0, 0)
                self._objects[self._next_id] = TrackedObject(
                    track_id=self._next_id, centroid=(cx, cy),
                    bbox=bbox, history=[(cx, cy)], age=0
                )
                self._next_id += 1
        else:
            # Match centroids to existing objects
            matched = set()
            for obj_id, obj in list(self._objects.items()):
                best_dist = float('inf')
                best_idx = -1
                for i, (cx, cy) in enumerate(centroids):
                    if i in matched:
                        continue
                    dist = np.sqrt((cx - obj.centroid[0]) ** 2 + (cy - obj.centroid[1]) ** 2)
                    if dist < best_dist and dist < self.max_displacement:
                        best_dist = dist
                        best_idx = i
                if best_idx >= 0:
                    matched.add(best_idx)
                    obj.centroid = centroids[best_idx]
                    obj.bbox = bboxes[best_idx] if best_idx < len(bboxes) else obj.bbox
                    obj.history.append(centroids[best_idx])
                    obj.history = obj.history[-50:]  # Keep last 50 positions
                    obj.age = 0
                else:
                    obj.age += 1

            # Create new objects for unmatched centroids
            for i, (cx, cy) in enumerate(centroids):
                if i not in matched:
                    bbox = bboxes[i] if i < len(bboxes) else (0, 0, 0, 0)
                    self._objects[self._next_id] = TrackedObject(
                        track_id=self._next_id, centroid=(cx, cy),
                        bbox=bbox, history=[(cx, cy)], age=0
                    )
                    self._next_id += 1

        # Remove old objects
        self._objects = {k: v for k, v in self._objects.items() if v.age <= self.max_age}
        self._centroids = centroids

        return list(self._objects.values())

    def get_active_count(self) -> int:
        return len([o for o in self._objects.values() if o.age <= self.max_age])


class MotionZone:
    """Configurable motion detection zone."""

    def __init__(self, name: str, points: List[Tuple[int, int]]):
        self.name = name
        self.points = np.array(points, dtype=np.int32)
        self.entry_count = 0
        self.exit_count = 0
        self.current_objects = 0

    def contains(self, point: Tuple[int, int]) -> bool:
        import cv2
        return cv2.pointPolygonTest(self.points, point, False) >= 0

    def draw(self, frame: np.ndarray, color: Tuple = (0, 255, 255), thickness: int = 2):
        import cv2
        cv2.polylines(frame, [self.points], True, color, thickness)


class MotionAnalyzer:
    """High-level motion analysis combining detection and tracking."""

    def __init__(self, method: str = "frame_diff"):
        self.method = method
        self.detector = MotionDetector()
        self.tracker = ObjectTracker()
        self.zones: List[MotionZone] = []
        self._entry_events: List[Dict] = []
        self._exit_events: List[Dict] = []
        self._heatmap: Optional[np.ndarray] = None

    def set_method(self, method: str):
        self.method = method

    def add_zone(self, zone: MotionZone):
        self.zones.append(zone)

    def clear_zones(self):
        self.zones.clear()

    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """Run full motion analysis on a frame."""
        if self.method == "frame_diff":
            result = self.detector.detect_frame_diff(frame)
        else:
            result = self.detector.detect_background_sub(frame)

        # Track objects
        tracked = self.tracker.update(result.centroids, result.bounding_boxes)

        # Check zones
        zone_counts = {}
        for zone in self.zones:
            count = sum(1 for c in result.centroids if zone.contains(c))
            zone_counts[zone.name] = count
            zone.current_objects = count

        # Build heatmap
        import cv2
        if self._heatmap is None or self._heatmap.shape[:2] != frame.shape[:2]:
            self._heatmap = np.zeros(frame.shape[:2], dtype=np.float32)
        for cx, cy in result.centroids:
            self._heatmap[cy, cx] = min(255, self._heatmap[cy, cx] + 10)
        self._heatmap = cv2.GaussianBlur(self._heatmap, (15, 15), 0)

        return {
            'motion_mask': result.motion_mask,
            'motion_intensity': result.motion_intensity,
            'bounding_boxes': result.bounding_boxes,
            'tracked_objects': [
                {
                    'id': o.track_id,
                    'centroid': o.centroid,
                    'bbox': o.bbox,
                    'history': o.history,
                    'age': o.age,
                }
                for o in tracked
            ],
            'active_count': self.tracker.get_active_count(),
            'zone_counts': zone_counts,
            'heatmap': self._heatmap,
            'processing_time_ms': result.processing_time_ms,
        }

    def draw_analysis(self, frame: np.ndarray, analysis: Dict) -> np.ndarray:
        """Draw motion analysis overlays on frame."""
        import cv2
        out = frame.copy()

        # Draw bounding boxes
        for obj in analysis.get('tracked_objects', []):
            x, y, w, h = obj['bbox']
            cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(out, f"ID:{obj['id']}", (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Draw trajectories
        for obj in analysis.get('tracked_objects', []):
            history = obj.get('history', [])
            if len(history) > 1:
                for i in range(1, len(history)):
                    pt1 = history[i - 1]
                    pt2 = history[i]
                    alpha = i / len(history)
                    color = (0, int(255 * alpha), int(255 * (1 - alpha)))
                    cv2.line(out, pt1, pt2, color, 2)

        # Draw zones
        for zone in self.zones:
            zone.draw(out)

        # Draw heatmap overlay
        heatmap = analysis.get('heatmap')
        if heatmap is not None and heatmap.shape[:2] == out.shape[:2]:
            heatmap_color = cv2.applyColorMap(heatmap.astype(np.uint8), cv2.COLORMAP_JET)
            out = cv2.addWeighted(out, 0.7, heatmap_color, 0.3, 0)

        return out

    def reset(self):
        self.detector.reset()
        self.tracker = ObjectTracker()
        self._heatmap = None
