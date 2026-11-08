"""VISIONFORGE X Protocol - Versioned communication protocol for device communication."""
import json
import time
import struct
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, Optional
import hashlib


class MessageType(Enum):
    """Protocol message types."""
    HANDSHAKE = "handshake"
    HANDSHAKE_ACK = "handshake_ack"
    COMMAND = "command"
    COMMAND_ACK = "command_ack"
    TELEMETRY = "telemetry"
    EVENT = "event"
    CONFIG = "config"
    CONFIG_ACK = "config_ack"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    FRAME_DATA = "frame_data"
    FRAME_ACK = "frame_ack"


class CommandType(Enum):
    """Available device commands."""
    START_CAMERA = "start_camera"
    STOP_CAMERA = "stop_camera"
    START_PROCESSING = "start_processing"
    STOP_PROCESSING = "stop_processing"
    SET_PROCESSING_MODE = "set_processing_mode"
    SET_PIPELINE = "set_pipeline"
    SET_PARAMETER = "set_parameter"
    SELECT_MODEL = "select_model"
    SET_INFERENCE_INTERVAL = "set_inference_interval"
    REQUEST_TELEMETRY = "request_telemetry"
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"
    START_BENCHMARK = "start_benchmark"
    STOP_BENCHMARK = "stop_benchmark"
    GET_STATUS = "get_status"
    REBOOT = "reboot"


class ErrorCode(Enum):
    """Error codes."""
    NONE = 0
    INVALID_COMMAND = 1
    INVALID_PARAMETER = 2
    HARDWARE_ERROR = 3
    TIMEOUT = 4
    NOT_CONNECTED = 5
    PIPELINE_ERROR = 6
    MODEL_ERROR = 7
    MEMORY_ERROR = 8
    DMA_ERROR = 9
    PROTOCOL_VERSION_MISMATCH = 10


PROTOCOL_VERSION = "1.0"


@dataclass
class BaseMessage:
    """Base protocol message."""
    protocol_version: str = PROTOCOL_VERSION
    type: str = ""
    sequence: int = 0
    timestamp_us: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseMessage':
        # Use cls fields only, ignore extra fields from subclasses
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(cls)}
        kwargs = {}
        for k, v in data.items():
            if k in field_names:
                kwargs[k] = v
        # Fill defaults for missing fields
        for f in dataclasses.fields(cls):
            if f.name not in kwargs and f.default is not dataclasses.MISSING:
                kwargs[f.name] = f.default
            elif f.name not in kwargs and f.default_factory is not dataclasses.MISSING:
                kwargs[f.name] = f.default_factory()
        return cls(**kwargs)


@dataclass
class HandshakeMessage(BaseMessage):
    """Handshake message for connection establishment."""
    type: str = "handshake"
    client_id: str = ""
    client_version: str = PROTOCOL_VERSION
    capabilities: list = field(default_factory=list)


@dataclass
class HandshakeAckMessage(BaseMessage):
    """Handshake acknowledgement."""
    type: str = "handshake_ack"
    device_id: str = ""
    device_name: str = ""
    firmware_version: str = "1.0"
    bitstream_version: str = "1.0"
    accepted: bool = True
    reason: str = ""


@dataclass
class CommandMessage(BaseMessage):
    """Command message to device."""
    type: str = "command"
    command_id: str = ""
    command_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandAckMessage(BaseMessage):
    """Command acknowledgement from device."""
    type: str = "command_ack"
    command_id: str = ""
    accepted: bool = True
    applied_config: Dict[str, Any] = field(default_factory=dict)
    error_code: int = 0
    error_message: str = ""


@dataclass
class TelemetryMessage(BaseMessage):
    """Telemetry data from device."""
    type: str = "telemetry"
    device: Dict[str, Any] = field(default_factory=dict)
    camera: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    hardware: Dict[str, Any] = field(default_factory=dict)
    ai: Dict[str, Any] = field(default_factory=dict)
    fpga: Dict[str, Any] = field(default_factory=dict)
    arm: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventMessage(BaseMessage):
    """Event notification from device."""
    type: str = "event"
    event_id: str = ""
    category: str = ""
    severity: str = "info"
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorMessage(BaseMessage):
    """Error message."""
    type: str = "error"
    error_code: int = 0
    error_message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HeartbeatMessage(BaseMessage):
    """Heartbeat message."""
    type: str = "heartbeat"
    active: bool = True


