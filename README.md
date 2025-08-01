# Rock 5B Plus Kernel Enhancement System

A comprehensive system for the Rock 5B Plus (RK3588) that provides:
- GPU driver switching from Panfrost to Mali
- Detailed kernel logging
- Power monitoring
- Crash reporting

## Features

### 1. GPU Driver Switch
- Switches from Panfrost to Mali proprietary driver
- Enables OpenCL and Vulkan support
- Supports 8K HDMI output
- Includes automatic configuration and verification

### 2. Kernel Logging System
- Continuous background logging daemon
- Captures build-time and runtime errors
- Configurable log rotation and storage
- Structured logging with severity levels
- Automated log management

### 3. Power Monitoring
- Real-time voltage monitoring
- Current input tracking
- Power consumption metrics
- Historical power data storage
- Configurable monitoring intervals

### 4. Crash Reporting
- Automatic crash detection
- Detailed crash reports with system state
- Boot-time crash checking
- Historical crash data retention
- Structured report storage

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-repo/rock5b-kernel-enhancement.git
cd rock5b-kernel-enhancement
```

2. Run the setup script as root:
```bash
sudo python3 scripts/setup.py
```

The setup script will:
- Install required Mali driver packages
- Configure system settings
- Enable necessary services
- Verify the installation

## Configuration

### GPU Driver
Configuration files in `/etc/apt/preferences.d/mali` and `/etc/modprobe.d/panfrost.conf`

### Logging System
Environment variables in `/etc/environment`:
- `KERNEL_LOG_PATH`: Log directory path
- `KERNEL_LOG_LEVEL`: Logging level
- `KERNEL_LOG_MAX_SIZE`: Maximum log file size
- `KERNEL_LOG_ROTATE_COUNT`: Number of log files to retain

### Services
The system includes three systemd services:
- `kernel-logger.service`: Continuous kernel logging
- `power-monitor.service`: Power metrics collection
- `crash-reporter.service`: Crash detection and reporting

## Log Files

- Kernel logs: `/var/log/kernel/kernel.log`
- Power monitoring: `/var/log/kernel/power.log`
- Crash reports: `/var/log/kernel/crashes/`
- Crash reporter logs: `/var/log/kernel/crash_reporter.log`

## Verification

To verify the system is working correctly:

1. Check GPU driver:
```bash
lsmod | grep -E 'mali|bifrost_kbase'
```

2. Check services:
```bash
systemctl status kernel-logger power-monitor crash-reporter
```

3. Monitor logs:
```bash
tail -f /var/log/kernel/kernel.log
tail -f /var/log/kernel/power.log
```

## Troubleshooting

1. If services fail to start:
   - Check service logs: `journalctl -u service-name`
   - Verify file permissions
   - Ensure all dependencies are installed

2. If GPU driver switch fails:
   - Verify hardware compatibility
   - Check Xorg logs
   - Ensure correct driver package is installed

3. If power monitoring shows no data:
   - Verify sysfs paths exist
   - Check power supply detection
   - Verify service permissions

## Support

For issues and support:
1. Check the logs in `/var/log/kernel/`
2. Review crash reports if available
3. Submit an issue with relevant log output

## License

This project is licensed under the MIT License - see the LICENSE file for details.