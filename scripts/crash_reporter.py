#!/usr/bin/env python3

import os
import json
import time
import shutil
from datetime import datetime
from pathlib import Path
from loguru import logger

class CrashReporter:
    def __init__(self):
        self.crash_dir = "/var/log/kernel/crashes"
        self.current_boot_file = "/var/log/kernel/current_boot"
        self.last_crash_file = "/var/log/kernel/last_crash"
        self.kernel_log = "/var/log/kernel/kernel.log"
        self.max_crash_reports = 50
        
        # Ensure directories exist
        os.makedirs(self.crash_dir, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for crash reporter"""
        logger.add(
            "/var/log/kernel/crash_reporter.log",
            rotation="100 MB",
            retention=5,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}"
        )

    def get_boot_id(self):
        """Get current boot ID from kernel"""
        try:
            with open("/proc/sys/kernel/random/boot_id", "r") as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to get boot ID: {e}")
            return None

    def save_current_boot(self):
        """Save current boot ID"""
        boot_id = self.get_boot_id()
        if boot_id:
            try:
                with open(self.current_boot_file, "w") as f:
                    f.write(boot_id)
            except Exception as e:
                logger.error(f"Failed to save current boot ID: {e}")

    def check_previous_crash(self):
        """Check if system crashed in previous session"""
        try:
            if os.path.exists(self.current_boot_file):
                with open(self.current_boot_file, "r") as f:
                    last_boot_id = f.read().strip()
                
                current_boot_id = self.get_boot_id()
                
                if last_boot_id != current_boot_id:
                    logger.warning("Detected unclean shutdown from previous session")
                    self.generate_crash_report(last_boot_id)
            
            # Update current boot ID
            self.save_current_boot()
            
        except Exception as e:
            logger.error(f"Error checking previous crash: {e}")

    def collect_system_state(self):
        """Collect relevant system state information"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "boot_id": self.get_boot_id(),
            "kernel_version": os.uname().release,
            "uptime": self.get_uptime(),
            "memory_info": self.get_memory_info(),
            "last_kernel_logs": self.get_last_kernel_logs(),
            "gpu_state": self.get_gpu_state()
        }
        return state

    def get_uptime(self):
        """Get system uptime"""
        try:
            with open("/proc/uptime", "r") as f:
                uptime = float(f.read().split()[0])
                return uptime
        except Exception as e:
            logger.error(f"Failed to get uptime: {e}")
            return None

    def get_memory_info(self):
        """Get memory information"""
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = {}
                for line in f:
                    key, value = line.split(":", 1)
                    meminfo[key.strip()] = value.strip()
                return meminfo
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return None

    def get_last_kernel_logs(self, lines=1000):
        """Get last N lines of kernel log"""
        try:
            if os.path.exists(self.kernel_log):
                with open(self.kernel_log, "r") as f:
                    return list(f.readlines()[-lines:])
            return []
        except Exception as e:
            logger.error(f"Failed to get kernel logs: {e}")
            return []

    def get_gpu_state(self):
        """Get GPU driver state"""
        try:
            gpu_state = {}
            # Check loaded GPU driver
            with open("/proc/modules", "r") as f:
                modules = f.read()
                if "mali" in modules:
                    gpu_state["driver"] = "mali"
                elif "panfrost" in modules:
                    gpu_state["driver"] = "panfrost"
                else:
                    gpu_state["driver"] = "unknown"
            
            return gpu_state
        except Exception as e:
            logger.error(f"Failed to get GPU state: {e}")
            return None

    def generate_crash_report(self, boot_id):
        """Generate crash report with system state"""
        try:
            # Collect system state
            state = self.collect_system_state()
            
            # Create crash report
            crash_report = {
                "crash_boot_id": boot_id,
                "current_boot_id": self.get_boot_id(),
                "crash_time": datetime.now().isoformat(),
                "system_state": state
            }
            
            # Save crash report
            report_path = os.path.join(
                self.crash_dir,
                f"crash_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(report_path, "w") as f:
                json.dump(crash_report, f, indent=2)
            
            # Update last crash file
            shutil.copy2(report_path, self.last_crash_file)
            
            logger.info(f"Generated crash report: {report_path}")
            
            # Cleanup old reports
            self.cleanup_old_reports()
            
        except Exception as e:
            logger.error(f"Failed to generate crash report: {e}")

    def cleanup_old_reports(self):
        """Remove old crash reports keeping only max_crash_reports"""
        try:
            reports = sorted(Path(self.crash_dir).glob("crash_report_*.json"))
            if len(reports) > self.max_crash_reports:
                for report in reports[:-self.max_crash_reports]:
                    report.unlink()
                logger.info(f"Cleaned up {len(reports) - self.max_crash_reports} old crash reports")
        except Exception as e:
            logger.error(f"Failed to cleanup old reports: {e}")

if __name__ == "__main__":
    reporter = CrashReporter()
    reporter.check_previous_crash()