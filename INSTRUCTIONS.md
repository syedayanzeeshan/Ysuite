# Rock 5B Plus Enhanced Kernel Build Instructions

This document provides step-by-step instructions for building and deploying the enhanced kernel for Rock 5B Plus, which includes GPU driver switching, advanced logging, power monitoring, and crash reporting.

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

## Step 1: Clone Repository

```bash
git clone https://github.com/your-repo/rock5b-kernel-enhancement.git
cd rock5b-kernel-enhancement
```

## Step 2: Automated Build (Recommended)

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

## Step 3: Manual Build (Alternative)

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

## Step 4: Installation

1. Flash the image to SD card or eMMC:
```bash
xzcat build/ubuntu-22.04-enhanced-rock-5b-plus.img.xz | sudo dd of=/dev/sdX bs=4M status=progress
```
Replace `/dev/sdX` with your actual device (be careful to use the correct device!)

2. Boot the Rock 5B Plus with the new image

## Step 5: Verification

After booting, verify the installation:

1. Check GPU driver:
```bash
lsmod | grep -E 'mali|bifrost_kbase'
```
Should show Mali driver loaded

2. Check logging system:
```bash
ls -l /var/log/kernel/
tail -f /var/log/kernel/kernel.log
```

3. Check power monitoring:
```bash
cat /sys/class/power_supply/rock5b_power/voltage_now
cat /sys/class/power_supply/rock5b_power/current_now
```

4. Check crash reporter:
```bash
ls -l /proc/rock5b_crash/
cat /proc/rock5b_crash/status
```

## Log File Locations

- Kernel logs: `/var/log/kernel/kernel.log`
- Error logs: `/var/log/kernel/errors.log`
- Build errors: `/var/log/kernel/build_errors.log`
- Runtime errors: `/var/log/kernel/runtime_errors.log`
- Power monitoring: `/var/log/kernel/power.log`
- Crash reports: `/var/log/kernel/crashes/`

## Troubleshooting

1. If GPU driver doesn't switch:
   - Check `/boot/extlinux/extlinux.conf` for correct kernel entry
   - Verify device tree overlay is applied: `dtoverlay -l`

2. If logging system isn't working:
   - Check service status: `systemctl status kernel-logger`
   - Verify permissions on log directory
   - Check dmesg for kernel module loading errors

3. If power monitoring fails:
   - Verify ADC channels are configured correctly
   - Check service status: `systemctl status power-monitor`
   - Verify sysfs entries exist

4. If crash reporting isn't working:
   - Check service status: `systemctl status crash-reporter`
   - Verify proc entries exist
   - Check permissions on crash report directory

## Manual GPU Driver Switch

If you need to manually switch GPU drivers:

1. Switch to Mali:
```bash
sudo rm /etc/modprobe.d/panfrost.conf
echo "blacklist panfrost" | sudo tee /etc/modprobe.d/panfrost.conf
sudo update-initramfs -u
```

2. Switch to Panfrost:
```bash
sudo rm /etc/modprobe.d/panfrost.conf
echo "blacklist mali" | sudo tee /etc/modprobe.d/mali.conf
sudo update-initramfs -u
```

## Service Management

All services can be managed using systemd:

```bash
# Kernel Logger
sudo systemctl status kernel-logger
sudo systemctl restart kernel-logger

# Power Monitor
sudo systemctl status power-monitor
sudo systemctl restart power-monitor

# Crash Reporter
sudo systemctl status crash-reporter
sudo systemctl restart crash-reporter
```

## Log Rotation

Logs are automatically rotated based on size:
- Maximum size per log: 100MB
- Number of rotations: 5

You can modify these settings in `/etc/environment`

## Support

If you encounter any issues:
1. Check the relevant log files
2. Verify service status
3. Check kernel messages: `dmesg | grep -E 'rock5b|mali|panfrost'`
4. Submit an issue with relevant logs and system information