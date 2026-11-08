# VISIONFORGE X - Troubleshooting

## Common Issues

### Application Won't Start
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Qt platform plugin error**: Set `QT_QPA_PLATFORM=offscreen` for headless
- **PySide6 import error**: Reinstall PySide6

### Camera Not Showing
- **Simulation mode**: Click Connect then Start
- **Hardware mode**: Check board IP and network connection
- **Permission error**: Grant camera access in OS settings

### No Telemetry Updates
- **Worker not running**: Ensure Start is clicked after Connect
- **Database locked**: Close other instances accessing the DB

### Vision Algorithm Errors
- **Invalid parameters**: Check kernel sizes are odd numbers
- **Empty frame**: Ensure camera is running before processing

### Database Errors
- **Disk full**: Check storage path has space
- **Corrupt DB**: Delete `storage/visionforge.db` to reset

### FPGA Monitor Shows N/A
- **No hardware**: FPGA data requires actual board connection
- **No report imported**: Import Vivado utilization report

### Benchmark Results Zero
- **No frames processed**: Start camera and processing first
- **Session not stopped**: Stop benchmark to finalize results

### Reports Fail to Generate
- **ReportLab missing**: `pip install reportlab`
- **Permission denied**: Check output directory permissions

## Logs
Check `logs/visionforge.log` for detailed error messages.

## Reset Configuration
In System Configuration → Actions → Reset to Defaults.

## Reinstall
```bash
pip uninstall -y PySide6 opencv-python numpy pyqtgraph reportlab
pip install -r requirements.txt
```
