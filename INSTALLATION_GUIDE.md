# YSuite v2.1.0 - Installation Guide

## Quick Installation

```bash
git clone https://github.com/syedayanzeeshan/Ysuite.git
cd YSuite
sudo ./install_ysuite.sh
```

## Features

- **Real-time monitoring**: CPU, GPU, NPU, memory, temperature, power
- **Power management**: USB-C PD, regulators, ADC sensors
- **Watchdog system**: CPU/RAM monitoring + WiFi/USB restart
- **GPU compute**: OpenCL/Vulkan support with Mali drivers

## Commands

- `ytop` - System monitoring
- `ypower` - Power monitoring  
- `ylog` - Log monitoring
- `ycrash` - Crash detection
- `yhelp` - Help system

## Watchdog Features

- CPU/RAM >80% for 15s → System reboot
- WiFi unavailable for 60s → USB/network restart

## Watchdog Status Verification

To check and verify both watchdog policies:

```bash
# Run comprehensive status check
sudo /usr/local/bin/check_watchdog_status.sh

# Quick status checks
sudo systemctl status watchdog-monitor.service
sudo tail -f /var/log/watchdog_monitor.log
```

### Policy 1: System Health Monitoring
- **CPU Threshold**: 80%
- **RAM Threshold**: 80%
- **Duration**: 15 seconds
- **Action**: System reboot

### Policy 2: Network Health Monitoring
- **WiFi Timeout**: 60 seconds
- **Action**: Restart USB ports and network adapters

## Power Configuration

- Use 45W+ USB-C PD charger
- Connect to display Type-C port
- YSuite shows power recommendations

## Troubleshooting

- Check logs: `/var/log/watchdog_monitor.log`
- Verify service: `sudo systemctl status watchdog-monitor.service`
- Power issues: Try display port, different charger

## Support

GitHub: https://github.com/syedayanzeeshan/Ysuite
