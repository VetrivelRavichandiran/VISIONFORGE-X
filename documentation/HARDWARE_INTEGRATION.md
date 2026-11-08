# VISIONFORGE X - Hardware Integration Guide

## Target Board: Digilent ZYBO Z7-10

### Board Specifications
- Zynq-7010 SoC (Dual-core ARM Cortex-A9 @ 667MHz)
- 512MB DDR3L
- 28K logic cells, 80 DSP slices, 80 BRAM
- Pcam camera, HDMI out, GbE, USB/UART

### Connection Setup
1. Connect ZYBO to network (Ethernet)
2. Default IP: 192.168.1.100 (configurable)
3. Configure in System Configuration page

### Firmware Requirements
- Embedded Linux with TCP/UDP service
- AXI DMA for frame transport
- Camera driver (Pcam or OV5640)
- HDMI output for local preview

### Integration Steps
1. Build Vivado project with IP cores
2. Generate bitstream
3. Deploy embedded Linux image
4. Run device service on ARM
5. Connect desktop in hardware mode

### IP Cores Provided
- `grayscale_conv.v` - RGB to grayscale
- `sobel_edge.v` - Edge detection with AXI-Lite control

### Verification
- TCP handshake successful
- Telemetry stream received
- Frame transport working (UDP)
- Command acknowledgements received
