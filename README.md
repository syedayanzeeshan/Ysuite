# YSuite v2.1.0 - Comprehensive System Monitoring and Management Suite

A unified package for headless systems with real-time monitoring, crash detection, power management, and system optimization.

## Features

- **Real-time System Monitoring**: CPU, GPU, NPU, memory, temperature, and power usage
- **Power Management**: Accurate power readings from hardware sensors (USB-C PD, regulators, ADC)
- **Watchdog System**: CPU/RAM monitoring with automatic reboot and WiFi connectivity monitoring
- **Crash Detection**: Automatic crash logging and system recovery
- **GPU Compute Support**: OpenCL and Vulkan monitoring and testing
- **Hardware Integration**: Direct access to system sensors and hardware interfaces

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/syedayanzeeshan/Ysuite.git
cd Ysuite

# Install YSuite
sudo ./install_ysuite.sh
```

### Usage

```bash
# System monitoring
ytop

# Power monitoring
ypower

# Log monitoring
ylog

# Crash monitoring
ycrash

# Watchdog status
ydog
```

## System Requirements

- Linux system with Python 3.6+
- Root access for hardware monitoring
- USB-C PD capable power supply (recommended)

## Power Configuration

YSuite automatically detects and prioritizes power sources:
1. **USB-C PD sensors** (highest priority)
2. **Hardware regulators** (voltage/current from kernel)
3. **ADC readings** (fallback)

For optimal performance, use a 45W+ USB-C PD charger.

## Watchdog Features

- **CPU/RAM Monitoring**: Reboots if usage exceeds 80% for 15 seconds
- **WiFi Monitoring**: Restarts modem/USB if connectivity lost for 60 seconds
- **Automatic Recovery**: System health monitoring and crash detection

## License

ahaha

## Support

For issues and feature requests, please open an issue on GitHub.

