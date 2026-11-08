<<<<<<< HEAD
# VISIONFORGE X
## Universal Adaptive Edge Vision Intelligence Platform

![Platform Banner](VISIONFORGE%20X_%20Futuristic%20Automation%20Suite.png)

---

## Project Mission

VISIONFORGE X is a complete, production-structured software platform designed around the **Digilent ZYBO Z7-10** development board (Xilinx Zynq-7010 SoC). It combines FPGA-accelerated image processing, ARM-based embedded control, adaptive computer vision, and AI-based visual understanding into a unified desktop application.

The platform operates in two modes:
- **SIMULATION MODE**: Complete software operation without physical hardware
- **HARDWARE MODE**: Communication with a real ZYBO Z7-10 via the implemented protocol

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    WINDOWS WORKSTATION                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Desktop Application (PySide6)              │   │
│  │  ┌──────────┬──────────┬──────────┬────────────────┐  │   │
│  │  │ Command  │  Vision  │    AI    │  Pipeline /    │  │   │
│  │  │ Center   │  Studio  │  Lab     │  FPGA Monitor  │  │   │
│  │  └──────────┴──────────┴──────────┴────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                    ↓ TCP/UDP Protocol                        │
├─────────────────────────────────────────────────────────────┤
│                    ZYBO Z7-10 BOARD                          │
│  ┌──────────────────────┐   ┌──────────────────────────┐    │
│  │   ARM Cortex-A9      │   │   Programmable Logic     │    │
│  │   - Device Control   │   │   - Grayscale IP         │    │
│  │   - Camera Mgmt      │   │   - Sobel Edge Detection │    │
│  │   - Telemetry        │   │   - AXI DMA              │    │
│  │   - Lightweight AI   │   │   - AXI-Lite Registers   │    │
│  └──────────────────────┘   └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### 12 Functional Application Pages

| Page | Description |
|------|-------------|
| **Command Center** | Live monitoring, dual camera view, system telemetry, event feed |
| **Vision Studio** | 16 real CV algorithms with adjustable parameters and pipeline ordering |
| **AI Intelligence Lab** | Model registry, loading, inference, confidence thresholds |
| **Motion Intelligence** | Frame differencing, background subtraction, tracking, heatmaps |
| **Anomaly Laboratory** | Anomaly scoring, heatmaps, threshold-based detection |
| **Pipeline Architect** | Visual pipeline editor with validation and templates |
| **FPGA Monitor** | Resource utilization, live telemetry, AXI status |
| **Performance Lab** | Real benchmarking with FPS, latency, throughput metrics |
| **Dataset Explorer** | Dataset import, browsing, class distribution, validation |
| **Event Intelligence** | Event management, search, filtering, export |
| **Research Reports** | PDF/CSV/JSON report generation |
| **System Configuration** | Device, camera, AI, storage settings |

### Core Capabilities

- **16 Vision Algorithms**: Grayscale, Gaussian/Median/Bilateral blur, CLAHE, Gamma correction, Sharpening, Sobel, Scharr, Canny, Binary/Adaptive/Otsu thresholding, Morphology (erosion/dilation/opening/closing), ROI
- **Motion Detection**: Frame differencing, background subtraction, centroid tracking, optical flow, Kalman tracking, motion heatmaps, zone-based detection
- **AI Model Management**: Classification, detection, anomaly detection with ONNX runtime support
- **Adaptive Controller**: Rule-based intelligence adjusting parameters based on system state
- **Pipeline Engine**: Safe, validated processing pipeline with no arbitrary code execution
- **Database**: SQLite persistence with full schema for telemetry, events, benchmarks, models, datasets
- **Protocol**: Versioned TCP/UDP communication with handshake, commands, acknowledgements, heartbeat

---

## Hardware Specifications

**Target Board**: Digilent ZYBO Z7-10
- Zynq-7010 SoC (Dual-core ARM Cortex-A9 @ 667MHz)
- 512MB DDR3L memory
- 28K logic cells, 80 DSP slices, 80 BRAM blocks
- Pcam-compatible camera interface
- HDMI output, Ethernet, USB/UART

---

## Software Stack

