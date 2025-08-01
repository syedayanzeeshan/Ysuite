#!/usr/bin/env python3

import os
import time
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

class PowerMonitor:
    def __init__(self):
        # Paths for voltage and current readings in sysfs
        self.voltage_path = "/sys/class/power_supply/rk808-usb/voltage_now"
        self.current_path = "/sys/class/power_supply/rk808-usb/current_now"
        self.power_stats_path = "/var/log/kernel/power_metrics.json"
        
        # Ensure power metrics directory exists
        os.makedirs(os.path.dirname(self.power_stats_path), exist_ok=True)
        
        # Initialize logger
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for power monitoring"""
        logger.add(
            "/var/log/kernel/power.log",
            rotation="100 MB",
            retention=5,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}"
        )

    def read_sysfs_value(self, path):
        """Read value from sysfs file"""
        try:
            with open(path, 'r') as f:
                return int(f.read().strip())
        except (IOError, ValueError) as e:
            logger.error(f"Error reading {path}: {e}")
            return None

    def get_voltage(self):
        """Get current voltage in microvolts"""
        value = self.read_sysfs_value(self.voltage_path)
        return value / 1000000 if value is not None else None  # Convert to volts

    def get_current(self):
        """Get current in microamps"""
        value = self.read_sysfs_value(self.current_path)
        return value / 1000 if value is not None else None  # Convert to milliamps

    def calculate_power(self, voltage, current):
        """Calculate power consumption in watts"""
        if voltage is not None and current is not None:
            return (voltage * current) / 1000  # Convert to watts
        return None

    def save_metrics(self, metrics):
        """Save power metrics to JSON file"""
        try:
            # Load existing metrics if file exists
            if os.path.exists(self.power_stats_path):
                with open(self.power_stats_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {'measurements': []}

            # Add new measurement
            data['measurements'].append(metrics)

            # Keep only last 1000 measurements
            if len(data['measurements']) > 1000:
                data['measurements'] = data['measurements'][-1000:]

            # Save updated metrics
            with open(self.power_stats_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving power metrics: {e}")

    def monitor(self):
        """Main monitoring loop"""
        logger.info("Starting power monitoring")
        
        try:
            while True:
                voltage = self.get_voltage()
                current = self.get_current()
                power = self.calculate_power(voltage, current)
                timestamp = datetime.now().isoformat()

                metrics = {
                    'timestamp': timestamp,
                    'voltage': voltage,
                    'current': current,
                    'power': power
                }

                # Log metrics
                if all(v is not None for v in [voltage, current, power]):
                    logger.info(
                        f"Power metrics - Voltage: {voltage:.2f}V, "
                        f"Current: {current:.2f}mA, "
                        f"Power: {power:.2f}W"
                    )
                else:
                    logger.warning("Failed to read some power metrics")

                # Save metrics to file
                self.save_metrics(metrics)

                # Wait before next reading
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Power monitoring stopped")
        except Exception as e:
            logger.error(f"Unexpected error in power monitoring: {e}")

if __name__ == "__main__":
    monitor = PowerMonitor()
    monitor.monitor()