"""VISIONFORGE X - Modular Vision Processing Engine."""
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class ExecutionSource(Enum):
    HOST = "HOST"
    FPGA = "FPGA"
    ARM = "ARM"
    SIMULATION = "SIMULATION"


@dataclass
class StageResult:
    """Result of a single processing stage."""
    stage_type: str
    output: np.ndarray
    processing_time_ms: float
    execution_source: ExecutionSource
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None


class VisionStage:
    """Base class for all vision processing stages."""

    def __init__(self, name: str, execution_source: ExecutionSource = ExecutionSource.HOST):
        self.name = name
        self.execution_source = execution_source
        self.params: Dict[str, Any] = {}
        self._enabled = True

    def set_param(self, key: str, value: Any):
        self.params[key] = value

    def set_params(self, params: Dict[str, Any]):
        self.params.update(params)

    def set_enabled(self, enabled: bool):
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    def process(self, frame: np.ndarray) -> StageResult:
        """Process a frame. Override in subclasses."""
        raise NotImplementedError

    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'execution_source': self.execution_source.value,
            'params': self.params,
            'enabled': self._enabled
        }


# ---- Concrete Vision Stages ----

class GrayscaleStage(VisionStage):
    def __init__(self):
        super().__init__("grayscale", ExecutionSource.HOST)
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        if frame.size == 0:
            return StageResult(self.name, frame.copy(), 0, self.execution_source,
                              metadata={'shape': frame.shape})
        if len(frame.shape) == 2:
            out = frame.copy()
        else:
            import cv2
            out = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source,
                          metadata={'shape': out.shape})


class GaussianBlurStage(VisionStage):
    def __init__(self, kernel_size: int = 5, sigma: float = 0):
        super().__init__("gaussian_blur", ExecutionSource.HOST)
        self.set_params({'kernel_size': kernel_size, 'sigma': sigma})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        k = self.params.get('kernel_size', 5)
        if k % 2 == 0:
            k += 1
        out = cv2.GaussianBlur(frame, (k, k), self.params.get('sigma', 0))
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class MedianBlurStage(VisionStage):
    def __init__(self, kernel_size: int = 5):
        super().__init__("median_blur", ExecutionSource.HOST)
        self.set_param('kernel_size', kernel_size)
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        k = self.params.get('kernel_size', 5)
        if k % 2 == 0:
            k += 1
        out = cv2.medianBlur(frame, k)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class BilateralFilterStage(VisionStage):
    def __init__(self, d: int = 9, sigma_color: float = 75, sigma_space: float = 75):
        super().__init__("bilateral_filter", ExecutionSource.HOST)
        self.set_params({'d': d, 'sigma_color': sigma_color, 'sigma_space': sigma_space})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        out = cv2.bilateralFilter(
            frame,
            self.params.get('d', 9),
            self.params.get('sigma_color', 75),
            self.params.get('sigma_space', 75)
        )
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class HistogramEqualizationStage(VisionStage):
    def __init__(self):
        super().__init__("histogram_equalization", ExecutionSource.HOST)
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        if len(frame.shape) == 3:
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
            ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
            out = cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR)
        else:
            out = cv2.equalizeHist(frame)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class CLAHEStage(VisionStage):
    def __init__(self, clip_limit: float = 2.0, tile_grid: tuple = (8, 8)):
        super().__init__("clahe", ExecutionSource.HOST)
        self.set_params({'clip_limit': clip_limit, 'tile_grid': tile_grid})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        clip = self.params.get('clip_limit', 2.0)
        tile = self.params.get('tile_grid', (8, 8))
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=tile)
        if len(frame.shape) == 3:
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
            ycrcb[:, :, 0] = clahe.apply(ycrcb[:, :, 0])
            out = cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR)
        else:
            out = clahe.apply(frame)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class GammaCorrectionStage(VisionStage):
    def __init__(self, gamma: float = 1.0):
        super().__init__("gamma_correction", ExecutionSource.HOST)
        self.set_param('gamma', gamma)
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        gamma = self.params.get('gamma', 1.0)
        inv = 1.0 / gamma
        table = (np.arange(0, 256) / 255.0) ** inv * 255
        table = np.clip(table, 0, 255).astype(np.uint8)
        out = cv2.LUT(frame, table) if 'cv2' in dir() else frame
        import cv2
        out = cv2.LUT(frame, table)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class SharpeningStage(VisionStage):
    def __init__(self, strength: float = 1.0):
        super().__init__("sharpening", ExecutionSource.HOST)
        self.set_param('strength', strength)
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        s = self.params.get('strength', 1.0)
        kernel = np.array([
            [0, -s, 0],
            [-s, 1 + 4 * s, -s],
            [0, -s, 0]
        ])
        out = cv2.filter2D(frame, -1, kernel)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class SobelStage(VisionStage):
    def __init__(self, dx: int = 1, dy: int = 0, ksize: int = 3):
        super().__init__("sobel", ExecutionSource.HOST)
        self.set_params({'dx': dx, 'dy': dy, 'ksize': ksize})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        dx = self.params.get('dx', 1)
        dy = self.params.get('dy', 0)
        k = self.params.get('ksize', 3)
        if k % 2 == 0:
            k += 1
        out = cv2.Sobel(gray, cv2.CV_64F, dx, dy, ksize=k)
        out = np.uint8(np.absolute(out))
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source,
                          metadata={'dx': dx, 'dy': dy})