| Layer | Technology |
|-------|-----------|
| Desktop GUI | Python 3.11, PySide6, PyQtGraph |
| Computer Vision | OpenCV 4.x, NumPy |
| AI/ML | PyTorch (workstation), ONNX Runtime (inference) |
| Database | SQLite, SQLAlchemy-style abstraction |
| Reports | ReportLab (PDF), CSV/JSON exporters |
| FPGA | Verilog, Vivado 2023.x, AXI4-Stream/Lite |
| Embedded | C/C++, Vitis-compatible structure |
| Testing | pytest, pytest-qt |
| Packaging | PyInstaller |

---

## Repository Layout

```
VISIONFORGE-X/
├── desktop_app/
│   ├── main.py                 # Application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── config/
│   │   └── settings.py         # Configuration management
│   ├── frontend/
│   │   ├── main_window.py      # Main window with all pages
│   │   ├── navigation.py       # Sidebar navigation
│   │   ├── design_system/      # Color/typography tokens
│   │   ├── components/         # Reusable UI components
│   │   └── pages/              # 12 application pages
│   ├── backend/
│   │   ├── vision/             # CV engine, motion analysis
│   │   ├── ai/                 # Model registry, inference
│   │   ├── adaptive/           # Adaptive controller
│   │   ├── pipeline/           # Pipeline engine
│   │   ├── analytics/          # Benchmarking
│   │   ├── events/             # Event management
│   │   ├── storage/            # Database layer
│   │   └── reports/            # Report generation
│   ├── adapters/               # Device abstraction
│   ├── protocol/               # Communication protocol
│   └── tests/                  # Test suite
├── embedded/                   # ARM-side services
├── fpga/                       # Verilog IP cores
├── ai_models/                  # Model storage
├── documentation/              # Technical docs
└── scripts/                    # Build/utility scripts
```

---

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
cd desktop_app
pip install -r requirements.txt
```

### Run Application
```bash
python main.py
```

### Run Tests
```bash
cd desktop_app
pytest tests/ -v
```

---

## Usage

### Simulation Mode (Default)
1. Launch the application
2. Click **Connect** (auto-selects simulation mode)
3. Click **Start** to begin video processing
4. Navigate through all 12 pages to explore features

### Hardware Mode
1. Connect ZYBO Z7-10 via Ethernet
2. Configure board IP in **System Configuration**
3. Switch mode to **hardware**
4. Click **Connect**

---

## Protocol

The platform uses a versioned JSON-based protocol over TCP for control and UDP for video frames. See `documentation/COMMUNICATION_PROTOCOL.md` for full details.

---

## Testing

```
pytest tests/ -v
```

Test coverage includes:
- Protocol serialization/deserialization
- Vision algorithm correctness
- Device simulation
- Database persistence
- Pipeline validation
- Adaptive controller logic
- Benchmark calculations

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](documentation/ARCHITECTURE.md) | System architecture details |
| [HARDWARE_INTEGRATION.md](documentation/HARDWARE_INTEGRATION.md) | ZYBO integration guide |
| [COMMUNICATION_PROTOCOL.md](documentation/COMMUNICATION_PROTOCOL.md) | Protocol specification |
| [DATABASE_SCHEMA.md](documentation/DATABASE_SCHEMA.md) | Database design |
| [AI_MODEL_GUIDE.md](documentation/AI_MODEL_GUIDE.md) | Model integration |
| [FPGA_INTEGRATION.md](documentation/FPGA_INTEGRATION.md) | FPGA IP guide |
| [SIMULATION_GUIDE.md](documentation/SIMULATION_GUIDE.md) | Simulation mode |
| [TESTING_GUIDE.md](documentation/TESTING_GUIDE.md) | Test framework |
| [WINDOWS_BUILD.md](documentation/WINDOWS_BUILD.md) | Packaging guide |
| [IMPLEMENTATION_STATUS.md](documentation/IMPLEMENTATION_STATUS.md) | Feature status |

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Limitations

- FPGA IP cores are templates requiring Vivado synthesis for actual hardware
- AI model inference in hardware mode requires compatible ARM runtime
- Full-resolution video processing occurs on the board; desktop receives lower-resolution preview
- Some benchmark values in simulation mode are synthetic and labeled as SIMULATED
=======
# VISIONFORGE-X
VISIONFORGE X — Universal Adaptive Edge Vision Intelligence Platform.  FPGA-accelerated computer vision + AI inference on a PySide6 desktop GUI.  12-page control suite, 16 CV algorithms, motion tracking, anomaly detection,  real-time benchmarking, and ZYBO Z7-10 hardware integration. Runs in simulation or hardware mode.
>>>>>>> 77664ce727262919f483468146bfb98b511a5c3e
