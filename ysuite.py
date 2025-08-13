#!/usr/bin/env python3
"""
YSuite - Comprehensive Rock 5B+ Monitoring and Management Suite
A unified package for headless Rock 5B+ systems with real-time monitoring,
crash detection, power management, and system optimization.
"""

import os
import sys
import json
import time
import subprocess
import threading
import signal
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import platform

# Global configuration
SUITE_VERSION = "1.0.0"
SUITE_NAME = "YSuite"
BASE_DIR = Path("/opt/ysuite")
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class YSuite:
    def __init__(self):
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories for the suite"""
        for directory in [BASE_DIR, LOG_DIR, CONFIG_DIR, DATA_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

class YTop:
    """Real-time system performance monitor (CLI version of rtop)"""
    
    def __init__(self):
        self.running = False
        
    def get_cpu_info(self):
        """Get CPU load and frequency information"""
        try:
            # CPU load from /proc/stat
            with open('/proc/stat', 'r') as f:
                lines = f.readlines()
                cpu_line = lines[0].split()[1:]
                total = sum(int(x) for x in cpu_line)
                idle = int(cpu_line[3])
                load = 100 - (idle * 100 / total)
                
            # CPU frequency
            freq = 0
            for i in range(8):  # Rock 5B has 8 cores
                try:
                    with open(f'/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq', 'r') as f:
                        freq += int(f.read().strip())
                except:
                    break
            freq = freq // 8  # Average frequency
            
            return {
                'load': round(load, 1),
                'freq': freq // 1000  # Convert to MHz
            }
        except:
            return {'load': 0, 'freq': 0}
    
    def get_gpu_info(self):
        """Get GPU load and frequency"""
        try:
            # GPU load
            with open('/sys/class/devfreq/fb000000.gpu/load', 'r') as f:
                load = int(f.read().strip())
                
            # GPU frequency
            with open('/sys/class/devfreq/fb000000.gpu/cur_freq', 'r') as f:
                freq = int(f.read().strip()) // 1000000  # Convert to MHz
                
            return {'load': load, 'freq': freq}
        except:
            return {'load': 0, 'freq': 0}
    
    def get_npu_info(self):
        """Get NPU load and frequency"""
        try:
            # NPU load
            result = subprocess.run(['sudo', 'cat', '/sys/kernel/debug/rknpu/load'], 
                                  capture_output=True, text=True)
            load = int(result.stdout.strip()) if result.returncode == 0 else 0
            
            # NPU frequency
            with open('/sys/class/devfreq/fdab0000.npu/cur_freq', 'r') as f:
                freq = int(f.read().strip()) // 1000000  # Convert to MHz
                
            return {'load': load, 'freq': freq}
        except:
            return {'load': 0, 'freq': 0}
    
    def get_memory_info(self):
        """Get memory usage information"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                mem_info = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        mem_info[key.strip()] = int(value.split()[0])
                        
            total = mem_info['MemTotal']
            available = mem_info['MemAvailable']
            used = total - available
            usage_percent = (used / total) * 100
            
            return {
                'total': total // 1024,  # MB
                'used': used // 1024,    # MB
                'usage_percent': round(usage_percent, 1)
            }
        except:
            return {'total': 0, 'used': 0, 'usage_percent': 0}
    
    def get_temperature(self):
        """Get system temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000  # Convert to Celsius
            return round(temp, 1)
        except:
            return 0
    
    def get_fan_speed(self):
        """Get fan speed"""
        try:
            with open('/sys/class/thermal/cooling_device4/cur_state', 'r') as f:
                speed = int(f.read().strip())
            return speed
        except:
            return 0
    
    def create_bar(self, value, max_value, width=20):
        """Create a visual progress bar"""
        filled = int((value / max_value) * width)
        bar = '█' * filled + '░' * (width - filled)
        return bar
    
    def display_stats(self):
        """Display real-time system statistics"""
        os.system('clear')
        
        # Get all system information
        cpu = self.get_cpu_info()
        gpu = self.get_gpu_info()
        npu = self.get_npu_info()
        memory = self.get_memory_info()
        temp = self.get_temperature()
        fan = self.get_fan_speed()
        
        # Header
        print(f"{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║                           YSuite - Real-time System Monitor                    ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║                              Rock 5B+ Performance Dashboard                      ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        print()
        
        # CPU Section
        print(f"{Colors.BOLD}{Colors.YELLOW}🖥️  CPU Information:{Colors.END}")
        cpu_bar = self.create_bar(cpu['load'], 100)
        print(f"   Load:    {cpu['load']:5.1f}% {cpu_bar} {Colors.GREEN}{cpu['load']:5.1f}%{Colors.END}")
        print(f"   Frequency: {cpu['freq']:4d} MHz")
        print()
        
        # GPU Section
        print(f"{Colors.BOLD}{Colors.MAGENTA}🎮 GPU Information:{Colors.END}")
        gpu_bar = self.create_bar(gpu['load'], 100)
        print(f"   Load:    {gpu['load']:5d}% {gpu_bar} {Colors.GREEN}{gpu['load']:5d}%{Colors.END}")
        print(f"   Frequency: {gpu['freq']:4d} MHz")
        print()
        
        # NPU Section
        print(f"{Colors.BOLD}{Colors.BLUE}🧠 NPU Information:{Colors.END}")
        npu_bar = self.create_bar(npu['load'], 100)
        print(f"   Load:    {npu['load']:5d}% {npu_bar} {Colors.GREEN}{npu['load']:5d}%{Colors.END}")
        print(f"   Frequency: {npu['freq']:4d} MHz")
        print()
        
        # Memory Section
        print(f"{Colors.BOLD}{Colors.CYAN}💾 Memory Information:{Colors.END}")
        mem_bar = self.create_bar(memory['usage_percent'], 100)
        print(f"   Usage:   {memory['usage_percent']:5.1f}% {mem_bar} {Colors.GREEN}{memory['usage_percent']:5.1f}%{Colors.END}")
        print(f"   Used:    {memory['used']:5d} MB / {memory['total']:5d} MB")
        print()
        
        # Temperature and Fan
        print(f"{Colors.BOLD}{Colors.RED}🌡️  System Status:{Colors.END}")
        temp_color = Colors.RED if temp > 70 else Colors.YELLOW if temp > 50 else Colors.GREEN
        print(f"   Temperature: {temp_color}{temp:5.1f}°C{Colors.END}")
        print(f"   Fan Speed:    {fan:5d} (0-255)")
        print()
        
        # Footer
        print(f"{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║  Press Ctrl+C to exit | YSuite v{SUITE_VERSION} | {datetime.now().strftime('%H:%M:%S')} ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
    
    def run(self, interval=1):
        """Run the real-time monitor"""
        self.running = True
        
        def signal_handler(signum, frame):
            self.running = False
            print(f"\n{Colors.YELLOW}YTop monitoring stopped.{Colors.END}")
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while self.running:
                self.display_stats()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.running = False
            print(f"\n{Colors.YELLOW}YTop monitoring stopped.{Colors.END}")

class YLog:
    """System log monitoring and classification"""
    
    def __init__(self):
        self.log_file = LOG_DIR / "system_logs.json"
        self.critical_patterns = [
            'error', 'fail', 'critical', 'panic', 'segfault', 'oom',
            'timeout', 'corruption', 'invalid', 'unexpected'
        ]
        
    def monitor_logs(self):
        """Monitor system logs in real-time"""
        print(f"{Colors.BOLD}{Colors.CYAN}📋 YLog - System Log Monitor{Colors.END}")
        print(f"{Colors.YELLOW}Monitoring system logs for critical events...{Colors.END}")
        print(f"Log file: {self.log_file}")
        print()
        
        try:
            # Monitor journalctl for new entries
            process = subprocess.Popen(
                ['journalctl', '-f', '--no-pager'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                    
                # Check for critical patterns
                if any(pattern in line.lower() for pattern in self.critical_patterns):
                    self.log_critical_event(line.strip())
                    print(f"{Colors.RED}🚨 CRITICAL: {line.strip()}{Colors.END}")
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Log monitoring stopped.{Colors.END}")
            
    def log_critical_event(self, message):
        """Log critical events to JSON file"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'severity': 'critical',
            'source': 'system_log'
        }
        
        # Load existing logs
        logs = []
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # Add new event
        logs.append(event)
        
        # Keep only last 1000 events
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Save to file
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def show_summary(self):
        """Show log summary"""
        if not self.log_file.exists():
            print(f"{Colors.YELLOW}No log file found.{Colors.END}")
            return
            
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        print(f"{Colors.BOLD}{Colors.CYAN}📊 Log Summary{Colors.END}")
        print(f"Total events: {len(logs)}")
        
        # Count by severity
        critical_count = len([log for log in logs if log.get('severity') == 'critical'])
        print(f"Critical events: {critical_count}")
        
        # Show recent events
        print(f"\n{Colors.BOLD}Recent Critical Events:{Colors.END}")
        recent_logs = logs[-10:]  # Last 10 events
        for log in recent_logs:
            timestamp = log['timestamp'][:19]  # Remove microseconds
            print(f"{Colors.RED}{timestamp}: {log['message'][:80]}...{Colors.END}")

