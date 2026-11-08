# 🚀 VISIONFORGE X

## Universal Adaptive Edge Vision Intelligence Platform

> **FPGA-accelerated computer vision · AI inference · Real-time edge intelligence** — unified in one powerful desktop application.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-6.6%2B-14Y7V9.svg?logo=qt)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8.svg?logo=opencv)
![Tests](https://img.shields.io/badge/Tests-pytest%20%2B%20pytest--qt-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

---

VISIONFORGE X is a production-structured software platform built around the **Digilent ZYBO Z7-10** (Xilinx Zynq-7010 SoC). It fuses **FPGA-accelerated image processing**, **ARM-based embedded control**, **adaptive computer vision**, and **AI-driven visual understanding** into a single, cohesive desktop GUI.

Designed for the modern edge-computing stack, it runs fully in **Simulation Mode** out of the box — and seamlessly switches to **Hardware Mode** when connected to a real ZYBO board over TCP/UDP.

---

## 📸 Platform Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WINDOWS WORKSTATION                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              VISIONFORGE X Desktop Application (PySide6)       │  │
│  │  ┌──────────┬──────────┬──────────┬────────────────────────┐  │  │
│  │  │ Command  │  Vision  │    AI    │   Pipeline / FPGA      │  │  │
│  │  │  Center  │  Studio  │   Lab    │       Monitor          │  │  │
│  │  └──────────┴──────────┴──────────┴────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                        ↓ TCP/UDP Protocol                             │
├─────────────────────────────────────────────────────────────────────┤
│                        ZYBO Z7-10 BOARD                               │
│  ┌────────────────────────┐      ┌───────────────────────────────┐  │
│  │    ARM Cortex-A9       │      │      Programmable Logic        │  │
│  │  - Device Control      │      │  - Grayscale IP                │  │
│  │  - Camera Management   │      │  - Sobel Edge Detection        │  │
│  │  - Telemetry           │      │  - AXI DMA                     │  │
│  │  - Lightweight AI      │      │  - AXI-Lite Registers          │  │
│  └────────────────────────┘      └───────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 🖥️ 12-Page Command Suite

| Page | Description |
|------|-------------|
| **⚡ Command Center** | Live monitoring, dual camera view, system telemetry, event feed |
| **🔬 Vision Studio** | 16 real CV algorithms with adjustable parameters and pipeline ordering |
| **🤖 AI Intelligence Lab** | Model registry, loading, inference, confidence thresholds |
| **🏃 Motion Intelligence** | Frame differencing, background subtraction, tracking, heatmaps |
| **⚠️ Anomaly Laboratory** | Anomaly scoring, heatmaps, threshold-based detection |
| **🔗 Pipeline Architect** | Visual pipeline editor with validation and templates |
| **🔧 FPGA Monitor** | Resource utilization, live telemetry, AXI status |
| **📊 Performance Lab** | Real benchmarking with FPS, latency, throughput metrics |
| **📁 Dataset Explorer** | Dataset import, browsing, class distribution, validation |
| **📋 Event Intelligence** | Event management, search, filtering, export |
| **📄 Research Reports** | PDF/CSV/JSON report generation |
| **⚙️ System Configuration** | Device, camera, AI, storage settings |

### 🧠 Core Capabilities

- **16 Vision Algorithms** — Grayscale, Gaussian/Median/Bilateral blur, CLAHE, Gamma correction, Sharpening, Sobel, Scharr, Canny, Binary/Adaptive/Otsu thresholding, Morphology (erosion/dilation/opening/closing), ROI
- **Motion Detection** — Frame differencing, background subtraction, centroid tracking, optical flow, Kalman tracking, motion heatmaps, zone-based detection
- **AI Model Management** — Classification, detection, anomaly detection with ONNX Runtime support
- **Adaptive Controller** — Rule-based intelligence adjusting parameters based on system state
- **Pipeline Engine** — Safe, validated processing pipeline with no arbitrary code execution
- **Database** — SQLite persistence with full schema for telemetry, events, benchmarks, models, datasets
- **Protocol** — Versioned TCP/UDP communication with handshake, commands, acknowledgements, heartbeat

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **GUI** | Python 3.11+, PySide6, PyQtGraph |
| **Computer Vision** | OpenCV 4.x, NumPy |
| **AI/ML** | PyTorch (workstation), ONNX Runtime (inference) |
| **Database** | SQLite |
| **Reports** | ReportLab (PDF), CSV/JSON exporters |
| **FPGA** | Verilog, Vivado 2023.x, AXI4-Stream/Lite |
| **Embedded** | C/C++, Vitis-compatible structure |
| **Testing** | pytest, pytest-qt |
| **Packaging** | PyInstaller |

---

## 🏃 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip
- (Optional) Digilent ZYBO Z7-10 board for hardware mode

### Installation

```bash
# Clone the repository
git clone https://github.com/VetrivelRavichandiran/VISIONFORGE-X.git
cd VISIONFORGE-X/desktop_app

# Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
python main.py
```

> ✅ **Runs immediately in simulation mode — no hardware required.**

### Run the Test Suite

```bash
cd desktop_app
pytest tests/ -v
```

---

## 🔄 Simulation vs Hardware Mode

| Feature | Simulation Mode | Hardware Mode |
|---------|----------------|---------------|
| **Setup** | Zero setup, runs instantly | Requires ZYBO Z7-10 board |
| **Camera** | Synthetic video feed | Real camera via Pcam interface |
| **Vision Processing** | Full OpenCV on workstation | FPGA-accelerated + OpenCV hybrid |
| **AI Inference** | ONNX on workstation | Lightweight ARM runtime |
| **FPGA Telemetry** | Simulated metrics | Real LUT/BRAM/DSP utilization |
| **Connectivity** | N/A | TCP/UDP over Ethernet |

---

## 📦 Repository Structure

```
VISIONFORGE-X/
├── desktop_app/                 # Main desktop application
│   ├── main.py                  # Application entry point
│   ├── requirements.txt         # Python dependencies
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── frontend/
│   │   ├── main_window.py       # Main window with all 12 pages
│   │   ├── navigation.py        # Sidebar navigation rail
│   │   ├── design_system/       # Color/typography tokens
│   │   ├── components/          # Reusable UI components
│   │   └── pages/               # 12 application pages
│   ├── backend/
│   │   ├── vision/              # CV engine, motion analysis
│   │   ├── ai/                  # Model registry, inference
│   │   ├── adaptive/            # Adaptive controller
│   │   ├── pipeline/            # Pipeline engine
│   │   ├── analytics/           # Benchmarking
│   │   ├── events/              # Event management
│   │   ├── storage/             # Database layer
│   │   └── reports/             # Report generation
│   ├── adapters/                # Device abstraction
│   ├── protocol/                # Communication protocol
│   └── tests/                   # Test suite
├── embedded/                    # ARM-side services (C/C++)
├── fpga/                        # Verilog IP cores
├── documentation/               # Technical documentation
├── scripts/                     # Build/utility scripts
├── .github/                     # GitHub templates & workflows
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── CHANGELOG.md
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](documentation/ARCHITECTURE.md) | System architecture & data flow |
| [HARDWARE_INTEGRATION.md](documentation/HARDWARE_INTEGRATION.md) | ZYBO board integration guide |
| [COMMUNICATION_PROTOCOL.md](documentation/COMMUNICATION_PROTOCOL.md) | TCP/UDP protocol specification |
| [DATABASE_SCHEMA.md](documentation/DATABASE_SCHEMA.md) | SQLite database design |
| [AI_MODEL_GUIDE.md](documentation/AI_MODEL_GUIDE.md) | AI model integration & ONNX |
| [FPGA_INTEGRATION.md](documentation/FPGA_INTEGRATION.md) | FPGA IP core guide |
| [SIMULATION_GUIDE.md](documentation/SIMULATION_GUIDE.md) | Simulation mode details |
| [TESTING_GUIDE.md](documentation/TESTING_GUIDE.md) | Test framework & coverage |
| [WINDOWS_BUILD.md](documentation/WINDOWS_BUILD.md) | Windows packaging with PyInstaller |
| [IMPLEMENTATION_STATUS.md](documentation/IMPLEMENTATION_STATUS.md) | Feature completion status |
| [TROUBLESHOOTING.md](documentation/TROUBLESHOOTING.md) | Common issues & fixes |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Digilent** for the ZYBO Z7-10 development board
- **Xilinx/AMD** for Zynq-7000 SoC architecture
- **OpenCV** team for computer vision library
- **PySide6/Qt** for the GUI framework
- **All contributors** who have helped build VISIONFORGE X

---

## 📬 Contact & Support

- **Issues & Bug Reports** → [GitHub Issues](https://github.com/VetrivelRavichandiran/VISIONFORGE-X/issues)
- **Feature Requests** → [GitHub Discussions](https://github.com/VetrivelRavichandiran/VISIONFORGE-X/discussions)
- **Security Concerns** → See [SECURITY.md](SECURITY.md)

---

⭐ **If this project helps you, consider giving it a star!**