class ScharrStage(VisionStage):
    def __init__(self, dx: int = 1, dy: int = 0):
        super().__init__("scharr", ExecutionSource.HOST)
        self.set_params({'dx': dx, 'dy': dy})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        dx = self.params.get('dx', 1)
        dy = self.params.get('dy', 0)
        out = cv2.Scharr(gray, cv2.CV_64F, dx, dy)
        out = np.uint8(np.absolute(out))
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class CannyStage(VisionStage):
    def __init__(self, threshold1: int = 100, threshold2: int = 200):
        super().__init__("canny", ExecutionSource.HOST)
        self.set_params({'threshold1': threshold1, 'threshold2': threshold2})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        t1 = self.params.get('threshold1', 100)
        t2 = self.params.get('threshold2', 200)
        out = cv2.Canny(gray, t1, t2)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source,
                          metadata={'threshold1': t1, 'threshold2': t2})


class BinaryThresholdStage(VisionStage):
    def __init__(self, threshold: int = 127, max_value: int = 255,
                 threshold_type: int = cv2.THRESH_BINARY if 'cv2' in dir() else 0):
        super().__init__("binary_threshold", ExecutionSource.HOST)
        import cv2
        self.set_params({'threshold': threshold, 'max_value': max_value,
                        'threshold_type': threshold_type})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        t = self.params.get('threshold', 127)
        mv = self.params.get('max_value', 255)
        tt = self.params.get('threshold_type', cv2.THRESH_BINARY)
        _, out = cv2.threshold(gray, t, mv, tt)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class AdaptiveThresholdStage(VisionStage):
    def __init__(self, block_size: int = 11, C: int = 2,
                 threshold_type: int = 0):
        super().__init__("adaptive_threshold", ExecutionSource.HOST)
        import cv2
        self.set_params({'block_size': block_size, 'C': C, 'threshold_type': threshold_type if threshold_type else cv2.THRESH_BINARY})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        bs = self.params.get('block_size', 11)
        if bs % 2 == 0:
            bs += 1
        c = self.params.get('C', 2)
        tt = self.params.get('threshold_type', cv2.THRESH_BINARY)
        out = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, tt, bs, c
        )
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class OtsuThresholdStage(VisionStage):
    def __init__(self):
        super().__init__("otsu_threshold", ExecutionSource.HOST)
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        _, out = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source)


class MorphologyStage(VisionStage):
    """Morphological operations: erosion, dilation, opening, closing."""

    OP_EROSION = 'erosion'
    OP_DILATION = 'dilation'
    OP_OPENING = 'opening'
    OP_CLOSING = 'closing'

    # OpenCV morphology operation codes (compatible across versions)
    OP_CODES = {
        'erosion': 0,    # cv2.MORPH_ERODE
        'dilation': 1,   # cv2.MORPH_DILATE
        'opening': 2,    # cv2.MORPH_OPEN
        'closing': 3,    # cv2.MORPH_CLOSE
    }

    def __init__(self, operation: str = 'opening', kernel_size: int = 3, iterations: int = 1):
        super().__init__("morphology", ExecutionSource.HOST)
        self.set_params({'operation': operation, 'kernel_size': kernel_size, 'iterations': iterations})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        import cv2
        op = self.params.get('operation', 'opening')
        ks = self.params.get('kernel_size', 3)
        if ks % 2 == 0:
            ks += 1
        it = self.params.get('iterations', 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ks, ks))
        cv2_op = self.OP_CODES.get(op, 2)  # default to opening
        out = cv2.morphologyEx(frame, cv2_op, kernel, iterations=it)
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source,
                          metadata={'operation': op, 'kernel_size': ks, 'iterations': it})


class ROIStage(VisionStage):
    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        super().__init__("roi", ExecutionSource.HOST)
        self.set_params({'x': x, 'y': y, 'width': width, 'height': height})
    def process(self, frame: np.ndarray) -> StageResult:
        t0 = time.perf_counter()
        x = self.params.get('x', 0)
        y = self.params.get('y', 0)
        w = self.params.get('width', frame.shape[1] - x)
        h = self.params.get('height', frame.shape[0] - y)
        if w <= 0 or h <= 0:
            out = frame.copy()
        else:
            out = frame[y:y+h, x:x+w].copy()
        elapsed = (time.perf_counter() - t0) * 1000
        return StageResult(self.name, out, elapsed, self.execution_source,
                          metadata={'roi': (x, y, w, h)})


