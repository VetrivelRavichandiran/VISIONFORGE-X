"""VISIONFORGE X - Vision Engine Tests."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import cv2
from backend.vision.engine import (
    VisionEngine, ExecutionSource, StageResult,
    GrayscaleStage, GaussianBlurStage, MedianBlurStage, CLAHEStage,
    CannyStage, BinaryThresholdStage, MorphologyStage, ROIStage,
    SobelStage, SharpeningStage
)


@pytest.fixture
def test_frame():
    """Create a test frame."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (100, 100), (300, 350), (0, 255, 255), -1)
    cv2.circle(frame, (500, 240), 80, (255, 0, 255), -1)
    return frame


@pytest.fixture
def test_gray():
    """Create a test grayscale frame."""
    return np.random.randint(0, 255, (480, 640), dtype=np.uint8)


class TestVisionStages:
    """Test individual vision processing stages."""

    def test_grayscale_output_shape(self, test_frame):
        stage = GrayscaleStage()
        result = stage.process(test_frame)
        assert result.output.shape == (480, 640)
        assert len(result.output.shape) == 2
        assert result.processing_time_ms >= 0
        assert result.error is None

    def test_grayscale_idempotent(self, test_gray):
        stage = GrayscaleStage()
        result = stage.process(test_gray)
        np.testing.assert_array_equal(result.output, test_gray)

    def test_gaussian_blur(self, test_frame):
        stage = GaussianBlurStage(kernel_size=5)
        result = stage.process(test_frame)
        assert result.output.shape == test_frame.shape
        assert result.output.dtype == np.uint8

    def test_gaussian_blur_even_kernel(self, test_frame):
        stage = GaussianBlurStage(kernel_size=4)  # Even - should become 5
        result = stage.process(test_frame)
        assert result.output.shape == test_frame.shape

    def test_median_blur(self, test_frame):
        stage = MedianBlurStage(kernel_size=3)
        result = stage.process(test_frame)
        assert result.output.shape == test_frame.shape

    def test_clahe_color(self, test_frame):
        stage = CLAHEStage(clip_limit=2.5)
        result = stage.process(test_frame)
        assert result.output.shape == test_frame.shape
        assert result.output.dtype == np.uint8

    def test_clahe_grayscale(self, test_gray):
        stage = CLAHEStage()
        result = stage.process(test_gray)
        assert result.output.shape == test_gray.shape

    def test_canny_edge(self, test_frame):
        stage = CannyStage(threshold1=50, threshold2=150)
        result = stage.process(test_frame)
        assert result.output.shape == (480, 640)
        assert result.output.dtype == np.uint8
        assert result.output.max() == 255 or result.output.max() == 0

    def test_binary_threshold(self, test_gray):
        stage = BinaryThresholdStage(threshold=127)
        result = stage.process(test_gray)
        assert result.output.shape == test_gray.shape
        assert set(np.unique(result.output)).issubset({0, 255})

    def test_morphology_opening(self, test_frame):
        stage = MorphologyStage(operation='opening', kernel_size=3)
        result = stage.process(test_frame)
        assert result.output.shape == test_frame.shape

    def test_morphology_invalid_operation(self, test_frame):
        stage = MorphologyStage(operation='invalid')
        result = stage.process(test_frame)
        # Should default to opening
        assert result.output.shape == test_frame.shape

    def test_roi_extraction(self, test_frame):
        stage = ROIStage(x=100, y=100, width=200, height=200)
        result = stage.process(test_frame)
        assert result.output.shape == (200, 200, 3)

    def test_roi_full_frame(self, test_frame):
        stage = ROIStage()
        result = stage.process(test_frame)
        assert result.output.shape == test_frame.shape

    def test_sobel(self, test_frame):
        stage = SobelStage(dx=1, dy=0)
        result = stage.process(test_frame)
        assert result.output.shape == (480, 640)

    def test_sharpening(self, test_frame):
        stage = SharpeningStage(strength=1.0)
        result = stage.process(test_frame)
        assert result.output.shape == test_frame.shape

    def test_stage_enabled(self, test_frame):
        stage = GrayscaleStage()
        stage.set_enabled(False)
        assert not stage.is_enabled()
        stage.set_enabled(True)
        assert stage.is_enabled()

    def test_stage_params(self, test_frame):
        stage = GaussianBlurStage()
        stage.set_param('kernel_size', 7)
        assert stage.params['kernel_size'] == 7
        stage.set_params({'kernel_size': 9, 'sigma': 1.0})
        assert stage.params['kernel_size'] == 9

    def test_empty_frame(self):
        stage = GrayscaleStage()
        empty = np.zeros((0, 0, 3), dtype=np.uint8)
        result = stage.process(empty)
        assert result.output.shape[0] == 0

    def test_single_pixel(self):
        stage = GrayscaleStage()
        single = np.array([[[128, 64, 32]]], dtype=np.uint8)
        result = stage.process(single)
        assert result.output.shape == (1, 1)


