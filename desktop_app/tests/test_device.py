"""VISIONFORGE X - Device and Simulation Tests."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
import numpy as np
from adapters.base_device import (
    SimulationDevice, ZyboHardwareDevice, create_device,
    ConnectionState, DeviceStatus
)


class TestSimulationDevice:
    """Test simulation device functionality."""

    def test_create_simulation_device(self):
        device = SimulationDevice({'mode': 'simulation'})
        assert device is not None
        assert device.status.mode == 'simulation'
        assert device.status.is_simulated is True

    def test_connect_disconnect(self):
        device = SimulationDevice()
        assert device.connect() is True
        assert device.is_connected() is True
        assert device.status.device_name == "ZYBO-Z7-10 (SIMULATED)"
        assert device.disconnect() is True
        assert device.is_connected() is False

    def test_start_stop_camera(self):
        device = SimulationDevice()
        device.connect()
        assert device.start_camera() is True
        assert device.status.camera_connected is True
        assert device.stop_camera() is True
        assert device.status.camera_connected is False

    def test_start_stop_processing(self):
        device = SimulationDevice()
        device.connect()
        device.start_camera()
        assert device.start_processing() is True
        assert device.status.processing_active is True
        assert device.stop_processing() is True
        assert device.status.processing_active is False

    def test_processing_mode(self):
        device = SimulationDevice()
        device.connect()
        assert device.set_processing_mode('quality') is True
        assert device.status.processing_mode == 'quality'
        assert device.set_processing_mode('balanced') is True
        assert device.set_processing_mode('invalid') is False

    def test_pipeline(self):
        device = SimulationDevice()
        device.connect()
        assert device.set_pipeline({'name': 'test', 'stages': []}) is True
        assert device.status.active_pipeline == 'test'

    def test_model_selection(self):
        device = SimulationDevice()
        device.connect()
        assert device.select_model('test_model') is True
        assert device.status.current_model == 'test_model'

    def test_inference_interval(self):
        device = SimulationDevice()
        device.connect()
        assert device.set_inference_interval(1) is True
        assert device.set_inference_interval(5) is True
        assert device.set_inference_interval(0) is False

    def test_telemetry(self):
        device = SimulationDevice()
        device.connect()
        device.start_camera()
        device.start_processing()
        events = []
        device.on('telemetry', lambda t: events.append(t))
        device.request_telemetry()
        assert len(events) >= 1
        assert 'processing_fps' in events[0]
        assert 'latency_ms' in events[0]

    def test_generate_frame(self):
        device = SimulationDevice()
        device.connect()
        frame, seq = device.generate_frame(640, 480)
        assert frame.shape == (480, 640, 3)
        assert frame.dtype == np.uint8
        assert seq == 1
        frame2, seq2 = device.generate_frame(640, 480)
        assert seq2 == 2

    def test_event_emission(self):
        device = SimulationDevice()
        events = []
        device.on('event', lambda e: events.append(e))
        device.connect()
        assert len(events) >= 1
        assert events[0]['category'] == 'device'

    def test_state_change_emission(self):
        device = SimulationDevice()
        states = []
        device.on('state_change', lambda s: states.append(s))
        device.connect()
        device.disconnect()
        assert len(states) >= 2

    def test_commands_require_connection(self):
        device = SimulationDevice()
        assert device.start_camera() is False
        assert device.start_processing() is False
        assert device.set_processing_mode('quality') is False

    def test_benchmark(self):
        device = SimulationDevice()
        device.connect()
        assert device.start_benchmark() is True
        assert device.stop_benchmark() is True

    def test_recording(self):
        device = SimulationDevice()
        device.connect()
        assert device.start_recording() is True
        assert device.stop_recording() is True

    def test_config_options(self):
        device = SimulationDevice({
            'simulated_fps': 20,
            'simulated_latency_ms': 25.0,
            'noise_level': 0.05
        })
        assert device._simulated_fps == 20
        assert device._simulated_latency == 25.0
        assert device._noise_level == 0.05


class TestDeviceFactory:
    """Test device factory function."""

    def test_create_simulation(self):
        device = create_device({'mode': 'simulation'})
        assert isinstance(device, SimulationDevice)

    def test_create_hardware(self):
        device = create_device({'mode': 'hardware'})
        assert isinstance(device, ZyboHardwareDevice)

    def test_default_mode(self):
        device = create_device({})
        assert isinstance(device, SimulationDevice)


class TestDeviceStatus:
    """Test DeviceStatus dataclass."""

    def test_default_status(self):
        status = DeviceStatus()
        assert status.connected is False
        assert status.mode == 'simulation'
        assert status.is_simulated is True

    def test_status_update(self):
        status = DeviceStatus()
        status.connected = True
        status.device_name = "ZYBO-001"
        assert status.connected is True
        assert status.device_name == "ZYBO-001"


class TestConnectionStates:
    """Test connection state transitions."""

    def test_state_values(self):
        assert ConnectionState.DISCONNECTED.value == "disconnected"
        assert ConnectionState.CONNECTED.value == "connected"
        assert ConnectionState.CONNECTING.value == "connecting"
        assert ConnectionState.RECONNECTING.value == "reconnecting"
        assert ConnectionState.ERROR.value == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