class VisionEngine:
    """Main vision processing engine that orchestrates stages."""

    def __init__(self, execution_source: ExecutionSource = ExecutionSource.HOST):
        self.execution_source = execution_source
        self._stages: List[VisionStage] = []
        self._stage_registry = self._build_registry()

    def _build_registry(self) -> Dict[str, type]:
        return {
            'grayscale': GrayscaleStage,
            'gaussian_blur': GaussianBlurStage,
            'median_blur': MedianBlurStage,
            'bilateral_filter': BilateralFilterStage,
            'histogram_equalization': HistogramEqualizationStage,
            'clahe': CLAHEStage,
            'gamma_correction': GammaCorrectionStage,
            'sharpening': SharpeningStage,
            'sobel': SobelStage,
            'scharr': ScharrStage,
            'canny': CannyStage,
            'binary_threshold': BinaryThresholdStage,
            'adaptive_threshold': AdaptiveThresholdStage,
            'otsu_threshold': OtsuThresholdStage,
            'morphology': MorphologyStage,
            'roi': ROIStage,
        }

    def add_stage(self, stage: VisionStage):
        self._stages.append(stage)

    def remove_stage(self, index: int):
        if 0 <= index < len(self._stages):
            self._stages.pop(index)

    def clear_stages(self):
        self._stages.clear()

    def create_stage(self, stage_type: str, **kwargs) -> Optional[VisionStage]:
        cls = self._stage_registry.get(stage_type)
        if cls:
            return cls(**kwargs)
        return None

    def set_stage_param(self, index: int, key: str, value: Any) -> bool:
        if 0 <= index < len(self._stages):
            self._stages[index].set_param(key, value)
            return True
        return False

    def set_stage_enabled(self, index: int, enabled: bool) -> bool:
        if 0 <= index < len(self._stages):
            self._stages[index].set_enabled(enabled)
            return True
        return False

    def process(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process frame through all enabled stages."""
        t0 = time.perf_counter()
        current = frame.copy()
        results = []
        total_time = 0.0

        for stage in self._stages:
            if not stage.is_enabled():
                continue
            try:
                result = stage.process(current)
                if result.error:
                    results.append(result)
                    continue
                current = result.output
                results.append(result)
                total_time += result.processing_time_ms
            except Exception as e:
                results.append(StageResult(
                    stage.name, frame.copy(), 0, self.execution_source,
                    error=str(e)
                ))

        elapsed = (time.perf_counter() - t0) * 1000
        return {
            'output': current,
            'total_time_ms': elapsed,
            'stage_results': results,
            'stage_count': len([r for r in results if not r.error]),
            'execution_source': self.execution_source.value,
        }

    def get_pipeline_summary(self) -> List[Dict[str, Any]]:
        return [s.get_metadata() for s in self._stages]

    def save_config(self) -> Dict[str, Any]:
        # Map class names back to registry keys
        class_to_key = {
            'GrayscaleStage': 'grayscale',
            'GaussianBlurStage': 'gaussian_blur',
            'MedianBlurStage': 'median_blur',
            'BilateralFilterStage': 'bilateral_filter',
            'HistogramEqualizationStage': 'histogram_equalization',
            'CLAHEStage': 'clahe',
            'GammaCorrectionStage': 'gamma_correction',
            'SharpeningStage': 'sharpening',
            'SobelStage': 'sobel',
            'ScharrStage': 'scharr',
            'CannyStage': 'canny',
            'BinaryThresholdStage': 'binary_threshold',
            'AdaptiveThresholdStage': 'adaptive_threshold',
            'OtsuThresholdStage': 'otsu_threshold',
            'MorphologyStage': 'morphology',
            'ROIStage': 'roi',
        }
        return {
            'stages': [
                {
                    'type': class_to_key.get(type(s).__name__, type(s).__name__.replace('Stage', '').lower()),
                    'params': s.params,
                    'enabled': s._enabled,
                }
                for s in self._stages
            ]
        }

    def load_config(self, config: Dict[str, Any]):
        self.clear_stages()
        for stage_cfg in config.get('stages', []):
            stage_type = stage_cfg.get('type', '')
            params = stage_cfg.get('params', {})
            try:
                stage = self.create_stage(stage_type, **params)
                if stage:
                    stage.set_params(params)
                    stage.set_enabled(stage_cfg.get('enabled', True))
                    self.add_stage(stage)
            except Exception:
                # Skip stages that fail to create (e.g., invalid params)
                pass
