#!/usr/bin/env python3
"""
Watchdog Monitor for Rock 5B+
Monitors CPU and RAM usage and triggers system reboot if either exceeds 80% for more than 15 seconds
"""

import psutil
import time
import subprocess
import logging
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

class WatchdogMonitor:
    def __init__(self, cpu_threshold=80, ram_threshold=80, duration_threshold=15):
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold
        self.duration_threshold = duration_threshold
        self.cpu_high_start = None
        self.ram_high_start = None
        self.last_log_time = 0
        
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    def get_ram_usage(self):
        """Get current RAM usage percentage"""
        memory = psutil.virtual_memory()
        return memory.percent
    
    def log_status(self, cpu_usage, ram_usage, cpu_duration=None, ram_duration=None):
        """Log current status"""
        current_time = time.time()
        if current_time - self.last_log_time >= 5:  # Log every 5 seconds max
            status_msg = f"CPU: {cpu_usage:.1f}%, RAM: {ram_usage:.1f}%"
            if cpu_duration:
                status_msg += f" (CPU high for {cpu_duration:.1f}s)"
            if ram_duration:
                status_msg += f" (RAM high for {ram_duration:.1f}s)"
            logging.info(status_msg)
            self.last_log_time = current_time
    
    def check_and_trigger(self):
        """Check CPU and RAM usage and trigger reboot if needed"""
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
        logging.info("Watchdog Monitor started")
        logging.info(f"Thresholds: CPU={self.cpu_threshold}%, RAM={self.ram_threshold}%, Duration={self.duration_threshold}s")
        
        try:
            while True:
                self.check_and_trigger()
                time.sleep(1)  # Check every second
        except KeyboardInterrupt:
            logging.info("Watchdog Monitor stopped by user")
        except Exception as e:
            logging.error(f"Watchdog Monitor error: {e}")
            raise

if __name__ == "__main__":
    monitor = WatchdogMonitor(cpu_threshold=80, ram_threshold=80, duration_threshold=15)
    monitor.run()