class TestVisionEngine:
    """Test the complete vision engine."""

    def test_engine_creation(self):
        engine = VisionEngine(ExecutionSource.HOST)
        assert len(engine._stages) == 0

    def test_add_remove_stage(self, test_frame):
        engine = VisionEngine()
        stage = GrayscaleStage()
        engine.add_stage(stage)
        assert len(engine._stages) == 1
        engine.remove_stage(0)
        assert len(engine._stages) == 0

    def test_process_single_stage(self, test_frame):
        engine = VisionEngine()
        engine.add_stage(GrayscaleStage())
        result = engine.process(test_frame)
        assert result['output'].shape == (480, 640)
        assert result['stage_count'] == 1
        assert result['total_time_ms'] >= 0

    def test_process_pipeline(self, test_frame):
        engine = VisionEngine()
        engine.add_stage(GaussianBlurStage())
        engine.add_stage(GrayscaleStage())
        engine.add_stage(CannyStage())
        result = engine.process(test_frame)
        assert result['stage_count'] == 3
        assert result['output'].shape == (480, 640)

    def test_disabled_stage_skipped(self, test_frame):
        engine = VisionEngine()
        s1 = GrayscaleStage()
        s2 = CannyStage()
        s2.set_enabled(False)
        engine.add_stage(s1)
        engine.add_stage(s2)
        result = engine.process(test_frame)
        assert result['stage_count'] == 1

    def test_create_stage(self):
        engine = VisionEngine()
        stage = engine.create_stage('grayscale')
        assert stage is not None
        assert isinstance(stage, GrayscaleStage)

    def test_create_invalid_stage(self):
        engine = VisionEngine()
        stage = engine.create_stage('nonexistent')
        assert stage is None

    def test_save_load_config(self, test_frame):
        engine = VisionEngine()
        engine.add_stage(GaussianBlurStage(kernel_size=7))
        engine.add_stage(GrayscaleStage())

        config = engine.save_config()
        assert len(config['stages']) == 2

        new_engine = VisionEngine()
        new_engine.load_config(config)
        assert len(new_engine._stages) == 2

        result = new_engine.process(test_frame)
        assert result['stage_count'] == 2

    def test_set_stage_param(self, test_frame):
        engine = VisionEngine()
        engine.add_stage(GaussianBlurStage())
        engine.set_stage_param(0, 'kernel_size', 9)
        result = engine.process(test_frame)
        assert result['output'].shape == test_frame.shape

    def test_get_pipeline_summary(self):
        engine = VisionEngine()
        engine.add_stage(GrayscaleStage())
        engine.add_stage(CannyStage())
        summary = engine.get_pipeline_summary()
        assert len(summary) == 2
        assert summary[0]['name'] == 'grayscale'

    def test_execution_source(self):
        engine = VisionEngine(ExecutionSource.FPGA)
        assert engine.execution_source == ExecutionSource.FPGA


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
