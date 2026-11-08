# VISIONFORGE X - Communication Protocol

## Version: 1.0

## Transport

### TCP (Control Channel)
- Port: 5000 (configurable)
- Purpose: Handshake, commands, acknowledgements, telemetry, events, heartbeat
- Format: JSON, UTF-8 encoded

### UDP (Frame Channel)
- Port: 5001 (configurable)
- Purpose: Low-latency preview frame transport
- Format: Binary with header

## Message Structure

All control messages contain:
```json
{
  "protocol_version": "1.0",
  "type": "message_type",
  "sequence": 1001,
  "timestamp_us": 123456789000,
  "payload_fields": "..."
}
```

## Message Types

### Handshake
Sent by desktop on connection. Device responds with `handshake_ack`.

### Command
Desktop → Device. Contains `command_id`, `command_type`, `parameters`.

### Command Ack
Device → Desktop. Contains matching `command_id`, `accepted` status, `applied_config`, error info.

### Telemetry
Device → Desktop. Contains device, camera, performance, hardware, AI, FPGA, ARM status.

### Event
Device → Desktop. Contains `event_id`, `category`, `severity`, `description`.

### Heartbeat
Bidirectional. Keeps connection alive.

## Commands

| Command | Parameters | Description |
|---------|-----------|-------------|
| start_camera | resolution | Start camera capture |
| stop_camera | - | Stop camera |
| start_processing | - | Start pipeline |
| stop_processing | - | Stop pipeline |
| set_processing_mode | mode | quality/balanced/performance |
| set_pipeline | pipeline | Apply pipeline config |
| set_parameter | stage, param, value | Set stage parameter |
| select_model | model | Select AI model |
| set_inference_interval | interval | Inference frequency |
| request_telemetry | - | Request current telemetry |
| start_benchmark | config | Start benchmark |
| stop_benchmark | - | Stop benchmark |

## Frame Format

```
+----------+----------+----------+----------+----------+----------+
|  Magic   |   Seq    | Timestamp|  Width   |  Height  |  Format  |
| 4 bytes  | 4 bytes  | 4 bytes  | 2 bytes  | 2 bytes  | 2 bytes  |
+----------+----------+----------+----------+----------+----------+
| Payload Length |        Payload Data (raw frame bytes)          |
|     4 bytes    |              N bytes                           |
+----------------+------------------------------------------------+
```

Formats: 0=RGB, 1=BGR, 2=GRAY, 3=COMPRESSED

## Error Handling

Error codes: 0=None, 1=Invalid Command, 2=Invalid Parameter, 3=Hardware Error, 4=Timeout, 5=Not Connected, 6=Pipeline Error, 7=Model Error, 8=Memory Error, 9=DMA Error, 10=Protocol Version Mismatch

## Reconnection

Client attempts reconnection with configurable delay. Sequence numbers reset on new connection.
