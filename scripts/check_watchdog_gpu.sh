#!/bin/bash

# Rock 5B+ Watchdog and GPU Status Check Script
# Run this on the board to verify and start systems

echo "🔍 Rock 5B+ System Status Check"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Some checks require root privileges. Run with sudo for full access."
    echo ""
fi

echo "📊 1. Watchdog Status Check"
echo "---------------------------"

# Check watchdog kernel module
echo "🔧 Watchdog kernel module:"
if lsmod | grep -q watchdog; then
    echo "✅ Watchdog module loaded"
    lsmod | grep watchdog
else
    echo "❌ Watchdog module not loaded"
    echo "   Loading watchdog module..."
    sudo modprobe watchdog
fi

# Check watchdog device
echo ""
echo "🔧 Watchdog device:"
if [ -e /dev/watchdog ]; then
    echo "✅ Watchdog device exists: /dev/watchdog"
    ls -la /dev/watchdog
else
    echo "❌ Watchdog device not found"
fi

# Check watchdog sysfs
echo ""
echo "🔧 Watchdog sysfs:"
if [ -d /sys/class/watchdog ]; then
    echo "✅ Watchdog sysfs exists"
    ls -la /sys/class/watchdog/
    if [ -f /sys/class/watchdog/watchdog0/timeout ]; then
        echo "   Timeout: $(cat /sys/class/watchdog/watchdog0/timeout)s"
    fi
    if [ -f /sys/class/watchdog/watchdog0/status ]; then
        echo "   Status: $(cat /sys/class/watchdog/watchdog0/status)"
    fi
else
    echo "❌ Watchdog sysfs not found"
fi

# Check watchdog service
echo ""
echo "🔧 Watchdog service:"
if systemctl is-active --quiet watchdog; then
    echo "✅ Watchdog service is running"
    systemctl status watchdog --no-pager -l
else
    echo "❌ Watchdog service not running"
    echo "   Starting watchdog service..."
    sudo systemctl start watchdog
    sudo systemctl enable watchdog
fi

echo ""
echo "🎮 2. GPU Status Check"
echo "----------------------"

# Check Mali GPU driver
echo "🔧 Mali GPU driver:"
if lsmod | grep -q mali; then
    echo "✅ Mali GPU driver loaded"
    lsmod | grep mali
else
    echo "❌ Mali GPU driver not loaded"
    echo "   Loading Mali driver..."
    sudo modprobe mali
fi

# Check GPU device
echo ""
echo "🔧 GPU device:"
if [ -e /dev/mali0 ]; then
    echo "✅ Mali GPU device exists: /dev/mali0"
    ls -la /dev/mali0
else
    echo "❌ Mali GPU device not found"
fi

# Check GPU sysfs
echo ""
echo "🔧 GPU sysfs:"
if [ -d /sys/class/devfreq/fb000000.gpu ]; then
    echo "✅ GPU sysfs exists"
    echo "   Current frequency: $(cat /sys/class/devfreq/fb000000.gpu/cur_freq) Hz"
    echo "   Available frequencies:"
    cat /sys/class/devfreq/fb000000.gpu/available_frequencies
else
    echo "❌ GPU sysfs not found"
fi

# Check OpenCL
echo ""
echo "🔧 OpenCL support:"
if command -v clinfo >/dev/null 2>&1; then
    echo "✅ clinfo available"
    echo "   OpenCL platforms:"
    clinfo | grep "Platform Name" || echo "   No OpenCL platforms found"
else
    echo "❌ clinfo not available"
    echo "   Installing clinfo..."
    sudo apt update && sudo apt install -y clinfo
fi

# Check Vulkan
echo ""
echo "🔧 Vulkan support:"
if command -v vulkaninfo >/dev/null 2>&1; then
    echo "✅ vulkaninfo available"
    echo "   Vulkan devices:"
    vulkaninfo --summary 2>/dev/null | grep "GPU" || echo "   No Vulkan devices found"
else
    echo "❌ vulkaninfo not available"
    echo "   Installing vulkan-tools..."
    sudo apt update && sudo apt install -y vulkan-tools
