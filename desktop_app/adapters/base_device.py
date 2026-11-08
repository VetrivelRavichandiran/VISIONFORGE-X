"""VISIONFORGE X - Abstract device interface and implementations."""
import abc
import threading
import time
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class DeviceStatus:
    """Current device status."""
    connected: bool = False
    mode: str = "simulation"
    device_name: str = ""
    firmware_version: str = ""
    bitstream_version: str = ""
    camera_connected: bool = False
    camera_width: int = 0
    camera_height: int = 0
    camera_fps: int = 0
    processing_active: bool = False
    processing_mode: str = "balanced"
    active_pipeline: str = ""
    current_model: str = ""
    inference_interval: int = 1
    is_simulated: bool = True
    last_telemetry: Dict[str, Any] = field(default_factory=dict)


class BaseDevice(abc.ABC):
    """Abstract base class for all device implementations."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._state = ConnectionState.DISCONNECTED
        self._status = DeviceStatus(mode=self.config.get('mode', 'simulation'),
                                     is_simulated=self.config.get('mode', 'simulation') == 'simulation')
        self._callbacks: Dict[str, List[Callable]] = {
            'telemetry': [], 'event': [], 'state_change': [], 'frame': []
        }
        self._lock = threading.Lock()
        self._running = False

    @property
    def state(self) -> ConnectionState:
        return self._state

    @property
    def status(self) -> DeviceStatus:
        return self._status

    def is_connected(self) -> bool:
        return self._state == ConnectionState.CONNECTED

    def on(self, event: str, callback: Callable):
        """Register event callback."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def off(self, event: str, callback: Callable):
        """Unregister event callback."""
        if event in self._callbacks:
            self._callbacks[event] = [c for c in self._callbacks[event] if c != callback]

    def _emit(self, event: str, data: Any):
        """Emit event to all registered callbacks."""
        for cb in self._callbacks.get(event, []):
            try:
                cb(data)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")

    def _set_state(self, new_state: ConnectionState):
        """Update connection state and notify."""
        old = self._state
        self._state = new_state
        self._status.connected = (new_state == ConnectionState.CONNECTED)
        self._emit('state_change', {'old': old, 'new': new_state})
        logger.info(f"Device state: {old.value} -> {new_state.value}")

    @abc.abstractmethod
    def connect(self) -> bool:
        """Connect to the device."""
        pass

    @abc.abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the device."""
        pass

    @abc.abstractmethod
    def get_status(self) -> DeviceStatus:
        """Get current device status."""
        pass

    @abc.abstractmethod
    def start_camera(self) -> bool:
        """Start camera capture."""
        pass

    @abc.abstractmethod
    def stop_camera(self) -> bool:
        """Stop camera capture."""
        pass

    @abc.abstractmethod
    def start_processing(self) -> bool:
        """Start image processing pipeline."""
        pass

    @abc.abstractmethod
    def stop_processing(self) -> bool:
        """Stop image processing pipeline."""
        pass

    @abc.abstractmethod
    def set_processing_mode(self, mode: str) -> bool:
        """Set processing mode (quality/balanced/performance)."""
        pass

    @abc.abstractmethod
    def set_pipeline(self, pipeline_config: Dict) -> bool:
        """Set processing pipeline configuration."""
        pass

    @abc.abstractmethod
    def set_parameter(self, stage: str, param: str, value: Any) -> bool:
        """Set a parameter for a processing stage."""
        pass

    @abc.abstractmethod
    def select_model(self, model_name: str) -> bool:
        """Select AI model for inference."""
        pass

    @abc.abstractmethod
    def set_inference_interval(self, interval: int) -> bool:
        """Set AI inference interval (frames)."""
        pass

    @abc.abstractmethod
    def request_telemetry(self) -> bool:
        """Request current telemetry data."""
        pass

    @abc.abstractmethod
    def start_recording(self, path: str = "") -> bool:
        """Start recording video."""
        pass

    @abc.abstractmethod
    def stop_recording(self) -> bool:
        """Stop recording video."""
        pass

    @abc.abstractmethod
    def start_benchmark(self, config: Dict = None) -> bool:
        """Start performance benchmark."""
        pass

    @abc.abstractmethod
    def stop_benchmark(self) -> bool:
        """Stop performance benchmark."""
        pass

    def shutdown(self):
        """Clean shutdown."""
        self._running = False
        self.disconnect()


class SimulationDevice(BaseDevice):
    """Simulation device that generates synthetic data without hardware."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self._camera_running = False
        self._processing_running = False
        self._recording = False
        self._benchmark_running = False
        self._frame_seq = 0
        self._telemetry_thread: Optional[threading.Thread] = None
        self._simulated_fps = self.config.get('simulated_fps', 30)
        self._simulated_latency = self.config.get('simulated_latency_ms', 15.0)
        self._noise_level = self.config.get('noise_level', 0.02)

    def connect(self) -> bool:
        with self._lock:
            self._set_state(ConnectionState.CONNECTING)
            self._status.device_name = "ZYBO-Z7-10 (SIMULATED)"
            self._status.firmware_version = "1.0.0-SIM"
            self._status.bitstream_version = "1.0.0-SIM"
            self._status.camera_width = 640
            self._status.camera_height = 480
            self._status.camera_fps = self._simulated_fps
            self._status.is_simulated = True
            self._running = True
            self._set_state(ConnectionState.CONNECTED)
            self._emit('event', {
                'category': 'device', 'severity': 'info',
                'description': 'Simulation device connected',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            return True

    def disconnect(self) -> bool:
        with self._lock:
            self.stop_camera()
            self.stop_processing()
            self._running = False
            self._set_state(ConnectionState.DISCONNECTED)
            self._emit('event', {
                'category': 'device', 'severity': 'info',
                'description': 'Simulation device disconnected',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            return True

    def get_status(self) -> DeviceStatus:
        return self._status

    def start_camera(self) -> bool:
        if not self.is_connected():
            return False
        self._camera_running = True
        self._status.camera_connected = True
        self._emit('event', {
            'category': 'camera', 'severity': 'info',
            'description': 'Camera started (SIMULATED)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return True

    def stop_camera(self) -> bool:
        self._camera_running = False
        self._status.camera_connected = False
        self._emit('event', {
            'category': 'camera', 'severity': 'info',
            'description': 'Camera stopped',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return True

    def start_processing(self) -> bool:
        if not self.is_connected():
            return False
        self._processing_running = True
        self._status.processing_active = True
        self._emit('event', {
            'category': 'processing', 'severity': 'info',
            'description': 'Processing started (SIMULATED)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return True

    def stop_processing(self) -> bool:
        self._processing_running = False
        self._status.processing_active = False
        return True

    def set_processing_mode(self, mode: str) -> bool:
        if not self.is_connected():
            return False
        valid = ['quality', 'balanced', 'performance']
        if mode not in valid:
            return False
        self._status.processing_mode = mode
        self._emit('event', {
            'category': 'processing', 'severity': 'info',
            'description': f'Processing mode set to {mode} (SIMULATED)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return True

    def set_pipeline(self, pipeline_config: Dict) -> bool:
        self._status.active_pipeline = pipeline_config.get('name', 'unnamed')
        self._emit('event', {
            'category': 'pipeline', 'severity': 'info',
            'description': f'Pipeline applied: {self._status.active_pipeline} (SIMULATED)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return True

    def set_parameter(self, stage: str, param: str, value: Any) -> bool:
        return True

    def select_model(self, model_name: str) -> bool:
        self._status.current_model = model_name
        self._emit('event', {
            'category': 'ai', 'severity': 'info',
            'description': f'Model selected: {model_name} (SIMULATED)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return True

    def set_inference_interval(self, interval: int) -> bool:
        if interval < 1:
            return False
        self._status.inference_interval = interval
        return True

    def request_telemetry(self) -> bool:
        self._generate_telemetry()
        return True

    def start_recording(self, path: str = "") -> bool:
        self._recording = True
        return True

    def stop_recording(self) -> bool:
        self._recording = False
        return True

    def start_benchmark(self, config: Dict = None) -> bool:
        self._benchmark_running = True
        self._emit('event', {
            'category': 'benchmark', 'severity': 'info',
            'description': 'Benchmark started (SIMULATED)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return True

    def stop_benchmark(self) -> bool:
        self._benchmark_running = False
        self._emit('event', {
            'category': 'benchmark', 'severity': 'info',
            'description': 'Benchmark completed (SIMULATED)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return True

    def _generate_telemetry(self):
        """Generate simulated telemetry data."""
        import random
        import numpy as np

        base_fps = self._simulated_fps * (0.9 + 0.2 * random.random())
        latency = self._simulated_latency * (0.8 + 0.4 * random.random())
        cpu = 25 + 40 * random.random()
        memory = 30 + 35 * random.random()
        motion = max(0, min(1, random.gauss(0.3, 0.2)))
        anomaly = max(0, min(1, random.gauss(0.1, 0.1)))
        inference = 30 + 15 * random.random()

        telemetry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'device_name': self._status.device_name,
            'processing_fps': round(base_fps, 1),
            'latency_ms': round(latency, 1),
            'dropped_frames': random.randint(0, 2),
            'cpu_usage': round(cpu, 1),
            'memory_usage': round(memory, 1),
            'motion_intensity': round(motion, 3),
            'anomaly_score': round(anomaly, 3),
            'ai_inference_ms': round(inference, 1),
            'pipeline_active': self._status.processing_active,
            'dma_status': 'running' if self._status.processing_active else 'idle',
        }
        self._status.last_telemetry = telemetry
        self._emit('telemetry', telemetry)

    def generate_frame(self, width: int = 640, height: int = 480):
        """Generate a simulated frame with patterns."""
        import numpy as np
        self._frame_seq += 1
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Create moving gradient pattern
        t = time.time()
        for c in range(3):
            frame[:, :, c] = np.tile(
                np.linspace(30 + c * 60, 180 + c * 30, width),
                (height, 1)
            )

        # Add moving circle
        cx = int(width * 0.5 + 100 * np.sin(t * 1.5))
        cy = int(height * 0.5 + 50 * np.cos(t * 2.0))
        cv2_available = False
        try:
            import cv2
            cv2_available = True
            cv2.circle(frame, (cx, cy), 40, (0, 255, 255), -1)
            cv2.circle(frame, (cx, cy), 45, (0, 0, 0), 2)
        except ImportError:
            pass

        # Add noise
        noise = np.random.normal(0, self._noise_level * 255, frame.shape)
        frame = np.clip(frame + noise, 0, 255).astype(np.uint8)

        return frame, self._frame_seq


class ZyboHardwareDevice(BaseDevice):
    """Hardware device adapter for ZYBO Z7-10 board.
    
    This adapter implements the communication protocol for real hardware.
    Actual hardware communication requires the physical board connected
    via Ethernet. In the absence of hardware, this adapter will report
    connection failures clearly.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.board_ip = self.config.get('board_ip', '192.168.1.100')
        self.tcp_port = self.config.get('tcp_port', 5000)
        self.udp_port = self.config.get('udp_port', 5001)
        self.timeout = self.config.get('comm_timeout', 5.0)
        self._tcp_socket = None
        self._udp_socket = None
        self._recv_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._seq = 0
        self._frame_buffer = None

    def connect(self) -> bool:
        self._set_state(ConnectionState.CONNECTING)
        self._emit('event', {
            'category': 'device', 'severity': 'info',
            'description': f'Connecting to ZYBO at {self.board_ip}:{self.tcp_port}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

        try:
            import socket
            self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcp_socket.settimeout(self.timeout)
            self._tcp_socket.connect((self.board_ip, self.tcp_port))

            # Send handshake
            from protocol.messages import HandshakeMessage, MessageParser
            handshake = HandshakeMessage(
                client_id="VISIONFORGE-X-DESKTOP",
                capabilities=["camera", "processing", "ai", "telemetry", "benchmark"]
            )
            self._tcp_socket.sendall(MessageParser.build_control(handshake))

            # Wait for ack
            data = self._tcp_socket.recv(4096)
            ack = MessageParser.parse_message(data)
            if ack and ack.type == 'handshake_ack' and ack.accepted:
                self._status.device_name = ack.device_name or "ZYBO-Z7-10"
                self._status.firmware_version = ack.firmware_version
                self._status.bitstream_version = ack.bitstream_version
                self._status.is_simulated = False
                self._set_state(ConnectionState.CONNECTED)
                self._start_receivers()
                self._emit('event', {
                    'category': 'device', 'severity': 'info',
                    'description': f'Connected to {self._status.device_name}',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                return True
            else:
                self._set_state(ConnectionState.ERROR)
                return False

        except (socket.timeout, socket.error, ConnectionRefusedError) as e:
            self._set_state(ConnectionState.ERROR)
            self._emit('event', {
                'category': 'device', 'severity': 'error',
                'description': f'Hardware connection failed: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            return False

    def disconnect(self) -> bool:
        self._running = False
        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except Exception:
                pass
            self._tcp_socket = None
        if self._udp_socket:
            try:
                self._udp_socket.close()
            except Exception:
                pass
            self._udp_socket = None
        self._set_state(ConnectionState.DISCONNECTED)
        return True

    def _start_receivers(self):
        """Start background receiver threads."""
        self._running = True
        self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._recv_thread.start()

    def _receive_loop(self):
        """Main receive loop for TCP messages."""
        import select
        while self._running and self._tcp_socket:
            try:
                ready, _, _ = select.select([self._tcp_socket], [], [], 1.0)
                if ready:
                    data = self._tcp_socket.recv(4096)
                    if not data:
                        break
                    from protocol.messages import MessageParser
                    msg = MessageParser.parse_message(data)
                    if msg:
                        self._handle_message(msg)
            except (socket.error, OSError):
                break

    def _handle_message(self, msg):
        """Handle incoming protocol message."""
        from protocol.messages import TelemetryMessage, EventMessage, CommandAckMessage
        if isinstance(msg, TelemetryMessage):
            self._status.last_telemetry = msg.to_dict()
            self._emit('telemetry', msg.to_dict())
        elif isinstance(msg, EventMessage):
            self._emit('event', msg.to_dict())
        elif isinstance(msg, CommandAckMessage):
            self._emit('event', {
                'category': 'command', 'severity': 'info',
                'description': f'Command {msg.command_id} ack: {"accepted" if msg.accepted else "rejected"}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

    def _send_command(self, command_type: str, params: Dict = None) -> bool:
        """Send a command to the device."""
        if not self._tcp_socket:
            return False
        from protocol.messages import CommandMessage, MessageParser
        self._seq += 1
        cmd = CommandMessage(
            sequence=self._seq,
            command_id=f"cmd_{self._seq}",
            command_type=command_type,
            parameters=params or {}
        )
        try:
            self._tcp_socket.sendall(MessageParser.build_control(cmd))
            return True
        except (socket.error, OSError):
            return False

    def get_status(self) -> DeviceStatus:
        return self._status

    def start_camera(self) -> bool:
        return self._send_command('start_camera')

    def stop_camera(self) -> bool:
        return self._send_command('stop_camera')

    def start_processing(self) -> bool:
        self._status.processing_active = True
        return self._send_command('start_processing')

    def stop_processing(self) -> bool:
        self._status.processing_active = False
        return self._send_command('stop_processing')

    def set_processing_mode(self, mode: str) -> bool:
        return self._send_command('set_processing_mode', {'mode': mode})

    def set_pipeline(self, pipeline_config: Dict) -> bool:
        return self._send_command('set_pipeline', {'pipeline': pipeline_config})

    def set_parameter(self, stage: str, param: str, value: Any) -> bool:
        return self._send_command('set_parameter', {'stage': stage, 'param': param, 'value': value})

    def select_model(self, model_name: str) -> bool:
        self._status.current_model = model_name
        return self._send_command('select_model', {'model': model_name})

    def set_inference_interval(self, interval: int) -> bool:
        return self._send_command('set_inference_interval', {'interval': interval})

    def request_telemetry(self) -> bool:
        return self._send_command('request_telemetry')

    def start_recording(self, path: str = "") -> bool:
        return self._send_command('start_recording', {'path': path})

    def stop_recording(self) -> bool:
        return self._send_command('stop_recording')

    def start_benchmark(self, config: Dict = None) -> bool:
        return self._send_command('start_benchmark', config or {})

    def stop_benchmark(self) -> bool:
        return self._send_command('stop_benchmark')


def create_device(config: Dict[str, Any]) -> BaseDevice:
    """Factory function to create appropriate device based on config."""
    mode = config.get('mode', 'simulation')
    if mode == 'simulation':
        return SimulationDevice(config)
    else:
        return ZyboHardwareDevice(config)
