#!/usr/bin/env python3
"""
Clean Stress Test for Rock 5B+
Shows only real hardware readings - no estimations
"""

import time
import threading
import subprocess
import os
import signal
import sys
from datetime import datetime

class CleanStressTest:
    def __init__(self):
        self.running = True
        self.cpu_threads = []
        self.gpu_process = None
        
    def cpu_stress(self, thread_id):
        """CPU stress function - maximum intensity"""
        print(f"Starting CPU stress thread {thread_id}")
        while self.running:
            # Maximum CPU stress - no delays
            result = 0
            for i in range(20000000):  # 20M iterations
                result += i * i * 3.14159
        print(f"CPU stress thread {thread_id} stopped")
    
    def get_cpu_percentage(self):
        """Get CPU usage percentage from /proc/stat"""
        try:
            with open('/proc/stat', 'r') as f:
                lines = f.readlines()
            
            cpu_line = lines[0].split()[1:]
            cpu_times = [int(x) for x in cpu_line]
            
            total_time = sum(cpu_times)
            idle_time = cpu_times[3]
            
            if not hasattr(self, 'prev_total'):
                self.prev_total = total_time
                self.prev_idle = idle_time
                return 0.0
            
            total_diff = total_time - self.prev_total
            idle_diff = idle_time - self.prev_idle
            
            if total_diff > 0:
                cpu_percent = 100.0 * (1.0 - idle_diff / total_diff)
            else:
                cpu_percent = 0.0
            
            self.prev_total = total_time
            self.prev_idle = idle_time
            
            return cpu_percent
            
        except Exception as e:
            return 0.0
    
    def get_gpu_load(self):
        """Get real GPU load from hardware"""
        try:
            # Try Mali GPU load
            with open('/sys/class/devfreq/fb000000.gpu-mali/load', 'r') as f:
                gpu_load = int(f.read().strip())
                return gpu_load
        except:
            try:
                # Try alternative GPU load path
                with open('/sys/class/devfreq/fb000000.gpu/load', 'r') as f:
                    gpu_load = int(f.read().strip())
                    return gpu_load
            except:
                return 0
    
    def get_real_power_readings(self):
        """Get real power readings from hardware sensors only"""
        power_info = {
            'voltage_input': 0,
            'current_input': 0,
            'power_input': 0,
            'power_source': 'No Sensor'
        }
        
        try:
            # Try USB-C power supply (most accurate)
            try:
                with open('/sys/class/power_supply/tcpm-source-psy-4-0022/current_now', 'r') as f:
                    current_ua = int(f.read().strip())
                    power_info['current_input'] = current_ua / 1000000.0  # μA to A
                
                with open('/sys/class/power_supply/tcpm-source-psy-4-0022/voltage_now', 'r') as f:
                    voltage_uv = int(f.read().strip())
                    power_info['voltage_input'] = voltage_uv / 1000000.0  # μV to V
                
                power_info['power_input'] = power_info['voltage_input'] * power_info['current_input']
                power_info['power_source'] = 'USB-C Power Supply'
                
            except:
                # Try hwmon7 sensor
                try:
                    with open('/sys/class/hwmon/hwmon7/curr1_input', 'r') as f:
                        current_ma = int(f.read().strip())
                        power_info['current_input'] = current_ma / 1000.0  # mA to A
                    
                    with open('/sys/class/hwmon/hwmon7/in0_input', 'r') as f:
                        voltage_mv = int(f.read().strip())
                        power_info['voltage_input'] = voltage_mv / 1000.0  # mV to V
                    
                    power_info['power_input'] = power_info['voltage_input'] * power_info['current_input']
                    power_info['power_source'] = 'hwmon7 Sensor'
                    
                except:
                    # Try regulator summary
                    try:
                        result = subprocess.run(['cat', '/sys/kernel/debug/regulator/regulator_summary'], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            lines = result.stdout.split('\n')
                            for line in lines:
                                if 'vcc_5v' in line or 'vcc_12v' in line:
                                    parts = line.split()
                                    if len(parts) >= 7:
                                        try:
                                            voltage = float(parts[5]) / 1000.0
                                            current = float(parts[6]) / 1000.0
                                            if voltage > 0:
                                                power_info['voltage_input'] = voltage
                                                power_info['current_input'] = current
                                                power_info['power_input'] = voltage * current
                                                power_info['power_source'] = 'Regulator'
                                                break
                                        except (ValueError, IndexError):
                                            continue
                    except:
                        pass
                
        except Exception as e:
            print(f"Power reading error: {e}")
        
        return power_info
    
    def gpu_stress(self):
        """GPU stress using glmark2"""
        print("Starting GPU stress (glmark2)")
        try:
            self.gpu_process = subprocess.Popen(['glmark2', '--duration', '60', '--fullscreen'], 
                                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("GPU stress using glmark2")
        except Exception as e:
            print(f"GPU stress failed: {e}")
    
    def monitor_system(self):
        """Monitor system resources with real hardware readings only"""
        print("Starting system monitoring")
        while self.running:
            try:
                # Get CPU percentage
                cpu_percent = self.get_cpu_percentage()
                
                # Get GPU load
                gpu_load = self.get_gpu_load()
                
                # Get memory usage
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                    total_mem = int(lines[0].split()[1])
                    free_mem = int(lines[1].split()[1])
                    used_mem = total_mem - free_mem
                    mem_percent = (used_mem / total_mem) * 100
                
                # Get temperature
                try:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = int(f.read().strip()) / 1000
                except:
                    temp = 0
                
                # Get real power readings
                power_info = self.get_real_power_readings()
                
                # Display monitoring info
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"CPU: {cpu_percent:.1f}% | "
                      f"GPU: {gpu_load}% | "
                      f"RAM: {mem_percent:.1f}% | "
                      f"Temp: {temp:.1f}°C | "
                      f"Power: {power_info['voltage_input']:.2f}V, "
                      f"{power_info['current_input']:.3f}A, "
                      f"{power_info['power_input']:.2f}W "
                      f"({power_info['power_source']})")
                
                time.sleep(5)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def start_stress(self, duration=300):
        """Start the stress test"""
        print(f"🚀 Starting Clean Stress Test (Duration: {duration}s)")
        print("=" * 50)
        print("📊 Real Hardware Readings Only - No Estimations")
        print("=" * 50)
        
        # Start CPU stress threads (6 threads for maximum load)
        for i in range(6):
            thread = threading.Thread(target=self.cpu_stress, args=(i+1,))
            thread.daemon = True
            thread.start()
            self.cpu_threads.append(thread)
        
        # Start GPU stress
        gpu_thread = threading.Thread(target=self.gpu_stress)
        gpu_thread.daemon = True
        gpu_thread.start()
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("✅ All stress components started")
        print("📊 Monitoring real hardware sensors...")
        print("⏰ Test will run for", duration, "seconds")
        print("🛑 Press Ctrl+C to stop early")
        print("=" * 50)
        
        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n⚠️  Stopping stress test...")
        
        self.stop_stress()
    
    def stop_stress(self):
        """Stop the stress test"""
        print("🛑 Stopping stress test...")
        self.running = False
        
        # Stop GPU process
        if self.gpu_process:
            try:
                self.gpu_process.terminate()
                self.gpu_process.wait(timeout=5)
            except:
                self.gpu_process.kill()
        
        # Wait for threads to finish
        for thread in self.cpu_threads:
            thread.join(timeout=2)
        
        print("✅ Stress test stopped")
        print("📊 Final system status:")
        
        # Show final status
        try:
            # Get final CPU percentage
            cpu_percent = self.get_cpu_percentage()
            print(f"   CPU Usage: {cpu_percent:.1f}%")
            
            # Get final GPU load
            gpu_load = self.get_gpu_load()
            print(f"   GPU Load: {gpu_load}%")
            
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total_mem = int(lines[0].split()[1])
                free_mem = int(lines[1].split()[1])
                used_mem = total_mem - free_mem
                mem_percent = (used_mem / total_mem) * 100
                print(f"   Memory Usage: {mem_percent:.1f}%")
            
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000
                print(f"   Temperature: {temp:.1f}°C")
            
            # Show final power status
            power_info = self.get_real_power_readings()
            print(f"   Power: {power_info['voltage_input']:.2f}V, "
                  f"{power_info['current_input']:.3f}A, "
                  f"{power_info['power_input']:.2f}W "
                  f"({power_info['power_source']})")
                
        except Exception as e:
            print(f"   Error reading final status: {e}")

def signal_handler(signum, frame):
    """Handle Ctrl+C"""
    print("\n⚠️  Received interrupt signal")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    duration = 300  # 5 minutes default
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 clean_stress_test.py [duration_seconds]")
            print("Default duration: 300 seconds (5 minutes)")
            sys.exit(1)
    
    # Create and run stress test
    stress_test = CleanStressTest()
    stress_test.start_stress(duration)
