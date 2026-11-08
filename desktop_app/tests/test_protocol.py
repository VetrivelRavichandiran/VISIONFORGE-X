"""VISIONFORGE X - Protocol Tests."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import json
import struct
from protocol.messages import (
    HandshakeMessage, HandshakeAckMessage, CommandMessage, CommandAckMessage,
    TelemetryMessage, EventMessage, ErrorMessage, HeartbeatMessage,
    MessageParser, FrameProtocol, PROTOCOL_VERSION
)


class TestMessageSerialization:
    """Test protocol message serialization/deserialization."""

    def test_handshake_roundtrip(self):
        msg = HandshakeMessage(
            client_id="TEST-CLIENT",
            capabilities=["camera", "processing"]
        )
        data = MessageParser.build_control(msg)
        parsed = MessageParser.parse_message(data)
        assert parsed is not None
        assert parsed.type == "handshake"
        assert parsed.client_id == "TEST-CLIENT"
        assert "camera" in parsed.capabilities

    def test_command_roundtrip(self):
        msg = CommandMessage(
            sequence=42,
            command_id="cmd_001",
            command_type="start_camera",
            parameters={"resolution": "640x480"}
        )
        data = MessageParser.build_control(msg)
        parsed = MessageParser.parse_message(data)
        assert parsed is not None
        assert parsed.type == "command"
        assert parsed.command_id == "cmd_001"
        assert parsed.parameters["resolution"] == "640x480"

    def test_telemetry_roundtrip(self):
        msg = TelemetryMessage(
            device={"name": "ZYBO-Z7-10", "firmware_version": "1.0"},
            camera={"connected": True, "width": 640, "height": 480},
            performance={"processing_fps": 25.5, "latency_ms": 12.3}
        )
        data = MessageParser.build_control(msg)
        parsed = MessageParser.parse_message(data)
        assert parsed is not None
        assert parsed.type == "telemetry"
        assert parsed.device["name"] == "ZYBO-Z7-10"
        assert parsed.camera["width"] == 640

    def test_command_ack_roundtrip(self):
        msg = CommandAckMessage(
            command_id="cmd_001",
            accepted=True,
            applied_config={"mode": "balanced"}
        )
        data = MessageParser.build_control(msg)
        parsed = MessageParser.parse_message(data)
        assert parsed is not None
        assert parsed.accepted is True
        assert parsed.applied_config["mode"] == "balanced"

    def test_event_message(self):
        msg = EventMessage(
            event_id="evt_001",
            category="motion",
            severity="info",
            description="Motion detected"
        )
        data = MessageParser.build_control(msg)
        parsed = MessageParser.parse_message(data)
        assert parsed.type == "event"
        assert parsed.category == "motion"

    def test_error_message(self):
        msg = ErrorMessage(
            error_code=1,
            error_message="Invalid command"
        )
        data = MessageParser.build_control(msg)
        parsed = MessageParser.parse_message(data)
        assert parsed.type == "error"
        assert parsed.error_code == 1

    def test_heartbeat_message(self):
        msg = HeartbeatMessage(active=True)
        data = MessageParser.build_control(msg)
        parsed = MessageParser.parse_message(data)
        assert parsed.type == "heartbeat"
        assert parsed.active is True

    def test_invalid_json(self):
        result = MessageParser.parse_control(b"not valid json{{{")
        assert result is None

    def test_empty_message(self):
        msg = MessageParser.parse_control(b"")
        assert msg is None

    def test_protocol_version(self):
        msg = HandshakeMessage()
        assert msg.protocol_version == PROTOCOL_VERSION
        assert MessageParser.validate_version(msg) is True

    def test_version_mismatch(self):
        msg = HandshakeMessage()
        msg.protocol_version = "0.9"
        assert MessageParser.validate_version(msg) is False

    def test_sequence_counter(self):
        parser = MessageParser()
        s1 = parser.next_sequence()
        s2 = parser.next_sequence()
        assert s2 == s1 + 1

    def test_sequence_wraparound(self):
        parser = MessageParser()
        parser._seq_counter = 65535
        s = parser.next_sequence()
        assert s == 0


class TestFrameProtocol:
    """Test binary frame protocol."""

    def test_build_and_parse_header(self):
        payload = b"\x00\x01\x02\x03"
        frame = FrameProtocol.build_frame(
            seq=100, timestamp_us=123456789,
            width=640, height=480, fmt=1, payload=payload
        )
        assert frame[:4] == FrameProtocol.FRAME_MAGIC
        header = FrameProtocol.parse_header(frame)
        assert header is not None
        assert header['seq'] == 100
        assert header['width'] == 640
        assert header['height'] == 480
        assert header['payload_len'] == 4

    def test_full_frame_roundtrip(self):
        payload = bytes(range(256))
        frame = FrameProtocol.build_frame(
            seq=42, timestamp_us=999, width=100, height=50,
            fmt=FrameProtocol.FORMAT_BGR, payload=payload
        )
        header = FrameProtocol.parse_header(frame)
        body = frame[FrameProtocol.HEADER_SIZE:]
        assert body == payload
        assert header['payload_len'] == 256

    def test_insufficient_header(self):
        result = FrameProtocol.parse_header(b"short")
        assert result is None

    def test_checksum(self):
        payload = b"test data"
        cs1 = FrameProtocol.frame_checksum(payload)
        cs2 = FrameProtocol.frame_checksum(payload)
        assert cs1 == cs2
        assert cs1 != FrameProtocol.frame_checksum(b"different")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
