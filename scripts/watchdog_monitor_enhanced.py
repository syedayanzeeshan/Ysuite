#!/usr/bin/env python3
"""
Enhanced Watchdog Monitor for Rock 5B+
Monitors CPU, RAM usage and WiFi connectivity
- Triggers system reboot if CPU/RAM exceeds 80% for 15 seconds
- Restarts USB ports and network adapters if WiFi unavailable for 60 seconds
"""

import psutil
import time
import subprocess
import logging
import os
import glob
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/watchdog_monitor.log'),
        logging.StreamHandler()
    ]
)

class EnhancedWatchdogMonitor:
    def __init__(self, cpu_threshold=80, ram_threshold=80, duration_threshold=15, wifi_timeout=60):
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold
        self.duration_threshold = duration_threshold
        self.wifi_timeout = wifi_timeout
        self.cpu_high_start = None
        self.ram_high_start = None
        self.wifi_down_start = None
        self.last_log_time = 0
        
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    def get_ram_usage(self):
        """Get current RAM usage percentage"""
        memory = psutil.virtual_memory()
        return memory.percent
    
    def check_wifi_connectivity(self):
        """Check if WiFi is connected and working"""
        try:
            # Check for WiFi interfaces
            wifi_interfaces = []
            for interface in psutil.net_if_addrs():
                if interface.startswith('wl') or interface.startswith('wlan'):
                    wifi_interfaces.append(interface)
            
            if not wifi_interfaces:
                return False
            
            # Test connectivity with ping
            for interface in wifi_interfaces:
                try:
                    # Get gateway for this interface
                    result = subprocess.run(['ip', 'route', 'show', 'dev', interface], 
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0 and 'default' in result.stdout:
                        # Try to ping gateway
                        gateway = result.stdout.split()[2]
                        ping_result = subprocess.run(['ping', '-c', '1', '-W', '3', gateway], 
                                                   capture_output=True, timeout=5)
                        if ping_result.returncode == 0:
                            return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def restart_modem_usb(self):
        """Restart USB ports and network adapters"""
        try:
            logging.warning("WiFi connectivity lost. Restarting USB ports and network adapters...")
            
            # Find USB devices
            usb_devices = []
            try:
                result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'modem' in line.lower() or 'network' in line.lower() or 'wifi' in line.lower():
                            usb_devices.append(line.split()[5])
            except:
                pass
            
            # Unbind and rebind USB devices
            for device in usb_devices:
                try:
                    # Find device in sysfs
                    device_path = f"/sys/bus/usb/devices/{device}"
                    if os.path.exists(device_path):
                        # Unbind
                        with open(f"{device_path}/driver/unbind", 'w') as f:
                            f.write(device)
                        time.sleep(2)
                        # Rebind
                        with open(f"{device_path}/driver/bind", 'w') as f:
                            f.write(device)
                        logging.info(f"Restarted USB device: {device}")
                except:
                    continue
            
            # Restart network interfaces
            try:
                wifi_interfaces = []
                for interface in psutil.net_if_addrs():
                    if interface.startswith('wl') or interface.startswith('wlan'):
                        wifi_interfaces.append(interface)
                
                for interface in wifi_interfaces:
                    try:
                        subprocess.run(['ip', 'link', 'set', interface, 'down'], timeout=5)
                        time.sleep(2)
                        subprocess.run(['ip', 'link', 'set', interface, 'up'], timeout=5)
                        logging.info(f"Restarted network interface: {interface}")
                    except:
                        continue
            except:
                pass
            
            logging.info("USB ports and network adapters restart completed")
            
        except Exception as e:
            logging.error(f"Error restarting USB/network: {e}")
    
    def log_status(self, cpu_usage, ram_usage, wifi_status, cpu_duration=None, ram_duration=None, wifi_duration=None):
        """Log current status"""
        current_time = time.time()
        if current_time - self.last_log_time >= 5:  # Log every 5 seconds max
            status_msg = f"CPU: {cpu_usage:.1f}%, RAM: {ram_usage:.1f}%, WiFi: {'OK' if wifi_status else 'DOWN'}"
            if cpu_duration:
                status_msg += f" (CPU high for {cpu_duration:.1f}s)"
            if ram_duration:
                status_msg += f" (RAM high for {ram_duration:.1f}s)"
            if wifi_duration:
                status_msg += f" (WiFi down for {wifi_duration:.1f}s)"
            logging.info(status_msg)
            self.last_log_time = current_time
    
    def check_and_trigger(self):
        """Check CPU, RAM, and WiFi and trigger actions if needed"""
        cpu_usage = self.get_cpu_usage()
        ram_usage = self.get_ram_usage()
        wifi_status = self.check_wifi_connectivity()
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
        
        # Check WiFi connectivity
        if not wifi_status:
            if self.wifi_down_start is None:
                self.wifi_down_start = current_time
                logging.warning("WiFi connectivity lost")
            else:
                wifi_duration = current_time - self.wifi_down_start
                if wifi_duration >= self.wifi_timeout:
                    logging.critical(f"WiFi unavailable for {wifi_duration:.1f} seconds. Restarting USB/network!")
                    self.restart_modem_usb()
                    self.wifi_down_start = None  # Reset timer
                    return
        else:
            if self.wifi_down_start is not None:
                logging.info("WiFi connectivity restored")
                self.wifi_down_start = None
        
        # Calculate durations for logging
        cpu_duration = None
        ram_duration = None
        wifi_duration = None
        if self.cpu_high_start:
            cpu_duration = current_time - self.cpu_high_start
        if self.ram_high_start:
            ram_duration = current_time - self.ram_high_start
        if self.wifi_down_start:
            wifi_duration = current_time - self.wifi_down_start
        
        self.log_status(cpu_usage, ram_usage, wifi_status, cpu_duration, ram_duration, wifi_duration)
    
    def trigger_reboot(self, reason):
        """Trigger system reboot"""
        logging.critical(f"WATCHDOG TRIGGERED: {reason}")
        logging.critical("System will reboot in 5 seconds...")
        
        # Write to syslog
        subprocess.run(['logger', f'WATCHDOG: {reason} - System rebooting'], check=False)
        
        # Wait 5 seconds then reboot
        time.sleep(5)
        subprocess.run(['reboot'], check=False)
    
    def run(self):
        """Main monitoring loop"""
        logging.info("Enhanced Watchdog Monitor started")
        logging.info(f"Thresholds: CPU={self.cpu_threshold}%, RAM={self.ram_threshold}%, Duration={self.duration_threshold}s, WiFi Timeout={self.wifi_timeout}s")
        
        try:
            while True:
                self.check_and_trigger()
                time.sleep(1)  # Check every second
        except KeyboardInterrupt:
            logging.info("Enhanced Watchdog Monitor stopped by user")
        except Exception as e:
            logging.error(f"Enhanced Watchdog Monitor error: {e}")
            raise

if __name__ == "__main__":
    monitor = EnhancedWatchdogMonitor(
        cpu_threshold=80, 
        ram_threshold=80, 
        duration_threshold=15,
        wifi_timeout=60
    )
    monitor.run()
