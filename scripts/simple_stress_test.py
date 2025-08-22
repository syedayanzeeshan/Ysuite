#!/usr/bin/env python3
"""
Simple Stress Test for Rock 5B+
Raises CPU usage to ~60% and utilizes GPU
"""

import time
import threading
import subprocess
import os
import signal
import sys
from datetime import datetime

class SimpleStressTest:
    def __init__(self):
        self.running = True
        self.cpu_threads = []
        self.gpu_process = None
        
    def cpu_stress(self, thread_id):
        """CPU stress function - mathematical calculations"""
        print(f"Starting CPU stress thread {thread_id}")
        while self.running:
            # Very intensive mathematical calculations to stress CPU
            result = 0
            for i in range(10000000):  # 10M iterations for maximum stress
                result += i * i * 3.14159
                # No delays - maximum CPU usage
        print(f"CPU stress thread {thread_id} stopped")
    
    def get_gpu_load(self):
        """Get GPU load percentage"""
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
    
    def gpu_stress(self):
        """GPU stress using glmark2"""
        print("Starting GPU stress (glmark2)")
        try:
            # Run glmark2 in background
            self.gpu_process = subprocess.Popen(['glmark2', '--duration', '60', '--fullscreen'], 
                                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("GPU stress using glmark2")
        except Exception as e:
            print(f"GPU stress failed: {e}")
            # Fallback: simple GPU utilization
            try:
                # Simple OpenCL test program
                opencl_code = """
                __kernel void stress_test(__global float* output) {
                    int gid = get_global_id(0);
                    float x = (float)gid;
                    float result = 0.0f;
                    
                    for(int i = 0; i < 1000; i++) {
                        result += sin(x + i) * cos(x - i);
                    }
                    output[gid] = result;
                }
                """
                
                # Write OpenCL code to temporary file
                with open('/tmp/gpu_stress.cl', 'w') as f:
                    f.write(opencl_code)
                
                # Run OpenCL stress test
                opencl_test = """
import pyopencl as cl
import numpy as np

# Create context and command queue
ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

# Read kernel
with open('/tmp/gpu_stress.cl', 'r') as f:
    kernel_src = f.read()

# Compile program
prg = cl.Program(ctx, kernel_src).build()

# Create buffers
size = 10000
output = np.zeros(size, dtype=np.float32)
output_buf = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, output.nbytes)

# Run kernel multiple times
for i in range(100):
    prg.stress_test(queue, (size,), None, output_buf)
    queue.finish()
    print(f"GPU iteration {i+1}/100")
    time.sleep(0.1)
"""
                
                # Write Python test to file
                with open('/tmp/gpu_test.py', 'w') as f:
                    f.write(opencl_test)
                
                # Run GPU test
                self.gpu_process = subprocess.Popen(['python3', '/tmp/gpu_test.py'])
                
            except Exception as e:
                print(f"GPU stress not available: {e}")
    
    def get_cpu_percentage(self):
        """Get CPU usage percentage"""
        try:
            # Read CPU stats
            with open('/proc/stat', 'r') as f:
                lines = f.readlines()
            
            # Get first line (total CPU)
            cpu_line = lines[0].split()[1:]
            cpu_times = [int(x) for x in cpu_line]
            
            # Calculate total and idle time
            total_time = sum(cpu_times)
            idle_time = cpu_times[3]  # idle time
            
            # Store previous values for calculation
            if not hasattr(self, 'prev_total'):
                self.prev_total = total_time
                self.prev_idle = idle_time
                return 0.0
            
            # Calculate CPU usage percentage
            total_diff = total_time - self.prev_total
            idle_diff = idle_time - self.prev_idle
            
            if total_diff > 0:
                cpu_percent = 100.0 * (1.0 - idle_diff / total_diff)
            else:
                cpu_percent = 0.0
            
            # Update previous values
            self.prev_total = total_time
            self.prev_idle = idle_time
            
            return cpu_percent
            
        except Exception as e:
            return 0.0

    def get_power_readings(self):
        """Get real-time power readings from multiple sources"""
        power_info = {
            'voltage_input': 0,
            'current_input': 0,
            'power_input': 0,
            'power_source': 'Unknown'
        }
        
        try:
            # Try to get actual current from system load estimation
            # Since hardware current sensors seem to show max values
            
            # Get CPU usage for power estimation
            cpu_percent = self.get_cpu_percentage()
            
            # Base power consumption (idle)
            base_current = 0.6  # 600mA idle
            
            # Estimate current based on CPU usage
            # Assume linear relationship: 0% CPU = 600mA, 100% CPU = 2400mA
            estimated_current = base_current + (cpu_percent / 100.0) * 1.8
            
            # Use actual voltage from power supply
            try:
                with open('/sys/class/power_supply/tcpm-source-psy-4-0022/voltage_now', 'r') as f:
                    voltage_uv = int(f.read().strip())
                    power_info['voltage_input'] = voltage_uv / 1000000.0  # Convert μV to V
            except:
                power_info['voltage_input'] = 5.0  # Default voltage
            
            power_info['current_input'] = estimated_current
            power_info['power_input'] = power_info['voltage_input'] * power_info['current_input']
            power_info['power_source'] = 'Estimated from CPU Load'
                
        except Exception as e:
            print(f"Power reading error: {e}")
        
        return power_info

    def monitor_system(self):
        """Monitor system resources and power"""
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
                
                # Get power readings
                power_info = self.get_power_readings()
                
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
    
    def start_stress(self, duration=300):  # 5 minutes default
        """Start the stress test"""
        print(f"🚀 Starting Simple Stress Test (Duration: {duration}s)")
        print("=" * 50)
        
        # Start CPU stress threads (4 threads for ~60% CPU)
        for i in range(4):
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
        print("📊 Monitoring system resources...")
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
        
        # Cleanup temporary files
        try:
            os.remove('/tmp/gpu_stress.cl')
            os.remove('/tmp/gpu_test.py')
        except:
            pass
        
        print("✅ Stress test stopped")
        print("📊 Final system status:")
        
        # Show final status
        try:
            # Get final CPU percentage
            cpu_percent = self.get_cpu_percentage()
            print(f"   CPU Usage: {cpu_percent:.1f}%")
            
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
            
            # Get final GPU load
            gpu_load = self.get_gpu_load()
            print(f"   GPU Load: {gpu_load}%")
            
            # Show final power status
            power_info = self.get_power_readings()
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
            print("Usage: python3 simple_stress_test.py [duration_seconds]")
            print("Default duration: 300 seconds (5 minutes)")
            sys.exit(1)
    
    # Create and run stress test
    stress_test = SimpleStressTest()
    stress_test.start_stress(duration)
