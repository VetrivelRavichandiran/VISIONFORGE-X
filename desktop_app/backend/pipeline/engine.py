"""VISIONFORGE X - Pipeline Architecture Engine."""
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class NodeType(Enum):
    CAMERA_INPUT = "camera_input"
    GRAYSCALE = "grayscale"
    GAUSSIAN_BLUR = "gaussian_blur"
    MEDIAN_FILTER = "median_filter"
    CLAHE = "clahe"
    EDGE_DETECTION = "edge_detection"
    THRESHOLD = "threshold"
    MORPHOLOGY = "morphology"
    MOTION_DETECTION = "motion_detection"
    ROI = "roi"
    AI_INFERENCE = "ai_inference"
    ANOMALY_DETECTION = "anomaly_detection"
    OUTPUT = "output"
    RECORDING = "recording"


@dataclass
class PipelineNode:
    """A node in the processing pipeline."""
    id: str
    node_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    execution_source: str = "HOST"
    position: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0})

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'node_type': self.node_type,
            'config': self.config,
            'enabled': self.enabled,
            'execution_source': self.execution_source,
            'position': self.position,
        }


@dataclass
class PipelineConnection:
    """Connection between two nodes."""
    source_id: str
    target_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {'source_id': self.source_id, 'target_id': self.target_id}


@dataclass
class PipelineTemplate:
    """Predefined pipeline template."""
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]


class PipelineValidator:
    """Validates pipeline configurations."""

    VALID_NODE_TYPES = {n.value for n in NodeType}
    INPUT_NODES = {NodeType.CAMERA_INPUT.value}
    OUTPUT_NODES = {NodeType.OUTPUT.value, NodeType.RECORDING.value}

    @classmethod
    def validate(cls, nodes: List[PipelineNode], connections: List[PipelineConnection]
                 ) -> tuple:
        """Validate pipeline. Returns (is_valid, errors)."""
        errors = []

        if not nodes:
            errors.append("Pipeline must have at least one node")
            return False, errors

        node_ids = {n.id for n in nodes}

        # Check for duplicate IDs
        if len(node_ids) != len(nodes):
            errors.append("Duplicate node IDs detected")

        # Check node types
        for node in nodes:
            if node.node_type not in cls.VALID_NODE_TYPES:
                errors.append(f"Invalid node type: {node.node_type}")

        # Check connections reference valid nodes
        for conn in connections:
            if conn.source_id not in node_ids:
                errors.append(f"Connection source not found: {conn.source_id}")
            if conn.target_id not in node_ids:
                errors.append(f"Connection target not found: {conn.target_id}")

        # Check for cycles (simple DFS)
        adj = {n.id: [] for n in nodes}
        for conn in connections:
            adj[conn.source_id].append(conn.target_id)

        visited = set()
        rec_stack = set()

        def has_cycle(node_id):
            visited.add(node_id)
            rec_stack.add(node_id)
            for neighbor in adj.get(node_id, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node_id)
            return False

        for node_id in node_ids:
            if node_id not in visited:
                if has_cycle(node_id):
                    errors.append("Pipeline contains a cycle")
                    break

        # Check for input node
        has_input = any(n.node_type in cls.INPUT_NODES for n in nodes if n.enabled)
        if not has_input and len([n for n in nodes if n.enabled]) > 0:
            errors.append("Pipeline must have an input node (camera_input)")

        is_valid = len(errors) == 0
        return is_valid, errors


