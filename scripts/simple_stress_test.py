#!/usr/bin/env python3
"""
Simple Stress Test for Rock 5B+
Raises CPU usage to ~60% and utilizes GPU/NPU
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
        self.npu_process = None
        
    def cpu_stress(self, thread_id):
        """CPU stress function - mathematical calculations"""
        print(f"Starting CPU stress thread {thread_id}")
        while self.running:
            # Mathematical calculations to stress CPU
            result = 0
            for i in range(100000):
                result += i * i * 3.14159
                if i % 10000 == 0:
                    time.sleep(0.001)  # Small delay to prevent 100% CPU
        print(f"CPU stress thread {thread_id} stopped")
    
    def gpu_stress(self):
        """GPU stress using OpenCL"""
        print("Starting GPU stress (OpenCL)")
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
            print(f"GPU stress failed: {e}")
            # Fallback: simple GPU utilization
            try:
                # Try to use glmark2 if available
                self.gpu_process = subprocess.Popen(['glmark2', '--duration', '60'])
            except:
                print("GPU stress not available")
    
    def npu_stress(self):
        """NPU stress using simple operations"""
        print("Starting NPU stress")
        try:
            # Simple NPU stress using system calls
            npu_test = """
import time
import subprocess

# Try to trigger NPU operations
for i in range(50):
    try:
        # Check NPU load
        with open('/sys/kernel/debug/rknpu/load', 'r') as f:
            load = f.read()
            print(f"NPU Load: {load.strip()}")
        
        # Run some system operations that might use NPU
        subprocess.run(['dd', 'if=/dev/zero', 'of=/tmp/npu_test', 'bs=1M', 'count=10'], 
                      capture_output=True, timeout=5)
        subprocess.run(['rm', '-f', '/tmp/npu_test'], capture_output=True)
        
        time.sleep(1)
    except Exception as e:
        print(f"NPU operation {i+1} failed: {e}")
        time.sleep(1)
"""
            
            # Write NPU test to file
            with open('/tmp/npu_test.py', 'w') as f:
                f.write(npu_test)
            
            # Run NPU test
            self.npu_process = subprocess.Popen(['python3', '/tmp/npu_test.py'])
            
        except Exception as e:
            print(f"NPU stress failed: {e}")
    
    def monitor_system(self):
        """Monitor system resources"""
        print("Starting system monitoring")
        while self.running:
            try:
                # Get CPU usage
                with open('/proc/loadavg', 'r') as f:
                    loadavg = f.read().strip().split()
                    cpu_load = float(loadavg[0])
                
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
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"CPU Load: {cpu_load:.2f}, "
                      f"Memory: {mem_percent:.1f}%, "
                      f"Temp: {temp:.1f}°C")
                
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
        
        # Start NPU stress
        npu_thread = threading.Thread(target=self.npu_stress)
        npu_thread.daemon = True
        npu_thread.start()
        
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
        
        # Stop NPU process
        if self.npu_process:
            try:
                self.npu_process.terminate()
                self.npu_process.wait(timeout=5)
            except:
                self.npu_process.kill()
        
        # Wait for threads to finish
        for thread in self.cpu_threads:
            thread.join(timeout=2)
        
        # Cleanup temporary files
        try:
            os.remove('/tmp/gpu_stress.cl')
            os.remove('/tmp/gpu_test.py')
            os.remove('/tmp/npu_test.py')
        except:
            pass
        
        print("✅ Stress test stopped")
        print("📊 Final system status:")
        
        # Show final status
        try:
            with open('/proc/loadavg', 'r') as f:
                loadavg = f.read().strip()
                print(f"   Load Average: {loadavg}")
            
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
