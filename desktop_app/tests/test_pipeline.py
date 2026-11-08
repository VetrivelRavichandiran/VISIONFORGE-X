"""VISIONFORGE X - Pipeline Engine Tests."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import cv2
from backend.pipeline.engine import (
    PipelineEngine, PipelineNode, PipelineConnection,
    PipelineValidator, NodeType
)


@pytest.fixture
def test_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


class TestPipelineNode:
    """Test pipeline node creation and configuration."""

    def test_create_node(self):
        node = PipelineNode(id="n1", node_type="grayscale")
        assert node.id == "n1"
        assert node.node_type == "grayscale"
        assert node.enabled is True

    def test_node_config(self):
        node = PipelineNode(id="n1", node_type="canny",
                           config={"threshold1": 100, "threshold2": 200})
        assert node.config["threshold1"] == 100

    def test_node_to_dict(self):
        node = PipelineNode(id="n1", node_type="grayscale", enabled=False)
        d = node.to_dict()
        assert d['id'] == 'n1'
        assert d['enabled'] is False


class TestPipelineValidator:
    """Test pipeline validation."""

    def test_valid_pipeline(self):
        nodes = [
            PipelineNode(id="cam", node_type="camera_input"),
            PipelineNode(id="gray", node_type="grayscale"),
            PipelineNode(id="out", node_type="output"),
        ]
        conns = [
            PipelineConnection("cam", "gray"),
            PipelineConnection("gray", "out"),
        ]
        is_valid, errors = PipelineValidator.validate(nodes, conns)
        assert is_valid is True
        assert len(errors) == 0

    def test_empty_pipeline(self):
        is_valid, errors = PipelineValidator.validate([], [])
        assert is_valid is False
        assert any("at least one node" in e for e in errors)

    def test_invalid_node_type(self):
        nodes = [
            PipelineNode(id="n1", node_type="invalid_type"),
        ]
        is_valid, errors = PipelineValidator.validate(nodes, [])
        assert is_valid is False
        assert any("Invalid node type" in e for e in errors)

    def test_invalid_connection(self):
        nodes = [PipelineNode(id="n1", node_type="camera_input")]
        conns = [PipelineConnection("n1", "nonexistent")]
        is_valid, errors = PipelineValidator.validate(nodes, conns)
        assert is_valid is False
        assert any("target not found" in e for e in errors)

    def test_cycle_detection(self):
        nodes = [
            PipelineNode(id="a", node_type="camera_input"),
            PipelineNode(id="b", node_type="grayscale"),
        ]
        conns = [
            PipelineConnection("a", "b"),
            PipelineConnection("b", "a"),  # Cycle
        ]
        is_valid, errors = PipelineValidator.validate(nodes, conns)
        assert is_valid is False
        assert any("cycle" in e for e in errors)

    def test_duplicate_ids(self):
        nodes = [
            PipelineNode(id="n1", node_type="camera_input"),
            PipelineNode(id="n1", node_type="grayscale"),
        ]
        is_valid, errors = PipelineValidator.validate(nodes, [])
        assert is_valid is False
        assert any("Duplicate" in e for e in errors)


class TestPipelineEngine:
    """Test pipeline execution engine."""

    def test_create_engine(self):
        engine = PipelineEngine()
        assert len(engine._nodes) == 0

    def test_add_remove_node(self):
        engine = PipelineEngine()
        node = PipelineNode(id="n1", node_type="grayscale")
        engine.add_node(node)
        assert len(engine._nodes) == 1
        engine.remove_node("n1")
        assert len(engine._nodes) == 0

    def test_connect_disconnect(self):
        engine = PipelineEngine()
        engine.add_node(PipelineNode(id="a", node_type="camera_input"))
        engine.add_node(PipelineNode(id="b", node_type="grayscale"))
        engine.connect("a", "b")
        assert len(engine._connections) == 1
        engine.disconnect("a", "b")
        assert len(engine._connections) == 0

    def test_process_empty_pipeline(self, test_frame):
        engine = PipelineEngine()
        result = engine.process_frame(test_frame)
        assert result['output'].shape == test_frame.shape
        assert result['total_time_ms'] == 0

    def test_process_grayscale_pipeline(self, test_frame):
        engine = PipelineEngine()
        engine.add_node(PipelineNode(id="cam", node_type="camera_input"))
        engine.add_node(PipelineNode(id="gray", node_type="grayscale"))
        engine.connect("cam", "gray")
        result = engine.process_frame(test_frame)
        # Grayscale converts to 2D
        assert result['output'].shape[:2] == (480, 640)
        assert result['node_count'] == 1

    def test_process_multi_stage(self, test_frame):
        engine = PipelineEngine()
        engine.add_node(PipelineNode(id="cam", node_type="camera_input"))
        engine.add_node(PipelineNode(id="gray", node_type="grayscale"))
        engine.add_node(PipelineNode(id="blur", node_type="gaussian_blur",
                                     config={"kernel_size": 5}))
        engine.add_node(PipelineNode(id="out", node_type="output"))
        engine.connect("cam", "gray")
        engine.connect("gray", "blur")
        engine.connect("blur", "out")
        result = engine.process_frame(test_frame)
        assert result['node_count'] == 2

    def test_invalid_pipeline_does_not_crash(self, test_frame):
        engine = PipelineEngine()
        engine.add_node(PipelineNode(id="n1", node_type="invalid_type"))
        result = engine.process_frame(test_frame)
        assert 'errors' in result

    def test_set_node_param(self, test_frame):
        engine = PipelineEngine()
        engine.add_node(PipelineNode(id="blur", node_type="gaussian_blur",
                                     config={"kernel_size": 5}))
        engine.set_node_param("blur", "kernel_size", 9)
        node = engine._nodes["blur"]
        assert node.config["kernel_size"] == 9

    def test_set_node_enabled(self, test_frame):
        engine = PipelineEngine()
        engine.add_node(PipelineNode(id="gray", node_type="grayscale"))
        engine.set_node_enabled("gray", False)
        result = engine.process_frame(test_frame)
        assert result['node_count'] == 0

    def test_get_topology(self):
        engine = PipelineEngine()
        engine.add_node(PipelineNode(id="a", node_type="camera_input"))
        engine.add_node(PipelineNode(id="b", node_type="grayscale"))
        engine.add_node(PipelineNode(id="c", node_type="output"))
        engine.connect("a", "b")
        engine.connect("b", "c")
        topology = engine.get_topology()
        assert len(topology) >= 1

    def test_save_load_config(self, test_frame):
        engine = PipelineEngine()
        engine.add_node(PipelineNode(id="cam", node_type="camera_input"))
        engine.add_node(PipelineNode(id="gray", node_type="grayscale",
                                     config={"test": 123}))
        engine.connect("cam", "gray")

        config = engine.get_config()
        assert len(config['nodes']) == 2
        assert len(config['connections']) == 1

        new_engine = PipelineEngine()
        new_engine.load_config(config)
        assert len(new_engine._nodes) == 2
        assert new_engine._nodes['gray'].config['test'] == 123

    def test_templates(self):
        templates = PipelineEngine.get_templates()
        assert len(templates) >= 3
        names = [t.name for t in templates]
        assert "Basic Enhancement" in names
        assert "Motion Detection" in names
        assert "AI Analysis" in names

    def test_validate_method(self, test_frame):
        engine = PipelineEngine()
        is_valid, errors = engine.validate()
        assert is_valid is False  # Empty pipeline

        engine.add_node(PipelineNode(id="cam", node_type="camera_input"))
        is_valid, errors = engine.validate()
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
