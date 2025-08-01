# Rock 5B Plus Enhanced Kernel Quick Start Guide

## Build and Install

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

## Verify Installation

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

## Quick Manual Checks

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

## Service Control

Restart services if needed:
```bash
sudo systemctl restart kernel-logger
sudo systemctl restart power-monitor
sudo systemctl restart crash-reporter
```

## Need Help?

1. Check [INSTRUCTIONS.md](INSTRUCTIONS.md) for detailed documentation
2. Run verification script for diagnostics
3. Check service logs:
   ```bash
   journalctl -u kernel-logger
   journalctl -u power-monitor
   journalctl -u crash-reporter