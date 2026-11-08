# VISIONFORGE X - Architecture

## System Overview

VISIONFORGE X follows a modular three-layer architecture:

1. **Windows Workstation Layer** - Desktop GUI, model training, analytics
2. **Communication Layer** - TCP/UDP protocol, frame transport
3. **Embedded Layer** - ARM control, FPGA processing

## Layer Details

### Desktop Application Layer

The desktop application is built with PySide6 (Qt for Python) and follows the Model-View pattern:

- **Frontend**: 12 pages, each a self-contained QWidget
- **Backend Services**: Independent modules communicating via explicit interfaces
- **Device Abstraction**: Common interface for simulation and hardware devices
- **Threading**: Worker threads for frame processing, network I/O, database operations

### Communication Protocol

- **TCP (port 5000)**: Commands, acknowledgements, telemetry, events
- **UDP (port 5001)**: Low-latency preview frame transport
- **JSON**: Control and telemetry messages
- **Binary**: Frame data with header (seq, timestamp, dimensions, format, payload)

### Device Abstraction

All business logic communicates through the `BaseDevice` interface:
- `SimulationDevice` - Generates synthetic data for development/testing
- `ZyboHardwareDevice` - Communicates with physical board via protocol

### Vision Processing Engine

Modular stage-based architecture:
- Each algorithm is a `VisionStage` subclass
- Stages are chained into pipelines
- Execution source is tracked (HOST/FPGA/ARM/SIMULATION)
- Processing time measured per stage

### Database Layer

SQLite with repository pattern:
- Thread-safe connections via context managers
- Schema versioning
- Indexed timestamp queries
- Data retention management

## Threading Model

```
GUI Thread (Main)
├── FrameWorker (QThread) - Frame capture, processing, telemetry
├── Network Thread - TCP command handling
├── DB Thread - Database operations (via connection pool)
└── Timer Threads - Periodic telemetry, heartbeat
```

The GUI thread only handles presentation and user interaction. All heavy processing occurs in worker threads.

## Data Flow

```
Camera → Device → Frame Worker → Vision Engine → Motion Analyzer
                                          ↓
                                    Telemetry → DB
                                          ↓
                                    GUI Updates
```

## Security Considerations

- No arbitrary code execution in pipeline (validated node types only)
- Parameter validation on all inputs
- Bounded queues to prevent memory exhaustion
- Database uses parameterized queries (no SQL injection)
- Protocol version checking prevents incompatible connections
