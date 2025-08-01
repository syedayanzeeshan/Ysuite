#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

echo_error() {
    echo -e "${RED}[✗]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

echo_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo_error "Please run as root"
    exit 1
fi

# Check GPU Driver
echo_header "Checking GPU Driver"
if lsmod | grep -q "mali\|bifrost_kbase"; then
    echo_success "Mali GPU driver is loaded"
    GPU_INFO=$(lsmod | grep -E "mali|bifrost_kbase")
    echo "$GPU_INFO"
else
    echo_error "Mali GPU driver not found"
    if lsmod | grep -q "panfrost"; then
        echo_error "Panfrost driver is still active"
    fi
fi

# Check Kernel Logger
echo_header "Checking Kernel Logger"
if systemctl is-active --quiet kernel-logger; then
    echo_success "Kernel logger service is running"
else
    echo_error "Kernel logger service is not running"
fi

if [ -f "/var/log/kernel/kernel.log" ]; then
    echo_success "Kernel log file exists"
    LOG_SIZE=$(du -h /var/log/kernel/kernel.log | cut -f1)
    echo "Log size: $LOG_SIZE"
else
    echo_error "Kernel log file not found"
fi

# Check Power Monitor
echo_header "Checking Power Monitor"
if systemctl is-active --quiet power-monitor; then
    echo_success "Power monitor service is running"
else
    echo_error "Power monitor service is not running"
fi

VOLTAGE_PATH="/sys/class/power_supply/rock5b_power/voltage_now"
CURRENT_PATH="/sys/class/power_supply/rock5b_power/current_now"

if [ -f "$VOLTAGE_PATH" ]; then
    VOLTAGE=$(cat "$VOLTAGE_PATH")
    echo_success "Voltage reading: $VOLTAGE µV"
else
    echo_error "Voltage monitoring not available"
fi

if [ -f "$CURRENT_PATH" ]; then
    CURRENT=$(cat "$CURRENT_PATH")
    echo_success "Current reading: $CURRENT µA"
else
    echo_error "Current monitoring not available"
fi

# Check Crash Reporter
echo_header "Checking Crash Reporter"
if systemctl is-active --quiet crash-reporter; then
    echo_success "Crash reporter service is running"
else
    echo_error "Crash reporter service is not running"
fi

if [ -d "/proc/rock5b_crash" ]; then
    echo_success "Crash reporter proc interface exists"
    if [ -f "/proc/rock5b_crash/status" ]; then
        STATUS=$(cat /proc/rock5b_crash/status)
        echo "Crash reporter status:"
        echo "$STATUS"
    fi
else
    echo_error "Crash reporter proc interface not found"
fi

# Check Log Files
echo_header "Checking Log Files"
LOG_FILES=(
    "/var/log/kernel/kernel.log"
    "/var/log/kernel/errors.log"
    "/var/log/kernel/build_errors.log"
    "/var/log/kernel/runtime_errors.log"
    "/var/log/kernel/power.log"
)

for log in "${LOG_FILES[@]}"; do
    if [ -f "$log" ]; then
        SIZE=$(du -h "$log" | cut -f1)
        echo_success "$(basename "$log") exists (Size: $SIZE)"
    else
        echo_error "$(basename "$log") not found"
    fi
done

# Check Crash Reports Directory
if [ -d "/var/log/kernel/crashes" ]; then
    echo_success "Crash reports directory exists"
    CRASH_COUNT=$(ls -1 /var/log/kernel/crashes/crash_report_*.json 2>/dev/null | wc -l)
    if [ $CRASH_COUNT -gt 0 ]; then
        echo_warning "Found $CRASH_COUNT crash report(s)"
    else
        echo_success "No crash reports found (system stable)"
    fi
else
    echo_error "Crash reports directory not found"
fi

# Summary
echo_header "Installation Verification Summary"
echo "Please check the above results for any errors marked with [✗]"
echo "For detailed troubleshooting, refer to INSTRUCTIONS.md"