class PipelineEngine:
    """Executes processing pipelines safely."""

    def __init__(self, device=None):
        self._nodes: Dict[str, PipelineNode] = {}
        self._connections: List[PipelineConnection] = []
        self._active_pipeline: Optional[str] = None
        self._device = device
        self._node_processors: Dict[str, Callable] = {}
        self._running = False
        self._register_processors()

    def _register_processors(self):
        """Register node type processors."""
        self._node_processors = {
            NodeType.GRAYSCALE.value: self._process_grayscale,
            NodeType.GAUSSIAN_BLUR.value: self._process_gaussian_blur,
            NodeType.MEDIAN_FILTER.value: self._process_median_filter,
            NodeType.CLAHE.value: self._process_clahe,
            NodeType.EDGE_DETECTION.value: self._process_edge_detection,
            NodeType.THRESHOLD.value: self._process_threshold,
            NodeType.MORPHOLOGY.value: self._process_morphology,
            NodeType.ROI.value: self._process_roi,
            NodeType.MOTION_DETECTION.value: self._process_motion,
            NodeType.AI_INFERENCE.value: self._process_ai,
            NodeType.ANOMALY_DETECTION.value: self._process_anomaly,
        }

    def add_node(self, node: PipelineNode):
        self._nodes[node.id] = node

    def remove_node(self, node_id: str):
        if node_id in self._nodes:
            del self._nodes[node_id]
            self._connections = [
                c for c in self._connections
                if c.source_id != node_id and c.target_id != node_id
            ]

    def connect(self, source_id: str, target_id: str):
        conn = PipelineConnection(source_id, target_id)
        if conn not in self._connections:
            self._connections.append(conn)

    def disconnect(self, source_id: str, target_id: str):
        self._connections = [
            c for c in self._connections
            if not (c.source_id == source_id and c.target_id == target_id)
        ]

    def set_node_param(self, node_id: str, key: str, value: Any) -> bool:
        if node_id in self._nodes:
            self._nodes[node_id].config[key] = value
            return True
        return False

    def set_node_enabled(self, node_id: str, enabled: bool) -> bool:
        if node_id in self._nodes:
            self._nodes[node_id].enabled = enabled
            return True
        return False

    def validate(self) -> tuple:
        return PipelineValidator.validate(
            list(self._nodes.values()), self._connections
        )

    def get_topology(self) -> List[List[str]]:
        """Get pipeline as ordered list of node chains."""
        if not self._nodes:
            return []

        # Build adjacency
        adj = {n: [] for n in self._nodes}
        in_degree = {n: 0 for n in self._nodes}
        for conn in self._connections:
            if conn.source_id in adj and conn.target_id in adj:
                adj[conn.source_id].append(conn.target_id)
                in_degree[conn.target_id] += 1

        # Topological sort
        queue = [n for n, d in in_degree.items() if d == 0]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Group into chains
        chains = []
        current_chain = []
        for node_id in order:
            current_chain.append(node_id)
            successors = [c for c in self._connections if c.source_id == node_id]
            if len(successors) <= 1:
                if len(successors) == 0:
                    chains.append(current_chain)
                    current_chain = []
            else:
                chains.append(current_chain)
                current_chain = []
        if current_chain:
            chains.append(current_chain)
        return chains

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a frame through the active pipeline."""
        if not self._nodes:
            return {'output': frame, 'stages': [], 'total_time_ms': 0}

        is_valid, errors = self.validate()
        if not is_valid:
            logger.error(f"Invalid pipeline: {errors}")
            return {'output': frame, 'stages': [], 'total_time_ms': 0, 'errors': errors}

        t0 = time.perf_counter()
        current = frame.copy()
        stages = []

        # Find input nodes
        input_nodes = [n for n in self._nodes.values()
                       if n.node_type == NodeType.CAMERA_INPUT.value and n.enabled]

        if not input_nodes:
            input_nodes = [n for n in self._nodes.values() if n.enabled][:1]

        # Process through enabled nodes in order
        processed_nodes = set()
        for node in self._nodes.values():
            if not node.enabled or node.node_type in (NodeType.CAMERA_INPUT.value,
                                                        NodeType.OUTPUT.value,
                                                        NodeType.RECORDING.value):
                continue

            node_type = node.node_type
            processor = self._node_processors.get(node_type)
            if processor:
                try:
                    t1 = time.perf_counter()
                    result = processor(current, node.config)
                    elapsed = (time.perf_counter() - t1) * 1000
                    if isinstance(result, tuple):
                        current = result[0]
                        extra = result[1] if len(result) > 1 else {}
                    else:
                        extra = {}
                    stages.append({
                        'node_id': node.id,
                        'node_type': node_type,
                        'time_ms': elapsed,
                        'execution_source': node.execution_source,
                        **extra
                    })
                    processed_nodes.add(node.id)
                except Exception as e:
                    logger.error(f"Pipeline node error ({node_type}): {e}")
                    stages.append({
                        'node_id': node.id,
                        'node_type': node_type,
                        'error': str(e),
                        'execution_source': node.execution_source,
                    })

        total_time = (time.perf_counter() - t0) * 1000
        return {
            'output': current,
            'stages': stages,
            'total_time_ms': total_time,
            'node_count': len(processed_nodes),
        }

    # ---- Individual node processors ----

    def _process_grayscale(self, frame, config):
        import cv2
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def _process_gaussian_blur(self, frame, config):
        import cv2
        k = config.get('kernel_size', 5)
        if k % 2 == 0:
            k += 1
        return cv2.GaussianBlur(frame, (k, k), 0)

    def _process_median_filter(self, frame, config):
        import cv2
        k = config.get('kernel_size', 5)
        if k % 2 == 0:
            k += 1
        return cv2.medianBlur(frame, k)

    def _process_clahe(self, frame, config):
        import cv2
        clahe = cv2.createCLAHE(
            clipLimit=config.get('clip_limit', 2.0),
            tileGridSize=config.get('tile_grid', (8, 8))
        )
        if len(frame.shape) == 3:
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
            ycrcb[:, :, 0] = clahe.apply(ycrcb[:, :, 0])
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR)
        return clahe.apply(frame)

    def _process_edge_detection(self, frame, config):
        import cv2
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        t1 = config.get('threshold1', 100)
        t2 = config.get('threshold2', 200)
        return cv2.Canny(gray, t1, t2)

    def _process_threshold(self, frame, config):
        import cv2
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        t = config.get('threshold', 127)
        _, out = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
        return out

    def _process_morphology(self, frame, config):
        import cv2
        op = config.get('operation', 'opening')
        ks = config.get('kernel_size', 3)
        if ks % 2 == 0:
            ks += 1
        it = config.get('iterations', 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ks, ks))
        ops = {'erosion': cv2.MORPH_ERODE, 'dilation': cv2.MORPH_DILATE,
               'opening': cv2.MORPH_OPEN, 'closing': cv2.MORPH_CLOSE}
        return cv2.morphologyEx(frame, ops.get(op, cv2.MORPH_OPEN), kernel, iterations=it)

    def _process_roi(self, frame, config):
        x = int(config.get('x', 0))
        y = int(config.get('y', 0))
        w = int(config.get('width', frame.shape[1] - x))
        h = int(config.get('height', frame.shape[0] - y))
        if w > 0 and h > 0:
            return frame[y:y+h, x:x+w].copy()
        return frame

    def _process_motion(self, frame, config):
        from backend.vision.motion import MotionDetector
        detector = MotionDetector(
            threshold=config.get('threshold', 25),
            min_area=config.get('min_area', 500)
        )
        result = detector.detect_frame_diff(frame)
        return frame, {
            'motion_intensity': result.motion_intensity,
            'detection_time_ms': result.processing_time_ms,
        }

    def _process_ai(self, frame, config):
        # AI inference handled by AI registry
        return frame, {'inference_skipped': True}

    def _process_anomaly(self, frame, config):
        from backend.ai.registry import AnomalyEngine
        engine = AnomalyEngine()
        result = engine.infer(frame)
        return frame, {
            'anomaly_score': result.predictions[0]['anomaly_score'] if result.predictions else 0,
        }

    def get_config(self) -> Dict[str, Any]:
        return {
            'nodes': [n.to_dict() for n in self._nodes.values()],
            'connections': [c.to_dict() for c in self._connections],
        }

    def load_config(self, config: Dict[str, Any]):
        self._nodes.clear()
        self._connections.clear()
        for node_data in config.get('nodes', []):
            node = PipelineNode(
                id=node_data['id'],
                node_type=node_data['node_type'],
                config=node_data.get('config', {}),
                enabled=node_data.get('enabled', True),
                execution_source=node_data.get('execution_source', 'HOST'),
                position=node_data.get('position', {'x': 0, 'y': 0}),
            )
            self._nodes[node.id] = node
        for conn_data in config.get('connections', []):
            self._connections.append(PipelineConnection(
                conn_data['source_id'], conn_data['target_id']
            ))

    def get_templates() -> List[PipelineTemplate]:
        """Return predefined pipeline templates."""
        return [
            PipelineTemplate(
                name="Basic Enhancement",
                description="Grayscale + CLAHE + Edge detection",
                nodes=[
                    {'id': 'cam', 'node_type': 'camera_input', 'config': {}},
                    {'id': 'gray', 'node_type': 'grayscale', 'config': {}},
                    {'id': 'clahe', 'node_type': 'clahe', 'config': {'clip_limit': 2.5}},
                    {'id': 'edge', 'node_type': 'edge_detection', 'config': {'threshold1': 50, 'threshold2': 150}},
                    {'id': 'out', 'node_type': 'output', 'config': {}},
                ],
                connections=[
                    {'source_id': 'cam', 'target_id': 'gray'},
                    {'source_id': 'gray', 'target_id': 'clahe'},
                    {'source_id': 'clahe', 'target_id': 'edge'},
                    {'source_id': 'edge', 'target_id': 'out'},
                ]
            ),
            PipelineTemplate(
                name="Motion Detection",
                description="Background subtraction with tracking",
                nodes=[
                    {'id': 'cam', 'node_type': 'camera_input', 'config': {}},
                    {'id': 'motion', 'node_type': 'motion_detection', 'config': {'threshold': 25, 'min_area': 500}},
                    {'id': 'out', 'node_type': 'output', 'config': {}},
                ],
                connections=[
                    {'source_id': 'cam', 'target_id': 'motion'},
                    {'source_id': 'motion', 'target_id': 'out'},
                ]
            ),
            PipelineTemplate(
                name="AI Analysis",
                description="Enhancement + AI inference",
                nodes=[
                    {'id': 'cam', 'node_type': 'camera_input', 'config': {}},
                    {'id': 'blur', 'node_type': 'gaussian_blur', 'config': {'kernel_size': 5}},
                    {'id': 'ai', 'node_type': 'ai_inference', 'config': {'interval': 1}},
                    {'id': 'out', 'node_type': 'output', 'config': {}},
                ],
                connections=[
                    {'source_id': 'cam', 'target_id': 'blur'},
                    {'source_id': 'blur', 'target_id': 'ai'},
                    {'source_id': 'ai', 'target_id': 'out'},
                ]
            ),
        ]

    get_templates = staticmethod(get_templates)
