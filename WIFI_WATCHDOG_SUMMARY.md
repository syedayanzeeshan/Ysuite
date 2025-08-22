# Enhanced Watchdog Monitor with WiFi Monitoring

## Overview
The watchdog monitor has been successfully enhanced to include WiFi connectivity monitoring and automatic modem/USB port restart functionality.

## Features Implemented

### 1. CPU and RAM Monitoring
- **CPU Threshold**: 80%
- **RAM Threshold**: 80%
- **Duration Threshold**: 15 seconds
- **Action**: System reboot if exceeded

### 2. WiFi Connectivity Monitoring
- **WiFi Timeout**: 60 seconds
- **Detection**: Monitors all WiFi interfaces starting with 'wl' (wlP2p33s0, wlxa047d70015ea)
- **Connectivity Test**: Pings 8.8.8.8 to verify internet access
- **Action**: Restarts modem and USB ports if WiFi is lost for 60+ seconds

### 3. Modem/USB Port Restart Functionality
When WiFi is lost for 60 seconds, the system will:
1. **Unbind USB devices**: Removes modem devices from USB bus
2. **Reset USB ports**: Toggles USB port authorization
3. **Rebind devices**: Reconnects devices to USB bus
4. **Wait for reinitialization**: 10-second delay for device recovery
5. **Verify restoration**: Checks if WiFi connectivity is restored

## Current Status

### ✅ Working Components
- **Enhanced watchdog script**: `/usr/local/bin/watchdog_monitor.py`
- **Systemd service**: `watchdog-monitor.service` (enabled and running)
- **WiFi detection**: Successfully detects `wlP2p33s0` with IP `10.35.0.215`
- **Logging**: Comprehensive logging to `/var/log/watchdog_monitor.log`
- **Service management**: Automatic start on boot, restart on failure

### 📊 Current Monitoring Data
- **CPU Usage**: 0.1-4.3% (well below 80% threshold)
- **RAM Usage**: 5.0-5.6% (well below 80% threshold)
- **WiFi Status**: Connected via `wlP2p33s0` with IP `10.35.0.215`
- **Internet Connectivity**: Verified via ping to 8.8.8.8

## Service Commands

```bash
# Check service status
systemctl status watchdog-monitor.service

# View real-time logs
journalctl -u watchdog-monitor -f

# View log file
tail -f /var/log/watchdog_monitor.log

# Restart service
systemctl restart watchdog-monitor.service

# Stop service
systemctl stop watchdog-monitor.service

# Start service
systemctl start watchdog-monitor.service
```

## Configuration

### Thresholds (configurable in script)
- **CPU threshold**: 80%
- **RAM threshold**: 80%
- **Duration threshold**: 15 seconds
- **WiFi timeout**: 60 seconds

### Log Files
- **Service logs**: `/var/log/watchdog_monitor.log`
- **System logs**: `journalctl -u watchdog-monitor`

## Safety Features

1. **Stress test removal**: All stress test tools removed to prevent accidental triggers
2. **Graceful handling**: Service restarts automatically if it fails
3. **Comprehensive logging**: All actions logged with timestamps
4. **Error recovery**: Multiple fallback methods for USB port reset
5. **Verification**: Checks WiFi status after modem restart

## Test Results

### WiFi Monitoring Test
- ✅ Detects WiFi interfaces: `wlP2p33s0`, `wlxa047d70015ea`
- ✅ Identifies active connection: `wlP2p33s0` with IP `10.35.0.215`
- ✅ Verifies internet connectivity via ping test
- ✅ Logs status every 5 seconds

### Service Status
- ✅ Service running: `active (running)`
- ✅ Auto-start enabled: `enabled`
- ✅ Process ID: 2263
- ✅ Memory usage: 7.5M
- ✅ CPU usage: Minimal

## Implementation Details

### WiFi Detection Logic
1. Scans all network interfaces for 'wl' prefix
2. Checks for valid IPv4 addresses (excludes localhost and AP mode IPs)
3. Tests internet connectivity with ping to 8.8.8.8
4. Returns connection status and interface details

### USB Port Reset Methods
1. **Device-specific**: Unbind/rebind specific USB devices
2. **Port-level**: Toggle USB port authorization
3. **Fallback**: Multiple reset attempts with error handling

### Logging Format
```
2025-08-21 12:24:32,649 - INFO - CPU: 0.1%, RAM: 5.2%, WiFi: WiFi wlP2p33s0 connected with IP 10.35.0.215
```

## Next Steps

The enhanced watchdog is now fully operational and will:
1. Monitor CPU and RAM usage continuously
2. Detect WiFi connectivity loss
3. Automatically restart modem/USB ports if WiFi is lost for 60+ seconds
4. Reboot system if CPU or RAM exceeds 80% for 15+ seconds
5. Log all activities for monitoring and debugging

The system is now protected against both resource exhaustion and network connectivity issues.