class YCrash:
    """Crash detection and analysis"""
    
    def __init__(self):
        self.crash_file = DATA_DIR / "crashes.json"
        self.crash_patterns = [
            'segmentation fault', 'core dumped', 'killed', 'oom',
            'panic', 'fatal', 'abort', 'assertion failed'
        ]
        
    def monitor_crashes(self):
        """Monitor for crash events"""
        print(f"{Colors.BOLD}{Colors.RED}💥 YCrash - Crash Monitor{Colors.END}")
        print(f"{Colors.YELLOW}Monitoring for system crashes and critical failures...{Colors.END}")
        print(f"Crash file: {self.crash_file}")
        print()
        
        # Monitor dmesg for crash events
        try:
            process = subprocess.Popen(
                ['dmesg', '-w'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                    
                # Check for crash patterns
                if any(pattern in line.lower() for pattern in self.crash_patterns):
                    self.log_crash_event(line.strip())
                    print(f"{Colors.RED}💥 CRASH DETECTED: {line.strip()}{Colors.END}")
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Crash monitoring stopped.{Colors.END}")
    
    def log_crash_event(self, message):
        """Log crash events to JSON file"""
        crash = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': 'crash',
            'source': 'kernel'
        }
        
        # Load existing crashes
        crashes = []
        if self.crash_file.exists():
            try:
                with open(self.crash_file, 'r') as f:
                    crashes = json.load(f)
            except:
                crashes = []
        
        # Add new crash
        crashes.append(crash)
        
        # Keep only last 100 crashes
        if len(crashes) > 100:
            crashes = crashes[-100:]
        
        # Save to file
        with open(self.crash_file, 'w') as f:
            json.dump(crashes, f, indent=2)
    
    def show_summary(self):
        """Show crash summary"""
        if not self.crash_file.exists():
            print(f"{Colors.YELLOW}No crash file found.{Colors.END}")
            return
            
        with open(self.crash_file, 'r') as f:
            crashes = json.load(f)
        
        print(f"{Colors.BOLD}{Colors.RED}💥 Crash Summary{Colors.END}")
        print(f"Total crashes: {len(crashes)}")
        
        # Show recent crashes
        print(f"\n{Colors.BOLD}Recent Crashes:{Colors.END}")
        recent_crashes = crashes[-5:]  # Last 5 crashes
        for crash in recent_crashes:
            timestamp = crash['timestamp'][:19]
            print(f"{Colors.RED}{timestamp}: {crash['message'][:80]}...{Colors.END}")

class YPower:
    """Power monitoring and USB PD negotiation"""
    
    def __init__(self):
        self.power_file = DATA_DIR / "power_data.json"
        
    def get_adc_voltage(self):
        """Get voltage from ADC"""
        try:
            with open('/sys/devices/platform/fec10000.saradc/iio:device0/in_voltage6_raw', 'r') as f:
                raw_value = int(f.read().strip())
            # Convert to voltage (approximate conversion)
            voltage = (raw_value / 4095) * 3.3 * 3  # Assuming 3.3V reference and voltage divider
            return round(voltage, 2)
        except:
            return 0
    
    def get_pd_info(self):
        """Get USB PD information"""
        pd_info = {
            'online': False,
            'voltage': 0,
            'current': 0,
            'pd_capable': False,
            'role': 'unknown'
        }
        
        try:
            # Check if PD supply is online
            with open('/sys/class/power_supply/usb-c0/online', 'r') as f:
                pd_info['online'] = bool(int(f.read().strip()))
            
            if pd_info['online']:
                # Get voltage and current
                with open('/sys/class/power_supply/usb-c0/voltage_now', 'r') as f:
                    pd_info['voltage'] = int(f.read().strip()) / 1000000  # Convert to V
                    
                with open('/sys/class/power_supply/usb-c0/current_now', 'r') as f:
                    pd_info['current'] = int(f.read().strip()) / 1000  # Convert to mA
                
                # Check if PD capable
                try:
                    with open('/sys/class/typec/port0/power_role', 'r') as f:
                        pd_info['role'] = f.read().strip()
                        pd_info['pd_capable'] = True
                except:
                    pd_info['pd_capable'] = False
                    
        except:
            pass
            
        return pd_info
    
    def negotiate_3a_current(self):
        """Attempt to negotiate 3A current"""
        try:
            # Try to set preferred role to sink
            subprocess.run(['sudo', 'bash', '-c', 
                          'echo sink > /sys/class/typec/port0/preferred_role'], 
                          capture_output=True)
            
            # Try to initiate power role swap
            subprocess.run(['sudo', 'bash', '-c', 
                          'echo 1 > /sys/class/typec/port0/pr_swap'], 
                          capture_output=True)
            
            print(f"{Colors.GREEN}✅ PD negotiation attempted{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ PD negotiation failed: {e}{Colors.END}")
    
    def estimate_current(self):
        """Estimate current based on system load"""
        try:
            # Get CPU load
            with open('/proc/stat', 'r') as f:
                lines = f.readlines()
                cpu_line = lines[0].split()[1:]
                total = sum(int(x) for x in cpu_line)
                idle = int(cpu_line[3])
                load = 100 - (idle * 100 / total)
            
            # Estimate current based on load (rough approximation)
            # Base current ~500mA, max current ~3A
            base_current = 0.5
            max_current = 3.0
            estimated_current = base_current + (load / 100) * (max_current - base_current)
            
            return round(estimated_current, 2)
        except:
            return 0.5
    
    def monitor_power(self):
        """Monitor power in real-time"""
        print(f"{Colors.BOLD}{Colors.GREEN}⚡ YPower - Power Monitor{Colors.END}")
        print(f"{Colors.YELLOW}Monitoring power input and attempting PD negotiation...{Colors.END}")
        print(f"Power file: {self.power_file}")
        print()
        
        try:
            while True:
                # Get power information
                adc_voltage = self.get_adc_voltage()
                pd_info = self.get_pd_info()
                estimated_current = self.estimate_current()
                
                # Determine actual voltage and current
                if pd_info['online'] and pd_info['voltage'] > 0:
                    voltage = pd_info['voltage']
                    current = pd_info['current'] / 1000  # Convert to A
                    power_source = "USB PD"
                elif adc_voltage > 0:
                    voltage = adc_voltage
                    current = estimated_current
                    power_source = "ADC Reading"
                else:
                    voltage = 0
                    current = 0
                    power_source = "Unknown"
                
                # Calculate power
                power = voltage * current
                
                # Display information
                os.system('clear')
                print(f"{Colors.BOLD}{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}║                              YPower - Power Monitor                          ║{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
                print()
                
                print(f"{Colors.BOLD}🔌 Power Source:{Colors.END} {power_source}")
                print(f"{Colors.BOLD}⚡ Voltage:{Colors.END}      {voltage:5.2f} V")
                print(f"{Colors.BOLD}🔋 Current:{Colors.END}      {current:5.2f} A")
                print(f"{Colors.BOLD}💡 Power:{Colors.END}        {power:5.2f} W")
                print()
                
                # PD Information
                print(f"{Colors.BOLD}🔗 USB PD Status:{Colors.END}")
                status_icon = "✅" if pd_info['online'] else "❌"
                print(f"   Online:     {status_icon} {pd_info['online']}")
                print(f"   PD Capable: {'✅' if pd_info['pd_capable'] else '❌'}")
                print(f"   Role:       {pd_info['role']}")
                print()
                
                # ADC Information
                print(f"{Colors.BOLD}📊 ADC Reading:{Colors.END}")
                print(f"   Raw ADC:    {adc_voltage:5.2f} V")
                print()
                
                # Footer
                print(f"{Colors.BOLD}{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}║  Press Ctrl+C to exit | Press 'n' to negotiate 3A | {datetime.now().strftime('%H:%M:%S')} ║{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
                
                # Log power data
                self.log_power_data(voltage, current, power, power_source)
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Power monitoring stopped.{Colors.END}")
    
    def log_power_data(self, voltage, current, power, source):
        """Log power data to JSON file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'voltage': voltage,
            'current': current,
            'power': power,
            'source': source
        }
        
        # Load existing data
        power_data = []
        if self.power_file.exists():
            try:
                with open(self.power_file, 'r') as f:
                    power_data = json.load(f)
            except:
                power_data = []
        
        # Add new data
        power_data.append(data)
        
        # Keep only last 1000 entries
        if len(power_data) > 1000:
            power_data = power_data[-1000:]
        
        # Save to file
        with open(self.power_file, 'w') as f:
            json.dump(power_data, f, indent=2)

def show_help():
    """Show comprehensive help for YSuite"""
    print(f"{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}║                              YSuite v{SUITE_VERSION} - Help                           ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
    print()
    
    print(f"{Colors.BOLD}{Colors.YELLOW}Available Commands:{Colors.END}")
    print()
    
    print(f"{Colors.BOLD}{Colors.GREEN}ytop{Colors.END} - Real-time System Performance Monitor")
    print(f"   Usage: ytop [interval]")
    print(f"   Description: CLI version of rtop for Rock 5B+")
    print(f"   Features: CPU, GPU, NPU, Memory, Temperature, Fan monitoring")
    print(f"   Example: ytop 2  # Update every 2 seconds")
    print()
    
    print(f"{Colors.BOLD}{Colors.BLUE}ylog{Colors.END} - System Log Monitor")
    print(f"   Usage: ylog [--monitor|--summary]")
    print(f"   Description: Monitor and classify system logs")
    print(f"   Features: Real-time monitoring, critical event detection, JSON logging")
    print(f"   Example: ylog --monitor  # Start real-time monitoring")
    print()
    
    print(f"{Colors.BOLD}{Colors.RED}ycrash{Colors.END} - Crash Detection and Analysis")
    print(f"   Usage: ycrash [--monitor|--summary]")
    print(f"   Description: Detect and analyze system crashes")
    print(f"   Features: Kernel crash detection, crash logging, analysis")
    print(f"   Example: ycrash --summary  # Show crash summary")
    print()
    
    print(f"{Colors.BOLD}{Colors.GREEN}ypower{Colors.END} - Power Monitoring and PD Negotiation")
    print(f"   Usage: ypower [--monitor|--negotiate]")
    print(f"   Description: Monitor power input and negotiate USB PD")
    print(f"   Features: Voltage/current monitoring, PD negotiation, ADC reading")
    print(f"   Example: ypower --monitor  # Start power monitoring")
    print()
    
    print(f"{Colors.BOLD}{Colors.MAGENTA}yhelp{Colors.END} - Show this help message")
    print()
    
    print(f"{Colors.BOLD}{Colors.CYAN}Data Storage:{Colors.END}")
    print(f"   Logs: {LOG_DIR}")
    print(f"   Data: {DATA_DIR}")
    print(f"   Config: {CONFIG_DIR}")
    print()
    
    print(f"{Colors.BOLD}{Colors.YELLOW}Installation:{Colors.END}")
    print(f"   Run this script with sudo to install YSuite system-wide")
    print(f"   Example: sudo python3 ysuite.py --install")

def install_suite():
    """Install YSuite system-wide"""
    print(f"{Colors.BOLD}{Colors.CYAN}Installing YSuite system-wide...{Colors.END}")
    
    # Copy script to /usr/local/bin
    script_path = Path(__file__).resolve()
    install_path = Path("/usr/local/bin/ysuite")
    
    try:
        shutil.copy2(script_path, install_path)
        os.chmod(install_path, 0o755)
        print(f"{Colors.GREEN}✅ YSuite installed to {install_path}{Colors.END}")
        
        # Create symlinks for individual commands
        commands = ['ytop', 'ylog', 'ycrash', 'ypower', 'yhelp']
        for cmd in commands:
            symlink_path = Path(f"/usr/local/bin/{cmd}")
            if symlink_path.exists():
                symlink_path.unlink()
            symlink_path.symlink_to(install_path)
            print(f"{Colors.GREEN}✅ Created symlink: {cmd}{Colors.END}")
            
        print(f"\n{Colors.BOLD}{Colors.GREEN}Installation complete!{Colors.END}")
        print(f"You can now use: ytop, ylog, ycrash, ypower, yhelp")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Installation failed: {e}{Colors.END}")
        sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='YSuite - Rock 5B+ Monitoring Suite')
    parser.add_argument('command', nargs='?', help='Command to run')
    parser.add_argument('--install', action='store_true', help='Install YSuite system-wide')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring mode')
    parser.add_argument('--summary', action='store_true', help='Show summary')
    parser.add_argument('--negotiate', action='store_true', help='Negotiate PD')
    parser.add_argument('args', nargs='*', help='Additional arguments')
    
    args = parser.parse_args()
    
    # Initialize suite
    suite = YSuite()
    
    if args.install:
        install_suite()
        return
    
    if not args.command:
        show_help()
        return
    
    # Handle commands
    if args.command == 'ytop':
        ytop = YTop()
        interval = int(args.args[0]) if args.args else 1
        ytop.run(interval)
        
    elif args.command == 'ylog':
        ylog = YLog()
        if args.monitor:
            ylog.monitor_logs()
        else:
            ylog.show_summary()
            
    elif args.command == 'ycrash':
        ycrash = YCrash()
        if args.monitor:
            ycrash.monitor_crashes()
        else:
            ycrash.show_summary()
            
    elif args.command == 'ypower':
        ypower = YPower()
        if args.negotiate:
            ypower.negotiate_3a_current()
        elif args.monitor:
            ypower.monitor_power()
        else:
            ypower.monitor_power()  # Default to monitoring
            
    elif args.command == 'yhelp':
        show_help()
        
    else:
        print(f"{Colors.RED}Unknown command: {args.command}{Colors.END}")
        show_help()

if __name__ == '__main__':
    main()
