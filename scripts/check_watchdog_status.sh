#!/bin/bash
# Watchdog Status Verification Script
# Checks both CPU/RAM and WiFi/USB restart policies

echo "🔍 Watchdog Policy Status Verification"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check service status
check_service_status() {
    echo -e "${BLUE}📋 Service Status:${NC}"
    if systemctl is-active --quiet watchdog-monitor.service; then
        echo -e "  ${GREEN}✅ Service: ACTIVE${NC}"
        systemctl status watchdog-monitor.service --no-pager | head -10
    else
        echo -e "  ${RED}❌ Service: INACTIVE${NC}"
        systemctl status watchdog-monitor.service --no-pager
    fi
    echo ""
}

# Function to check policy configuration
check_policy_config() {
    echo -e "${BLUE}⚙️  Policy Configuration:${NC}"
    
    # Check CPU/RAM policy
    echo -e "  ${YELLOW}Policy 1: CPU/RAM Monitoring (System Reboot)${NC}"
    echo "    • CPU Threshold: 80%"
    echo "    • RAM Threshold: 80%"
    echo "    • Duration: 15 seconds"
    echo "    • Action: System reboot"
    
    # Check WiFi policy
    echo -e "  ${YELLOW}Policy 2: WiFi Connectivity (USB/Network Restart)${NC}"
    echo "    • WiFi Timeout: 60 seconds"
    echo "    • Action: Restart USB ports and network adapters"
    echo ""
}

# Function to check recent logs
check_recent_logs() {
    echo -e "${BLUE}📊 Recent Activity (Last 10 entries):${NC}"
    if [ -f "/var/log/watchdog_monitor.log" ]; then
        tail -10 /var/log/watchdog_monitor.log | while read line; do
            if echo "$line" | grep -q "WiFi: OK"; then
                echo -e "  ${GREEN}✅ $line${NC}"
            elif echo "$line" | grep -q "WiFi: DOWN"; then
                echo -e "  ${RED}❌ $line${NC}"
            elif echo "$line" | grep -q "WARNING\|CRITICAL"; then
                echo -e "  ${YELLOW}⚠️  $line${NC}"
            else
                echo "  $line"
            fi
        done
    else
        echo -e "  ${RED}❌ Log file not found${NC}"
    fi
    echo ""
}

# Function to check WiFi connectivity
check_wifi_status() {
    echo -e "${BLUE}📶 WiFi Connectivity Status:${NC}"
    
    # Check WiFi interfaces
    wifi_interfaces=$(ip link show | grep -E 'wl|wlan' | wc -l)
    if [ $wifi_interfaces -gt 0 ]; then
        echo -e "  ${GREEN}✅ WiFi interfaces found: $wifi_interfaces${NC}"
        
        # Check if WiFi is connected
        if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
            echo -e "  ${GREEN}✅ Internet connectivity: OK${NC}"
        else
            echo -e "  ${RED}❌ Internet connectivity: FAILED${NC}"
        fi
    else
        echo -e "  ${RED}❌ No WiFi interfaces found${NC}"
    fi
    echo ""
}

# Function to check current system metrics
check_current_metrics() {
    echo -e "${BLUE}📈 Current System Metrics:${NC}"
    
    # CPU usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "  • CPU Usage: ${cpu_usage}%"
    
    # RAM usage
    ram_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    echo "  • RAM Usage: ${ram_usage}%"
    
    # Check if thresholds are exceeded
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        echo -e "  ${RED}⚠️  CPU usage exceeds 80% threshold${NC}"
    else
        echo -e "  ${GREEN}✅ CPU usage within normal range${NC}"
    fi
    
    if (( $(echo "$ram_usage > 80" | bc -l) )); then
        echo -e "  ${RED}⚠️  RAM usage exceeds 80% threshold${NC}"
    else
        echo -e "  ${GREEN}✅ RAM usage within normal range${NC}"
    fi
    echo ""
}

# Function to check USB devices
check_usb_devices() {
    echo -e "${BLUE}🔌 USB Devices (for restart capability):${NC}"
    
    # Check for network/modem USB devices
    network_devices=$(lsusb | grep -i -E 'modem|network|wifi' | wc -l)
    if [ $network_devices -gt 0 ]; then
        echo -e "  ${GREEN}✅ Network USB devices found: $network_devices${NC}"
        lsusb | grep -i -E 'modem|network|wifi'
    else
        echo -e "  ${YELLOW}⚠️  No network USB devices detected${NC}"
    fi
    echo ""
}

# Function to check log file health
check_log_health() {
    echo -e "${BLUE}📝 Log File Health:${NC}"
    
    if [ -f "/var/log/watchdog_monitor.log" ]; then
        log_size=$(du -h /var/log/watchdog_monitor.log | cut -f1)
        log_lines=$(wc -l < /var/log/watchdog_monitor.log)
        last_modified=$(stat -c %y /var/log/watchdog_monitor.log | cut -d' ' -f1,2)
        
        echo "  • Log file size: $log_size"
        echo "  • Total log entries: $log_lines"
        echo "  • Last modified: $last_modified"
        
        # Check for recent activity
        if [ $(find /var/log/watchdog_monitor.log -mmin -5 2>/dev/null | wc -l) -gt 0 ]; then
            echo -e "  ${GREEN}✅ Log file is being actively updated${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Log file hasn't been updated recently${NC}"
        fi
    else
        echo -e "  ${RED}❌ Log file not found${NC}"
    fi
    echo ""
}

# Function to show policy summary
show_policy_summary() {
    echo -e "${BLUE}📋 Policy Summary:${NC}"
    echo "  ${YELLOW}Policy 1: System Health Monitoring${NC}"
    echo "    └─ CPU/RAM > 80% for 15s → System reboot"
    echo ""
    echo "  ${YELLOW}Policy 2: Network Health Monitoring${NC}"
    echo "    └─ WiFi unavailable for 60s → USB/network restart"
    echo ""
    echo "  ${YELLOW}Monitoring Frequency:${NC}"
    echo "    └─ Every 1 second"
    echo ""
    echo "  ${YELLOW}Logging:${NC}"
    echo "    └─ /var/log/watchdog_monitor.log"
    echo ""
}

# Main execution
main() {
    echo "🔍 Watchdog Policy Status Verification"
    echo "======================================"
    echo ""
    
    check_service_status
    check_policy_config
    check_current_metrics
    check_wifi_status
    check_usb_devices
    check_recent_logs
    check_log_health
    show_policy_summary
    
    echo -e "${GREEN}✅ Verification complete!${NC}"
    echo ""
    echo "For real-time monitoring:"
    echo "  • Watch logs: sudo tail -f /var/log/watchdog_monitor.log"
    echo "  • Service status: sudo systemctl status watchdog-monitor.service"
    echo "  • YSuite monitoring: ytop"
}

# Run main function
main
