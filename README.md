import pypandoc

readme = r'''<div align="center">

# 🚀 VISIONFORGE X

### Universal Adaptive Edge Vision Intelligence Platform

**See faster. Think smarter. Process at the edge.**

An integrated computer-vision and AI desktop platform combining FPGA acceleration, embedded processing, adaptive intelligence, and real-time visual analytics — built around the **Digilent ZYBO Z7-10 (Xilinx Zynq-7010 SoC)**.

<br/>

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt&logoColor=white)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)
![FPGA](https://img.shields.io/badge/Hardware-Zynq--7000-orange)
![License](https://img.shields.io/badge/License-MIT-blue)
![Platforms](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

<br/>

**[Getting Started](#-quick-start) · [Features](#-platform-capabilities) · [Architecture](#-system-architecture) · [Documentation](#-documentation)**

</div>

---

## ⚡ At a Glance

VISIONFORGE X brings the major building blocks of an edge-vision system into one desktop environment:

| Capability | What it delivers |
|---|---|
| **Computer Vision** | 16 image-processing algorithms with configurable parameters and pipeline ordering |
| **AI Inference** | Model registry and inference workflows, including ONNX Runtime support |
| **Motion Intelligence** | Motion detection, tracking, optical flow, and heatmap visualization |
| **FPGA Acceleration** | Verilog IP integration for grayscale processing and Sobel edge detection |
| **Embedded Control** | ARM-side device management, camera control, and telemetry |
| **System Analytics** | FPS, latency, throughput, event records, and report generation |

> **Start without hardware.** The application launches in Simulation Mode, allowing you to explore its workflows without a connected FPGA board. Hardware Mode is designed for communication with a ZYBO Z7-10 over TCP/UDP.

---

## 🧭 System Architecture

VISIONFORGE X uses a workstation-to-edge-device architecture. The desktop application provides the operator interface and high-level vision/AI workflows, while the Zynq platform separates embedded control from programmable-logic processing.

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         HOST WORKSTATION                             │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              VISIONFORGE X · PySide6 Desktop                  │  │
│  │                                                               │  │
│  │   Command Center   Vision Studio   AI Lab   Pipeline Monitor  │  │
│  │                                                               │  │
│  │   Analytics   Events   Datasets   Reports   Configuration     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                               │                                     │
│                         TCP / UDP                                  │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                         DIGILENT ZYBO Z7-10                         │
│                         Xilinx Zynq-7010 SoC                         │
│                                                                     │
│  ┌────────────────────────────┐  ┌────────────────────────────────┐  │
│  │     Processing System     │  │       Programmable Logic       │  │
│  │       ARM Cortex-A9       │  │                                │  │
│  │                            │  │  Grayscale IP                  │  │
│  │  Device and camera control│  │  Sobel edge detection          │  │
│  │  Telemetry                │  │  AXI DMA                        │  │
│  │  Lightweight AI           │  │  AXI-Lite registers             │  │
│  └────────────────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Two operating modes

| Area | Simulation Mode | Hardware Mode |
|---|---|---|
| Setup | Runs without an FPGA board | Requires a ZYBO Z7-10 |
| Camera input | Synthetic video feed | Real camera through Pcam interface |
| Vision processing | OpenCV on workstation | FPGA-accelerated and OpenCV hybrid |
| AI inference | ONNX on workstation | Lightweight ARM runtime |
| FPGA telemetry | Simulated metrics | LUT, BRAM, and DSP utilization |
| Communication | No board connection required | TCP/UDP over Ethernet |

---

## ✨ Platform Capabilities

### 🖥️ 12-page desktop command suite

| Workspace | Purpose |
|---|---|
| ⚡ **Command Center** | Live monitoring, dual-camera view, system telemetry, and event feed |
| 🔬 **Vision Studio** | 16 computer-vision algorithms with adjustable parameters and pipeline ordering |
| 🤖 **AI Intelligence Lab** | Model registry, model loading, inference, and confidence thresholds |
| 🏃 **Motion Intelligence** | Frame differencing, background subtraction, tracking, and heatmaps |
| ⚠️ **Anomaly Laboratory** | Anomaly scoring, heatmaps, and threshold-based detection |
| 🔗 **Pipeline Architect** | Visual pipeline editor with validation and templates |
| 🔧 **FPGA Monitor** | Resource utilization, telemetry, and AXI status |
| 📊 **Performance Lab** | FPS, latency, and throughput benchmarking |
| 📁 **Dataset Explorer** | Dataset import, browsing, class distribution, and validation |
| 📋 **Event Intelligence** | Event management, search, filtering, and export |
| 📄 **Research Reports** | PDF, CSV, and JSON report generation |
| ⚙️ **System Configuration** | Device, camera, AI, and storage settings |

### 🔬 Computer-vision toolkit

The platform includes 16 image-processing algorithm groups and operations:

- **Image enhancement:** grayscale conversion, Gaussian blur, median blur, bilateral filtering, CLAHE, gamma correction, and sharpening.
- **Edge detection:** Sobel, Scharr, and Canny.
- **Thresholding:** binary, adaptive, and Otsu thresholding.
- **Morphology:** erosion, dilation, opening, and closing.
- **Region processing:** region of interest (ROI) operations.

### 🏃 Motion and scene intelligence

- Frame differencing and background subtraction
- Centroid-based object tracking
- Optical flow
- Kalman tracking
- Motion heatmaps
- Zone-based motion detection

### 🧠 AI and adaptive processing

- Model registry and model-loading workflows
- Classification, object-detection, and anomaly-detection workflows
- ONNX Runtime inference support
- Confidence-threshold configuration
- Rule-based adaptive controller for adjusting parameters according to system state

### 🔗 Validated processing pipelines

The pipeline engine supports configurable processing sequences with validation and templates. It is designed to execute approved processing operations rather than arbitrary user-supplied code.

### 📈 Monitoring, persistence, and reporting

- FPS, latency, and throughput measurements
- Telemetry and event persistence using SQLite
- Model and dataset records
- Event search, filtering, and export
- PDF, CSV, and JSON report generation

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Desktop application | Python 3.11+, PySide6, PyQtGraph |
| Computer vision | OpenCV 4.x, NumPy |
| AI / ML | PyTorch (workstation), ONNX Runtime (inference) |
| Database | SQLite |
| Reporting | ReportLab, CSV, JSON |
| FPGA design | Verilog, Vivado 2023.x, AXI4-Stream, AXI-Lite |
| Embedded software | C/C++, Vitis-compatible structure |
| Communication | Versioned TCP/UDP protocol |
| Testing | pytest, pytest-qt |
| Packaging | PyInstaller |

---

## 🚀 Quick Start

### Requirements

- Python **3.11 or newer**
- `pip`
- Optional: Digilent **ZYBO Z7-10** board for hardware operation

### 1. Clone the repository

```bash
git clone https://github.com/VetrivelRavichandiran/VISIONFORGE-X.git
cd VISIONFORGE-X/desktop_app
```

### 2. Create and activate a virtual environment

**Windows**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch VISIONFORGE X

```bash
python main.py
```

> ✅ **No FPGA board is required to get started.** The application runs in Simulation Mode by default.

### 5. Run the tests

From the `desktop_app` directory:

```bash
pytest tests/ -v
```

---

## 📁 Repository Layout

```text
VISIONFORGE-X/
├── desktop_app/
│   ├── main.py
│   ├── requirements.txt
│   ├── config/
│   │   └── settings.py
│   ├── frontend/
│   │   ├── main_window.py
│   │   ├── navigation.py
│   │   ├── design_system/
│   │   ├── components/
│   │   └── pages/
│   ├── backend/
│   │   ├── vision/
│   │   ├── ai/
│   │   ├── adaptive/
│   │   ├── pipeline/
│   │   ├── analytics/
│   │   ├── events/
│   │   ├── storage/
│   │   └── reports/
│   ├── adapters/
│   ├── protocol/
│   └── tests/
├── embedded/              # ARM-side services (C/C++)
├── fpga/                  # Verilog IP cores
├── documentation/         # Architecture and engineering guides
├── scripts/               # Build and utility scripts
├── .github/               # GitHub templates and workflows
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── CHANGELOG.md
```

---

## 📚 Documentation

The `documentation/` directory contains focused engineering guides:

| Document | Description |
|---|---|
| [Architecture](documentation/ARCHITECTURE.md) | System architecture and data flow |
| [Hardware Integration](documentation/HARDWARE_INTEGRATION.md) | ZYBO board integration |
| [Communication Protocol](documentation/COMMUNICATION_PROTOCOL.md) | TCP/UDP protocol specification |
| [Database Schema](documentation/DATABASE_SCHEMA.md) | SQLite database design |
| [AI Model Guide](documentation/AI_MODEL_GUIDE.md) | Model integration and ONNX workflows |
| [FPGA Integration](documentation/FPGA_INTEGRATION.md) | FPGA IP core integration |
| [Simulation Guide](documentation/SIMULATION_GUIDE.md) | Simulation mode details |
| [Testing Guide](documentation/TESTING_GUIDE.md) | Test framework and execution |
| [Windows Build](documentation/WINDOWS_BUILD.md) | PyInstaller packaging |
| [Implementation Status](documentation/IMPLEMENTATION_STATUS.md) | Feature implementation status |
| [Troubleshooting](documentation/TROUBLESHOOTING.md) | Common issues and fixes |

---

## 🤝 Contributing

Contributions, ideas, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push the branch: `git push origin feature/your-feature`.
5. Open a Pull Request.

Please review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

---

## 🔐 Security

For security-related concerns, please follow the reporting guidance in [SECURITY.md](SECURITY.md).

## 📄 License

VISIONFORGE X is released under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Digilent** — ZYBO Z7-10 development board
- **AMD Xilinx** — Zynq-7000 SoC architecture and FPGA ecosystem
- **OpenCV** — Computer-vision library
- **Qt / PySide6** — Desktop application framework
- **Contributors** — Everyone helping improve VISIONFORGE X

---

## 📬 Contact & Support

- **Bug reports:** [GitHub Issues](https://github.com/VetrivelRavichandiran/VISIONFORGE-X/issues)
- **Feature discussions:** [GitHub Discussions](https://github.com/VetrivelRavichandiran/VISIONFORGE-X/discussions)
- **Security:** See [SECURITY.md](SECURITY.md)

---

<div align="center">

### ⭐ Build at the edge. See beyond the frame.

If VISIONFORGE X is useful to you, consider giving the repository a star.

**VISIONFORGE X** · Adaptive Vision · Edge AI · FPGA Engineering

</div>
'''

output_path = "/mnt/data/VISIONFORGE_X_README.md"
pypandoc.convert_text(readme, "md", format="md", outputfile=output_path, extra_args=["--standalone"])
print(f"Created: {output_path}")
