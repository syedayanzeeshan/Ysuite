#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
from pathlib import Path

class SystemSetup:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.config_dir = self.script_dir.parent / "configs"
        
    def run_command(self, cmd, check=True):
        """Run a shell command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=check,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error running command '{cmd}': {e}")
            if check:
                sys.exit(1)
            return None

    def install_mali_driver(self):
        """Install Mali GPU driver packages"""
        print("Installing Mali GPU driver...")
        
        # Check product ID
        result = self.run_command("rsetup get_product_ids")
        if "rk3588" in result.stdout:
            self.run_command(
                "apt-get install -y libmali-valhall-g610-g24p0-x11-wayland-gbm"
            )
        elif any(id in result.stdout for id in ["rk3576", "rk3568", "rk3566"]):
            self.run_command(
                "apt-get install -y libmali-bifrost-g52-g13p0-x11-wayland-gbm"
            )
        else:
            print("Unsupported product ID")
            sys.exit(1)

    def setup_configs(self):
        """Set up configuration files"""
        print("Setting up configuration files...")
        
        # Create required directories
        dirs = [
            "/etc/apt/preferences.d",
            "/etc/modprobe.d",
            "/etc/systemd/system",
            "/var/log/kernel",
            "/var/log/kernel/crashes",
            "/usr/local/bin"
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        # Copy configuration files
        configs = {
            "etc/apt/preferences.d/mali": "/etc/apt/preferences.d/mali",
            "etc/modprobe.d/panfrost.conf": "/etc/modprobe.d/panfrost.conf",
            "etc/environment": "/etc/environment",
            "etc/systemd/system/kernel-logger.service": "/etc/systemd/system/kernel-logger.service",
            "etc/systemd/system/power-monitor.service": "/etc/systemd/system/power-monitor.service",
            "etc/systemd/system/crash-reporter.service": "/etc/systemd/system/crash-reporter.service"
        }
        
        for src, dst in configs.items():
            src_path = self.config_dir / src
            if src_path.exists():
                shutil.copy2(src_path, dst)
                print(f"Copied {src} to {dst}")
            else:
                print(f"Warning: Source file {src_path} not found")

        # Copy scripts
        scripts = [
            "kernel_logger_daemon.py",
            "power_monitor.py",
            "crash_reporter.py"
        ]
        
        for script in scripts:
            src = self.script_dir / script
            dst = f"/usr/local/bin/{script}"
            if src.exists():
                shutil.copy2(src, dst)
                os.chmod(dst, 0o755)
                print(f"Installed {script} to {dst}")
            else:
                print(f"Warning: Script {src} not found")

    def enable_services(self):
        """Enable and start systemd services"""
        print("Enabling services...")
        services = [
            "kernel-logger.service",
            "power-monitor.service",
            "crash-reporter.service"
        ]
        
        for service in services:
            self.run_command(f"systemctl enable {service}")
            self.run_command(f"systemctl start {service}")
            
            # Check service status
            result = self.run_command(f"systemctl is-active {service}", check=False)
            if result and result.stdout.strip() == "active":
                print(f"Service {service} is running")
            else:
                print(f"Warning: Service {service} failed to start")

    def verify_installation(self):
        """Perform basic verification tests"""
        print("\nVerifying installation...")
        
        # Check GPU driver
        print("\nChecking GPU driver:")
        self.run_command("lsmod | grep -E 'mali|bifrost_kbase|panfrost'")
        
        # Check logging
        print("\nChecking log files:")
        log_files = [
            "/var/log/kernel/kernel.log",
            "/var/log/kernel/power.log",
            "/var/log/kernel/crash_reporter.log"
        ]
        for log_file in log_files:
            if os.path.exists(log_file):
                size = os.path.getsize(log_file)
                print(f"{log_file}: {size} bytes")
            else:
                print(f"Warning: {log_file} not found")
        
        # Check services
        print("\nChecking service status:")
        self.run_command("systemctl status kernel-logger power-monitor crash-reporter")

def main():
    if os.geteuid() != 0:
        print("This script must be run as root")
        sys.exit(1)
        
    setup = SystemSetup()
    
    print("Starting system setup...")
    setup.install_mali_driver()
    setup.setup_configs()
    setup.enable_services()
    setup.verify_installation()
    print("\nSetup completed successfully")

if __name__ == "__main__":
    main()