class MessageParser:
    """Parses and validates protocol messages."""

    CONTROL_HEADER = b'VF'
    CONTROL_VERSION = 1

    def __init__(self):
        self._seq_counter = 0

    def next_sequence(self) -> int:
        self._seq_counter = (self._seq_counter + 1) % 65536
        return self._seq_counter

    @staticmethod
    def parse_control(data: bytes) -> Optional[Dict[str, Any]]:
        """Parse a control (JSON) message from bytes."""
        try:
            text = data.decode('utf-8').strip()
            return json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

    @staticmethod
    def build_control(message: BaseMessage) -> bytes:
        """Build a control message bytes."""
        return message.to_json().encode('utf-8')

    @staticmethod
    def parse_message(data: bytes) -> Optional[BaseMessage]:
        """Parse any message from raw bytes."""
        parsed = MessageParser.parse_control(data)
        if parsed is None:
            return None

        msg_type = parsed.get('type', '')

        type_map = {
            'handshake': HandshakeMessage,
            'handshake_ack': HandshakeAckMessage,
            'command': CommandMessage,
            'command_ack': CommandAckMessage,
            'telemetry': TelemetryMessage,
            'event': EventMessage,
            'error': ErrorMessage,
            'heartbeat': HeartbeatMessage,
        }

        cls = type_map.get(msg_type, BaseMessage)
        try:
            return cls.from_dict(parsed)
        except Exception:
            return None

    @staticmethod
    def validate_version(message: BaseMessage) -> bool:
        """Validate protocol version compatibility."""
        return message.protocol_version == PROTOCOL_VERSION


class FrameProtocol:
    """Protocol for binary frame data transfer."""

    HEADER_FORMAT = '>IIHHII'  # seq, timestamp_us, width, height, format, payload_len
    HEADER_DATA_SIZE = struct.calcsize(HEADER_FORMAT)
    FRAME_MAGIC = b'VFFR'
    FRAME_MAGIC_LEN = len(FRAME_MAGIC)
    HEADER_SIZE = FRAME_MAGIC_LEN + HEADER_DATA_SIZE  # Total header including magic

    # Frame formats
    FORMAT_RGB = 0
    FORMAT_BGR = 1
    FORMAT_GRAY = 2
    FORMAT_COMPRESSED = 3

    @staticmethod
    def build_header(seq: int, timestamp_us: int, width: int, height: int,
                     fmt: int, payload_len: int) -> bytes:
        return FrameProtocol.FRAME_MAGIC + struct.pack(
            FrameProtocol.HEADER_FORMAT, seq, timestamp_us, width, height, fmt, payload_len
        )

    @staticmethod
    def parse_header(data: bytes) -> Optional[Dict[str, Any]]:
        if len(data) < FrameProtocol.HEADER_SIZE:
            return None
        try:
            # Skip magic bytes (4) and parse the rest
            seq, ts, w, h, fmt, plen = struct.unpack(
                FrameProtocol.HEADER_FORMAT,
                data[FrameProtocol.FRAME_MAGIC_LEN:FrameProtocol.HEADER_SIZE]
            )
            return {
                'seq': seq, 'timestamp_us': ts, 'width': w, 'height': h,
                'format': fmt, 'payload_len': plen
            }
        except struct.error:
            return None

    @staticmethod
    def build_frame(seq: int, timestamp_us: int, width: int, height: int,
                    fmt: int, payload: bytes) -> bytes:
        header = FrameProtocol.build_header(seq, timestamp_us, width, height, fmt, len(payload))
        return header + payload

    @staticmethod
    def frame_checksum(payload: bytes) -> str:
        return hashlib.md5(payload).hexdigest()
