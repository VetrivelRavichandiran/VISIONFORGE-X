# VISIONFORGE X - FPGA Integration Guide

## IP Cores

### Grayscale Conversion
- File: `fpga/hdl/grayscale_conv.v`
- Interface: AXI4-Stream in/out
- Function: RGB → Grayscale (BT.601 coefficients)
- Fixed-point: Y = (77R + 150G + 29B) >> 8

### Sobel Edge Detection
- File: `fpga/hdl/sobel_edge.v`
- Interface: AXI4-Stream + AXI-Lite control
- Function: 3x3 Sobel operator
- Control registers: threshold, enable, frame counter

## Vivado Project Structure
```
fpga/vivado/
├── visionforge.xpr          # Vivado project
├── hdl/                     # Verilog sources
├── ip/                      # Generated IP
├── constraints/             # XDC constraint files
└── reports/                 # Synthesis reports
```

## Integration Steps
1. Create Vivado project for Zynq-7010
2. Add HDL sources
3. Generate block design with PS-PL interfaces
4. Configure AXI DMA for frame transport
5. Run synthesis and implementation
6. Generate bitstream
7. Export hardware to Vitis

## Resource Estimates
- Grayscale: ~200 LUTs, minimal FFs
- Sobel: ~1500 LUTs, line buffers

## Constraints
- System clock: 100MHz
- Camera interface: Pcam/OV5640 timing
