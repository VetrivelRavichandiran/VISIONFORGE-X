"""VISIONFORGE X - Embedded Communication Service (ARM side).
This module implements the device-side protocol handler that would run
on the ZYBO Z7-10 ARM processor. It handles TCP commands, telemetry,
and frame transport.
"""
import socket
import struct
import json
import time
import threading
import logging
from typing import Dict, Any, Optional, Callable, List

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = "1.0"
FRAME_MAGIC = b'VFFR'


class EmbeddedDeviceService:
    """Device-side service running on ZYBO ARM processor.
    
    Handles:
    - TCP command reception and response
    - Telemetry generation and transmission
    - Frame transport via UDP
    - Heartbeat management
    """

    def __init__(self, config: Dict[str, Any]):
        self.tcp_port = config.get('tcp_port', 5000)
        self.udp_port = config.get('udp_port', 5001)
        self.device_name = config.get('device_name', 'ZYBO-Z7-10')
        self.firmware_version = config.get('firmware_version', '1.0.0')
        self.bitstream_version = config.get('bitstream_version', '1.0.0')
        self.heartbeat_interval = config.get('heartbeat_interval', 2.0)

        self._tcp_server = None
        self._udp_socket = None
        self._client_socket = None
        self._running = False
        self._seq = 0
        self._frame_seq = 0
        self._connected = False
        self._camera_running = False
        self._processing_active = False

        # Callbacks for hardware integration
        self._on_command: Optional[Callable] = None
        self._frame_source: Optional[Callable] = None

        # Telemetry state
        self._telemetry_state = {
            'camera': {'connected': False, 'width': 640, 'height': 480, 'fps': 30},
            'performance': {'processing_fps': 0, 'latency_ms': 0, 'dropped_frames': 0},
            'hardware': {'pipeline_active': False, 'dma_status': 'idle'},
            'arm': {'cpu_usage': 0, 'memory_usage': 0, 'uptime': 0},
        }

    def set_command_handler(self, handler: Callable):
        """Set command handler callback."""
        self._on_command = handler

    def set_frame_source(self, source: Callable):
        """Set frame source callback (returns numpy frame or None)."""
        self._frame_source = source

    def start(self):
        """Start the device service."""
        self._running = True
        self._start_tcp_server()
        self._start_udp_socket()
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        logger.info(f"Embedded service started on port {self.tcp_port}")

    def stop(self):
        """Stop the device service."""
        self._running = False
        self._camera_running = False
        self._processing_active = False
        if self._tcp_server:
            self._tcp_server.close()
        if self._udp_socket:
            self._udp_socket.close()
        if self._client_socket:
            self._client_socket.close()
        logger.info("Embedded service stopped")

    def _start_tcp_server(self):
        """Start TCP command server."""
        self._tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._tcp_server.bind(('0.0.0.0', self.tcp_port))
        self._tcp_server.listen(1)
        self._tcp_server.settimeout(1.0)
        threading.Thread(target=self._tcp_accept_loop, daemon=True).start()

    def _start_udp_socket(self):
        """Start UDP frame sender."""
        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def _tcp_accept_loop(self):
        """Accept TCP client connections."""
        while self._running:
            try:
                client, addr = self._tcp_server.accept()
                client.settimeout(5.0)
                self._client_socket = client
                self._connected = True
                logger.info(f"Client connected: {addr}")
                self._handle_client(client)
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    logger.error(f"TCP accept error: {e}")
                break

    def _handle_client(self, client: socket.socket):
        """Handle a connected client."""
        try:
            while self._running:
                data = client.recv(4096)
                if not data:
                    break
                msg = self._parse_message(data)
                if msg:
                    self._handle_message(msg, client)
        except (socket.error, ConnectionResetError):
            pass
        finally:
            client.close()
            self._client_socket = None
            self._connected = False
            logger.info("Client disconnected")

    def _parse_message(self, data: bytes) -> Optional[Dict]:
        """Parse incoming JSON message."""
        try:
            return json.loads(data.decode('utf-8').strip())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _build_message(self, msg_type: str, payload: Dict = None,
                       sequence: int = 0) -> bytes:
        """Build a JSON message."""
        msg = {
            'protocol_version': PROTOCOL_VERSION,
            'type': msg_type,
            'sequence': sequence,
            'timestamp_us': int(time.time() * 1_000_000),
        }
        if payload:
            msg.update(payload)
        return json.dumps(msg).encode('utf-8')

    def _handle_message(self, msg: Dict, client: socket.socket):
        """Handle incoming message."""
        msg_type = msg.get('type', '')

        if msg_type == 'handshake':
            self._handle_handshake(msg, client)
        elif msg_type == 'command':
            self._handle_command(msg, client)
        elif msg_type == 'heartbeat':
            client.sendall(self._build_message('heartbeat', {'active': True}))
        elif msg_type == 'request_telemetry':
            self._send_telemetry(client)

    def _handle_handshake(self, msg: Dict, client: socket.socket):
        """Handle handshake."""
        ack = {
            'device_id': 'ZYBO-001',
            'device_name': self.device_name,
            'firmware_version': self.firmware_version,
            'bitstream_version': self.bitstream_version,
            'accepted': True,
        }
        client.sendall(self._build_message('handshake_ack', ack))

    def _handle_command(self, msg: Dict, client: socket.socket):
        """Handle command."""
        cmd = msg.get('command_type', '')
        params = msg.get('parameters', {})
        cmd_id = msg.get('command_id', '')

        accepted = True
        error_msg = ""
        applied = {}

        if cmd == 'start_camera':
            self._camera_running = True
            self._telemetry_state['camera']['connected'] = True
        elif cmd == 'stop_camera':
            self._camera_running = False
            self._telemetry_state['camera']['connected'] = False
        elif cmd == 'start_processing':
            self._processing_active = True
            self._telemetry_state['hardware']['pipeline_active'] = True
        elif cmd == 'stop_processing':
            self._processing_active = False
            self._telemetry_state['hardware']['pipeline_active'] = False
        elif cmd == 'set_processing_mode':
            applied['processing_mode'] = params.get('mode', 'balanced')
        elif cmd == 'set_pipeline':
            applied['pipeline'] = params.get('pipeline', {})
        elif cmd == 'select_model':
            applied['model'] = params.get('model', '')
        elif cmd == 'set_inference_interval':
            applied['inference_interval'] = params.get('interval', 1)
        elif cmd == 'start_benchmark':
            applied['benchmark'] = 'started'
        elif cmd == 'stop_benchmark':
            applied['benchmark'] = 'stopped'
        else:
            accepted = False
            error_msg = f"Unknown command: {cmd}"

        # Execute callback if set
        if self._on_command:
            try:
                result = self._on_command(cmd, params)
                if result is False:
                    accepted = False
                    error_msg = "Command handler rejected"
            except Exception as e:
                accepted = False
                error_msg = str(e)

        # Send acknowledgement
        ack = {
            'command_id': cmd_id,
            'accepted': accepted,
            'applied_config': applied,
            'error_code': 0 if accepted else 1,
            'error_message': error_msg,
        }
        client.sendall(self._build_message('command_ack', ack))

    def _send_telemetry(self, client: socket.socket):
        """Send telemetry data."""
        telemetry = {
            'device': {
                'name': self.device_name,
                'connection_mode': 'hardware',
                'firmware_version': self.firmware_version,
                'bitstream_version': self.bitstream_version,
            },
            'camera': self._telemetry_state['camera'],
            'performance': self._telemetry_state['performance'],
            'hardware': self._telemetry_state['hardware'],
            'arm': self._telemetry_state['arm'],
        }
        client.sendall(self._build_message('telemetry', telemetry))

    def _heartbeat_loop(self):
        """Send periodic heartbeat."""
        while self._running:
            time.sleep(self.heartbeat_interval)
            if self._client_socket and self._connected:
                try:
                    self._client_socket.sendall(
                        self._build_message('heartbeat', {'active': True})
                    )
                except Exception:
                    self._connected = False

    def send_frame(self, frame_data: bytes, width: int, height: int, fmt: int = 1):
        """Send a frame via UDP."""
        if not self._udp_socket:
            return
        self._frame_seq = (self._frame_seq + 1) % 65536
        header = FRAME_MAGIC + struct.pack(
            '>IIHHI',
            self._frame_seq,
            int(time.time() * 1_000_000),
            width, height, fmt, len(frame_data)
        )
        self._udp_socket.sendto(header + frame_data, ('255.255.255.255', self.udp_port))

    def get_status(self) -> Dict[str, Any]:
        """Get current device status."""
        return {
            'connected': self._connected,
            'camera_running': self._camera_running,
            'processing_active': self._processing_active,
            'telemetry': self._telemetry_state,
        }
