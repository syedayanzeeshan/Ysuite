#!/bin/bash
# Watchdog Monitor Setup for Rock 5B+ (Simplified)
# Monitors CPU and RAM usage and triggers reboot if either exceeds 80% for 15+ seconds

set -e

echo "🔧 Setting up Watchdog Monitor for Rock 5B+"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "📁 Creating watchdog monitor script..."
cat > /usr/local/bin/watchdog_monitor.py << 'EOF'
#!/usr/bin/env python3
import psutil
import time
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/watchdog_monitor.log'),
        logging.StreamHandler()
    ]
)

class WatchdogMonitor:
    def __init__(self, cpu_threshold=80, ram_threshold=80, duration_threshold=15):
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold
        self.duration_threshold = duration_threshold
        self.cpu_high_start = None
        self.ram_high_start = None
        self.last_log_time = 0
        
    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)
    
    def get_ram_usage(self):
        memory = psutil.virtual_memory()
        return memory.percent
    
    def log_status(self, cpu_usage, ram_usage, cpu_duration=None, ram_duration=None):
        current_time = time.time()
        if current_time - self.last_log_time >= 5:
            status_msg = f"CPU: {cpu_usage:.1f}%, RAM: {ram_usage:.1f}%"
            if cpu_duration:
                status_msg += f" (CPU high for {cpu_duration:.1f}s)"
            if ram_duration:
                status_msg += f" (RAM high for {ram_duration:.1f}s)"
            logging.info(status_msg)
            self.last_log_time = current_time
    
    def check_and_trigger(self):
        cpu_usage = self.get_cpu_usage()
        ram_usage = self.get_ram_usage()
        current_time = time.time()
        
        # Check CPU usage
        if cpu_usage > self.cpu_threshold:
            if self.cpu_high_start is None:
                self.cpu_high_start = current_time
                logging.warning(f"CPU usage exceeded {self.cpu_threshold}%: {cpu_usage:.1f}%")
            else:
                cpu_duration = current_time - self.cpu_high_start
                if cpu_duration >= self.duration_threshold:
                    logging.critical(f"CPU usage exceeded {self.cpu_threshold}% for {cpu_duration:.1f} seconds. Triggering reboot!")
                    self.trigger_reboot("CPU usage exceeded threshold")
                    return
        else:
            if self.cpu_high_start is not None:
                logging.info(f"CPU usage returned to normal: {cpu_usage:.1f}%")
                self.cpu_high_start = None
        
        # Check RAM usage
        if ram_usage > self.ram_threshold:
            if self.ram_high_start is None:
                self.ram_high_start = current_time
                logging.warning(f"RAM usage exceeded {self.ram_threshold}%: {ram_usage:.1f}%")
            else:
                ram_duration = current_time - self.ram_high_start
                if ram_duration >= self.duration_threshold:
                    logging.critical(f"RAM usage exceeded {self.ram_threshold}% for {ram_duration:.1f} seconds. Triggering reboot!")
                    self.trigger_reboot("RAM usage exceeded threshold")
                    return
        else:
            if self.ram_high_start is not None:
                logging.info(f"RAM usage returned to normal: {ram_usage:.1f}%")
                self.ram_high_start = None
        
        # Calculate durations for logging
        cpu_duration = None
        ram_duration = None
        if self.cpu_high_start:
            cpu_duration = current_time - self.cpu_high_start
        if self.ram_high_start:
            ram_duration = current_time - self.ram_high_start
        
        self.log_status(cpu_usage, ram_usage, cpu_duration, ram_duration)
    
    def trigger_reboot(self, reason):
        logging.critical(f"WATCHDOG TRIGGERED: {reason}")
        logging.critical("System will reboot in 5 seconds...")
        subprocess.run(['logger', f'WATCHDOG: {reason} - System rebooting'], check=False)
        time.sleep(5)
        subprocess.run(['reboot'], check=False)
    
    def run(self):
        logging.info("Watchdog Monitor started")
        logging.info(f"Thresholds: CPU={self.cpu_threshold}%, RAM={self.ram_threshold}%, Duration={self.duration_threshold}s")
        
        try:
            while True:
                self.check_and_trigger()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Watchdog Monitor stopped by user")
        except Exception as e:
            logging.error(f"Watchdog Monitor error: {e}")
            raise

if __name__ == "__main__":
    monitor = WatchdogMonitor(cpu_threshold=80, ram_threshold=80, duration_threshold=15)
    monitor.run()
EOF

chmod +x /usr/local/bin/watchdog_monitor.py

echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/watchdog-monitor.service << 'EOF'
[Unit]
Description=Watchdog Monitor for CPU and RAM Usage
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/watchdog_monitor.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd..."
systemctl daemon-reload

echo "🚀 Enabling and starting watchdog monitor service..."
systemctl enable watchdog-monitor.service
systemctl start watchdog-monitor.service

echo "🗑️ Removing stress test tools..."
rm -f /usr/local/bin/ystress /usr/local/bin/ocl-stress

echo "📊 Checking service status..."
systemctl status watchdog-monitor.service --no-pager

echo ""
echo "✅ Watchdog Monitor setup completed!"
echo ""
echo "📋 Configuration:"
echo "   • CPU threshold: 80%"
echo "   • RAM threshold: 80%"
echo "   • Duration threshold: 15 seconds"
echo "   • Log file: /var/log/watchdog_monitor.log"
echo ""
echo "🔧 Service commands:"
echo "   • Status: systemctl status watchdog-monitor"
echo "   • Stop: systemctl stop watchdog-monitor"
echo "   • Start: systemctl start watchdog-monitor"
echo "   • Restart: systemctl restart watchdog-monitor"
echo "   • Logs: journalctl -u watchdog-monitor -f"
echo ""
echo "⚠️  WARNING: This will reboot the system if CPU or RAM usage exceeds 80% for 15+ seconds!"
echo "   Stress test tools have been removed to prevent accidental triggers."
