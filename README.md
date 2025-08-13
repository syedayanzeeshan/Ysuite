# YSuite - Comprehensive Rock 5B+ Monitoring and Management Suite

A unified package for headless Rock 5B+ systems with real-time monitoring, crash detection, power management, and system optimization.

## 🚀 Features

### **ytop** - Real-time System Performance Monitor
- CPU, GPU, NPU, Memory monitoring
- Temperature and fan control
- Beautiful CLI dashboard with progress bars

### **ylog** - System Log Monitor
- Real-time critical event detection
- JSON-structured log storage
- Pattern-based error classification

### **ycrash** - Crash Detection and Analysis
- Kernel crash detection
- Segmentation fault monitoring
- OOM and system panic tracking

### **ypower** - Power Monitoring and PD Negotiation
- Multi-source power detection (USB PD, ADC, barrel jack)
- Real-time voltage/current monitoring
- Aggressive 3A current negotiation

## 📦 Installation

### Quick Install
```bash
# Download and install YSuite
sudo ./install_ysuite.sh
```

### Direct Board Installation
```bash
# Copy files to your Rock 5B+ board (via USB, SD card, or direct transfer)
# Then on the board, run:
sudo ./install_ysuite.sh
```

## 🎯 Usage

### Get Help
```bash
yhelp
```

### Basic Commands
```bash
# Real-time system monitoring
ytop

# Monitor system logs
ylog

# Check for crashes
ycrash

# Monitor power
ypower
```

## 📁 Package Contents

- **ysuite.py** - Main Python script with all functionality
- **install_ysuite.sh** - Installation script
- **deploy_ysuite.sh** - Installation guide and instructions
- **YSUITE_SUMMARY.md** - Detailed documentation

## 🔧 Requirements

- Rock 5B+ board
- Python 3.8+
- Linux kernel with sysfs support
- Root/sudo access for hardware monitoring

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
