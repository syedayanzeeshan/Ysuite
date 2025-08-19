# Rock 5B Plus Enhanced Kernel Build Guide

This document provides comprehensive instructions for building and deploying the enhanced kernel for Rock 5B Plus, which includes GPU driver switching, advanced logging, power monitoring, and crash reporting.

## Prerequisites

Required packages:
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    flex \
    bison \
    libssl-dev \
    libelf-dev \
    bc \
    kmod \
    cpio \
    dwarves \
    dpkg-dev \
    debhelper \
    fakeroot \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu
```

## Quick Start (5-minute setup)

1. Clone repository:
```bash
git clone https://github.com/your-repo/rock5b-kernel-enhancement.git
cd rock5b-kernel-enhancement
```

2. Build everything (takes ~30 minutes):
```bash
sudo ./scripts/build_all.sh
```

3. Flash to SD card/eMMC:
```bash
# Replace sdX with your device (be careful!)
xzcat build/ubuntu-22.04-enhanced-rock-5b-plus.img.xz | sudo dd of=/dev/sdX bs=4M status=progress
```

4. Boot Rock 5B Plus with the new image

## Detailed Build Process

### Step 1: Automated Build (Recommended)

The easiest way to build and package everything is using the automated build script:

```bash
sudo ./scripts/build_all.sh
```

This will:
1. Download the Ubuntu image
2. Set up the build environment
3. Build the kernel
4. Create the kernel package
5. Modify the image
6. Generate the final enhanced image

The final image will be available at: `build/ubuntu-22.04-enhanced-rock-5b-plus.img.xz`

### Step 2: Manual Build (Alternative)

If you prefer to build step by step:

1. Prepare environment:
```bash
sudo ./scripts/prepare_environment.sh
```

2. Build kernel:
```bash
sudo ./scripts/build_kernel.sh
```

3. Modify image:
```bash
sudo ./scripts/modify_image.sh
```

## Verification and Testing

### Installation Verification

Run the verification script:
```bash
sudo ./scripts/verify_installation.sh
```

This will check:
- GPU driver status
- Logging system
- Power monitoring
- Crash reporting
- All service states

### Quick Manual Checks

Check GPU driver:
```bash
lsmod | grep -E 'mali|bifrost_kbase'
```

View kernel logs:
```bash
tail -f /var/log/kernel/kernel.log
```

Monitor power readings:
```bash
watch -n 1 'cat /sys/class/power_supply/rock5b_power/voltage_now; cat /sys/class/power_supply/rock5b_power/current_now'
```

Check crash reporter:
```bash
cat /proc/rock5b_crash/status
```

### Comprehensive Testing

#### Test 1: Error Detection
```bash
cd scripts/analysis
python kernel_log_analyzer.py
```
**Expected**: Rich console output with error categorization

#### Test 2: Build Monitoring
```bash
cd scripts/monitoring
python build_monitor.py
```
**Expected**: Real-time build progress with completion report

#### Test 3: Configuration Management
```bash
cd scripts/utils
python kernel_config.py
```
**Expected**: Kernel validation and config backup

### Interactive Demo Scenarios

#### Demo 1: Error Simulation
```bash
cd scripts/analysis
python -c "
from kernel_log_analyzer import KernelLogAnalyzer
analyzer = KernelLogAnalyzer()
errors = [
    'Kernel panic: unable to mount root filesystem',
    'rk3588-pcie: PCIe link training failed',
    'mali-gpu: GPU fault detected',
    'thermal: Critical temperature reached on RK3588'
]
for error in errors:
    criticality, pattern = analyzer.analyze_log_line(error)
    analyzer.log_error(error, criticality, {'board': 'radxa-rock5b+'})
    print(f'Detected: {criticality.upper()} - {error}')
"
```

#### Demo 2: Log Analysis
```bash
# View generated logs
cat logs/critical.log
cat logs/error.log
cat logs/warning.log
```

#### Demo 3: Build Performance
```bash
cd scripts/monitoring
python build_monitor.py
# Watch real-time build progress and final report
```

## Service Control

Restart services if needed:
```bash
sudo systemctl restart kernel-logger
sudo systemctl restart power-monitor
sudo systemctl restart crash-reporter
```

## Performance Testing

### Accuracy Test
```bash
cd scripts/analysis
python -c "
from kernel_log_analyzer import KernelLogAnalyzer
import time
analyzer = KernelLogAnalyzer()
test_cases = [
    ('Kernel panic: unable to mount root filesystem', 'critical'),
    ('ERROR: Failed to load module', 'error'),
    ('WARNING: Deprecated API', 'warning'),
    ('rk3588-pcie: PCIe link training failed', 'critical')
]
start = time.time()
correct = sum(1 for error, expected in test_cases 
             if analyzer.analyze_log_line(error)[0] == expected)
accuracy = (correct / len(test_cases)) * 100
duration = time.time() - start
print(f'Accuracy: {accuracy:.1f}% ({correct}/{len(test_cases)})')
print(f'Speed: {len(test_cases)/duration:.1f} patterns/second')
"
```

## Troubleshooting

### Need Help?

1. Check service logs:
   ```bash
   journalctl -u kernel-logger
   journalctl -u power-monitor
   journalctl -u crash-reporter
   ```

2. Run verification script for diagnostics

3. Check for common issues:
   - GPU driver not loading: Check kernel modules
   - Power monitoring not working: Verify sysfs paths
   - Logging system errors: Check permissions and disk space
