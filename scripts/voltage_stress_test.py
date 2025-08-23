#!/usr/bin/env python3
"""
Voltage Stress Test for Rock 5B+
Designed to force voltage intake to increase by maximizing CPU and GPU load
"""

import time
import threading
import subprocess
import os
import signal
import sys
from datetime import datetime
import multiprocessing

class VoltageStressTest:
    def __init__(self):
        self.running = True
        self.cpu_processes = []
        self.gpu_process = None
        
    def get_voltage(self):
        """Get current voltage from ADC"""
        try:
            with open('/sys/bus/iio/devices/iio:device0/in_voltage6_raw', 'r') as f:
                adc_raw = int(f.read().strip())
                voltage = adc_raw / 172.5
                return round(voltage, 2)
        except:
            return 0
    
    def get_cpu_percentage(self):
        """Get CPU usage percentage"""
        try:
            with open('/proc/loadavg', 'r') as f:
                load = f.read().strip().split()[0]
                return float(load)
        except:
            return 0
    
    def get_gpu_load(self):
        """Get GPU load"""
        try:
            with open('/sys/class/devfreq/fb000000.gpu-mali/load', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def cpu_stress_process(self, process_id):
        """Maximum CPU stress - pure computation with no delays"""
        print(f"🔥 CPU stress process {process_id} started")
        while self.running:
            # Maximum CPU stress - pure computation
            result = 0
            for i in range(100000000):  # 100M iterations
                result += i * i * 3.14159
                # No delays - pure CPU stress
                if i % 10000000 == 0:  # Check every 10M iterations
                    if not self.running:
                        break
        print(f"CPU stress process {process_id} stopped")
    
    def gpu_stress(self):
        """GPU stress using multiple methods"""
        print("🔥 Starting GPU stress")
        try:
            # Method 1: glmark2 with multiple instances
            try:
                # Start multiple glmark2 instances
                for i in range(3):
                    cmd = ['glmark2', '--duration', '60', '--size', '800x600', '--fullscreen']
                    self.gpu_process = subprocess.Popen(cmd, 
                                                      stdout=subprocess.DEVNULL, 
                                                      stderr=subprocess.DEVNULL)
                    print(f"GPU stress glmark2 instance {i+1} started")
            except Exception as e:
                print(f"glmark2 failed: {e}")
                self.gpu_process = None
            
            # Method 2: File I/O stress (affects GPU indirectly)
            try:
                gpu_io_stress = """
import time
import subprocess
import os

# Create GPU stress using file operations and system calls
for i in range(60):
    try:
        # Create and delete files rapidly
        for j in range(100):
            with open(f'/tmp/gpu_stress_{j}.tmp', 'w') as f:
                f.write('GPU stress data' * 1000)
            os.remove(f'/tmp/gpu_stress_{j}.tmp')
        
        # Use dd for I/O stress
        subprocess.run(['dd', 'if=/dev/urandom', 'of=/tmp/gpu_test', 'bs=1M', 'count=20'], 
                      capture_output=True, timeout=10)
        subprocess.run(['rm', '-f', '/tmp/gpu_test'], capture_output=True)
        
        time.sleep(1)
    except:
        time.sleep(1)
"""
                with open('/tmp/gpu_io_stress.py', 'w') as f:
                    f.write(gpu_io_stress)
                
                if not self.gpu_process:
                    self.gpu_process = subprocess.Popen(['python3', '/tmp/gpu_io_stress.py'])
                    print("GPU stress using file I/O method")
                
            except Exception as e:
                print(f"Alternative GPU stress failed: {e}")
                
        except Exception as e:
            print(f"GPU stress failed: {e}")
    
    def memory_stress(self):
        """Memory stress to increase power consumption"""
        print("🔥 Starting memory stress")
        try:
            # Allocate large amounts of memory
            memory_stress = """
import time
import gc

# Allocate large amounts of memory
memory_blocks = []
block_size = 100 * 1024 * 1024  # 100MB blocks

try:
    for i in range(10):  # Try to allocate 1GB
        block = bytearray(block_size)
        memory_blocks.append(block)
        print(f"Allocated {len(memory_blocks) * block_size // (1024*1024)}MB")
        time.sleep(1)
    
    # Keep memory allocated and perform operations
    while True:
        for block in memory_blocks:
            # Perform operations on memory
            for j in range(0, len(block), 1024):
                block[j] = (block[j] + 1) % 256
        time.sleep(0.1)
except MemoryError:
    print("Memory limit reached")
    # Continue with available memory
    while True:
        for block in memory_blocks:
            for j in range(0, len(block), 1024):
                block[j] = (block[j] + 1) % 256
        time.sleep(0.1)
"""
            with open('/tmp/memory_stress.py', 'w') as f:
                f.write(memory_stress)
            
            memory_process = subprocess.Popen(['python3', '/tmp/memory_stress.py'],
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
            print("Memory stress started")
            
        except Exception as e:
            print(f"Memory stress failed: {e}")
    
    def monitor_system(self):
        """Monitor system resources and voltage"""
        print("📊 Starting system monitoring")
        baseline_voltage = self.get_voltage()
        print(f"Baseline voltage: {baseline_voltage}V")
        
        while self.running:
            try:
                # Get current readings
                voltage = self.get_voltage()
                cpu_load = self.get_cpu_percentage()
                gpu_load = self.get_gpu_load()
                
                # Calculate voltage change
                voltage_change = voltage - baseline_voltage
                
                # Display monitoring info
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Voltage: {voltage}V ({voltage_change:+.2f}V) | "
                      f"CPU Load: {cpu_load:.1f} | "
                      f"GPU Load: {gpu_load}%")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(2)
    
    def start_stress(self, duration=60):
        """Start the voltage stress test"""
        print(f"🚀 Starting Voltage Stress Test (Duration: {duration}s)")
        print("=" * 60)
        print("🔥 Maximum CPU, GPU, and Memory Load")
        print("📈 Designed to increase voltage intake")
        print("=" * 60)
        
        # Start CPU stress processes (one per core)
        cpu_count = multiprocessing.cpu_count()
        print(f"Starting {cpu_count} CPU stress processes...")
        
        for i in range(cpu_count):
            process = multiprocessing.Process(target=self.cpu_stress_process, args=(i+1,))
            process.daemon = True
            process.start()
            self.cpu_processes.append(process)
        
        # Start GPU stress
        gpu_thread = threading.Thread(target=self.gpu_stress)
        gpu_thread.daemon = True
        gpu_thread.start()
        
        # Start memory stress
        memory_thread = threading.Thread(target=self.memory_stress)
        memory_thread.daemon = True
        memory_thread.start()
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("✅ All stress components started")
        print("📊 Monitoring voltage changes...")
        print("⏰ Test will run for", duration, "seconds")
        print("🛑 Press Ctrl+C to stop early")
        print("=" * 60)
        
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
        
        # Stop CPU processes
        for process in self.cpu_processes:
            try:
                process.terminate()
                process.join(timeout=2)
            except:
                process.kill()
        
        # Cleanup temporary files
        try:
            os.remove('/tmp/gpu_io_stress.py')
            os.remove('/tmp/memory_stress.py')
        except:
            pass
        
        print("✅ Stress test stopped")
        print("📊 Final voltage reading:")
        
        # Show final voltage
        try:
            final_voltage = self.get_voltage()
            print(f"   Final Voltage: {final_voltage}V")
        except Exception as e:
            print(f"   Error reading final voltage: {e}")

def signal_handler(signum, frame):
    """Handle Ctrl+C"""
    print("\n⚠️  Received interrupt signal")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    duration = 60  # 1 minute default
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 voltage_stress_test.py [duration_seconds]")
            print("Default duration: 60 seconds")
            sys.exit(1)
    
    # Create and run stress test
    stress_test = VoltageStressTest()
    stress_test.start_stress(duration)
