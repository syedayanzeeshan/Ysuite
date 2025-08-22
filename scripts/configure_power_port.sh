#!/bin/bash

# Configure Power Type-C Port for PD Sink Mode
# This script helps configure the Rock 5B+ power Type-C port for USB PD

echo "=== Rock 5B+ Power Type-C Port Configuration ==="
echo "This script configures the power Type-C port for USB PD sink mode"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "1. Checking current Type-C port status..."
echo "   Power Role: $(cat /sys/class/typec/port0/power_role)"
echo "   Data Role: $(cat /sys/class/typec/port0/data_role)"
echo "   Preferred Role: $(cat /sys/class/typec/port0/preferred_role)"
echo "   Power Operation Mode: $(cat /sys/class/typec/port0/power_operation_mode)"
echo

echo "2. Checking USB PD capabilities..."
if [ -d "/sys/class/typec/port0/usb_power_delivery" ]; then
    echo "   USB PD Revision: $(cat /sys/class/typec/port0/usb_power_delivery_revision)"
    echo "   Sink Capabilities:"
    for cap in /sys/class/typec/port0/usb_power_delivery/sink-capabilities/*/; do
        if [ -d "$cap" ]; then
            voltage=$(cat "$cap/voltage" 2>/dev/null || echo "N/A")
            current=$(cat "$cap/operational_current" 2>/dev/null || echo "N/A")
            echo "     - ${voltage}mV / ${current}mA"
        fi
    done
else
    echo "   USB PD not available"
fi
echo

echo "3. Checking power supply status..."
if [ -d "/sys/bus/i2c/devices/4-0022/power_supply" ]; then
    for psy in /sys/bus/i2c/devices/4-0022/power_supply/*/; do
        if [ -d "$psy" ]; then
            name=$(basename "$psy")
            online=$(cat "$psy/online" 2>/dev/null || echo "N/A")
            echo "   $name: online=$online"
        fi
    done
else
    echo "   Power supply not found"
fi
echo

echo "4. Checking current sensors..."
if [ -f "/sys/class/hwmon/hwmon7/curr1_input" ]; then
    current=$(cat /sys/class/hwmon/hwmon7/curr1_input)
    echo "   hwmon7 current: ${current}mA"
else
    echo "   Current sensor not found"
fi

if [ -f "/sys/class/hwmon/hwmon7/in0_input" ]; then
    voltage=$(cat /sys/class/hwmon/hwmon7/in0_input)
    echo "   hwmon7 voltage: ${voltage}mV"
else
    echo "   Voltage sensor not found"
fi
echo

echo "5. Attempting to configure for PD sink mode..."
echo "   Note: Some settings may require physical disconnect/reconnect"

# Try to set preferred role to sink (may not work while connected)
if [ -w "/sys/class/typec/port0/preferred_role" ]; then
    echo "sink" > /sys/class/typec/port0/preferred_role 2>/dev/null && echo "   ✓ Set preferred role to sink" || echo "   ✗ Could not set preferred role"
else
    echo "   ✗ Cannot write to preferred_role"
fi

# Try to set data role to device (may not work while connected)
if [ -w "/sys/class/typec/port0/data_role" ]; then
    echo "device" > /sys/class/typec/port0/data_role 2>/dev/null && echo "   ✓ Set data role to device" || echo "   ✗ Could not set data role"
else
    echo "   ✗ Cannot write to data_role"
fi
echo

echo "6. Recommendations:"
echo "   - If power port is not working, try the display Type-C port"
echo "   - Physical disconnect/reconnect may be required for PD negotiation"
echo "   - Check if your power adapter supports USB PD"
echo "   - Some power adapters may only work on specific ports"
echo

echo "7. Current YSuite power reading:"
if command -v ytop >/dev/null 2>&1; then
    ytop_power=$(python3 -c "
import sys
sys.path.insert(0, '/usr/local/bin')
exec(open('/usr/local/bin/ysuite').read())
ytop = YTop()
power = ytop.get_accurate_power_readings()
print(f'Voltage: {power[\"voltage_input\"]}V, Current: {power[\"current_input\"]}A, Power: {power[\"power_input\"]}W, Source: {power[\"power_source\"]}')
" 2>/dev/null || echo "YSuite not available")
    echo "   $ytop_power"
else
    echo "   YSuite not available"
fi
echo

echo "Configuration complete!"
echo "If power port still doesn't work, try using the display Type-C port instead."