fi

echo ""
echo "🔧 3. System Services Check"
echo "---------------------------"

# Check YSuite services
echo "🔧 YSuite services:"
services=("ylogd" "ypowerd" "ycrashd")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "✅ $service is running"
    else
        echo "❌ $service not running"
        echo "   Starting $service..."
        sudo systemctl start "$service" 2>/dev/null || echo "   Service not found"
    fi
done

echo ""
echo "🔧 4. Hardware Monitoring"
echo "-------------------------"

# Check temperature sensors
echo "🔧 Temperature sensors:"
for i in {0..9}; do
    if [ -f "/sys/class/thermal/thermal_zone$i/temp" ]; then
        temp=$(cat "/sys/class/thermal/thermal_zone$i/temp")
        temp_c=$(echo "scale=1; $temp/1000" | bc -l 2>/dev/null || echo "N/A")
        echo "   Thermal zone $i: ${temp_c}°C"
    fi
done

# Check fan
echo ""
echo "🔧 Fan status:"
fan_paths=(
    "/sys/class/thermal/cooling_device0/cur_state"
    "/sys/class/thermal/cooling_device1/cur_state"
    "/sys/class/hwmon/hwmon*/fan1_input"
    "/sys/class/hwmon/hwmon*/pwm1"
)

fan_found=false
for path in "${fan_paths[@]}"; do
    if [ -f "$path" ]; then
        fan_value=$(cat "$path" 2>/dev/null)
        if [ "$fan_value" -gt 0 ] 2>/dev/null; then
            echo "✅ Fan running: $path = $fan_value"
            fan_found=true
            break
        fi
    fi
done

if [ "$fan_found" = false ]; then
    echo "❌ No active fan detected"
fi

echo ""
echo "🔧 5. Power Status"
echo "------------------"

# Check power supply
echo "🔧 Power supply:"
if [ -d "/sys/class/power_supply" ]; then
    for supply in /sys/class/power_supply/*; do
        if [ -d "$supply" ]; then
            supply_name=$(basename "$supply")
            if [ -f "$supply/online" ]; then
                online=$(cat "$supply/online")
                if [ "$online" -eq 1 ]; then
                    echo "✅ $supply_name: Online"
                    if [ -f "$supply/voltage_now" ]; then
                        voltage=$(cat "$supply/voltage_now")
                        voltage_v=$(echo "scale=2; $voltage/1000000" | bc -l 2>/dev/null || echo "N/A")
                        echo "   Voltage: ${voltage_v}V"
                    fi
                    if [ -f "$supply/current_now" ]; then
                        current=$(cat "$supply/current_now")
                        current_ma=$(echo "scale=1; $current/1000" | bc -l 2>/dev/null || echo "N/A")
                        echo "   Current: ${current_ma}mA"
                    fi
                else
                    echo "❌ $supply_name: Offline"
                fi
            fi
        fi
    done
else
    echo "❌ Power supply sysfs not found"
fi

echo ""
echo "🎯 6. Quick YSuite Test"
echo "----------------------"

# Test YSuite commands
if command -v ytop >/dev/null 2>&1; then
    echo "✅ ytop available"
    echo "   Running quick test..."
    timeout 5s ytop 2>/dev/null && echo "   ✅ ytop working" || echo "   ❌ ytop failed"
else
    echo "❌ ytop not available"
fi

if command -v ylog >/dev/null 2>&1; then
    echo "✅ ylog available"
    echo "   Running quick test..."
    timeout 3s ylog 2>/dev/null && echo "   ✅ ylog working" || echo "   ❌ ylog failed"
else
    echo "❌ ylog not available"
fi

echo ""
echo "✅ System check complete!"
echo "=================================="
echo ""
echo "💡 Next steps:"
echo "1. Run 'ytop' for real-time monitoring"
echo "2. Run 'ylog' to check system logs"
echo "3. Run 'ycrash' to check for crashes"
echo "4. Run 'ypower' to monitor power"
echo "5. Run 'yhelp' for all available commands"



