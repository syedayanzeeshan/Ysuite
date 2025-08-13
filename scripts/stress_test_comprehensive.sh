#!/bin/bash

# Comprehensive Stress Test with OpenCL and Vulkan
# Monitors system with ytop in real-time

echo "🔥 Comprehensive Stress Test - OpenCL + Vulkan + System Monitoring"
echo "=================================================================="
echo ""

# Check if required tools are available
echo "🔧 Checking prerequisites..."

# Check OpenCL
if ! command -v clinfo >/dev/null 2>&1; then
    echo "❌ clinfo not found. Installing..."
    sudo apt update && sudo apt install -y clinfo
fi

# Check Vulkan
if ! command -v vulkaninfo >/dev/null 2>&1; then
    echo "❌ vulkaninfo not found. Installing..."
    sudo apt update && sudo apt install -y vulkan-tools
fi

# Check YSuite
if ! command -v ytop >/dev/null 2>&1; then
    echo "❌ ytop not found. Installing YSuite..."
    cd ~/Ysuite
    sudo ./install_ysuite.sh
fi

# Check stress-ng
if ! command -v stress-ng >/dev/null 2>&1; then
    echo "❌ stress-ng not found. Installing..."
    sudo apt update && sudo apt install -y stress-ng
fi

echo "✅ All prerequisites available"
echo ""

# Create OpenCL stress test
echo "🔧 Creating OpenCL stress test..."
cat > opencl_stress.c << 'EOF'
#include <CL/cl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BUFFER_SIZE 1024*1024
#define ITERATIONS 1000

int main() {
    cl_platform_id platform;
    cl_device_id device;
    cl_context context;
    cl_command_queue queue;
    cl_int err;
    
    printf("🔥 Starting OpenCL Stress Test...\n");
    
    // Get platform and device
    err = clGetPlatformIDs(1, &platform, NULL);
    if (err != CL_SUCCESS) {
        printf("❌ Failed to get platform: %d\n", err);
        return 1;
    }
    
    err = clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU, 1, &device, NULL);
    if (err != CL_SUCCESS) {
        printf("❌ Failed to get GPU device: %d\n", err);
        return 1;
    }
    
    // Create context and command queue
    context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
    if (err != CL_SUCCESS) {
        printf("❌ Failed to create context: %d\n", err);
        return 1;
    }
    
    queue = clCreateCommandQueue(context, device, 0, &err);
    if (err != CL_SUCCESS) {
        printf("❌ Failed to create command queue: %d\n", err);
        return 1;
    }
    
    // Create buffers
    cl_mem input_buffer = clCreateBuffer(context, CL_MEM_READ_ONLY, BUFFER_SIZE, NULL, &err);
    cl_mem output_buffer = clCreateBuffer(context, CL_MEM_WRITE_ONLY, BUFFER_SIZE, NULL, &err);
    
    if (err != CL_SUCCESS) {
        printf("❌ Failed to create buffers: %d\n", err);
        return 1;
    }
    
    // Create simple kernel
    const char* kernel_source = 
        "__kernel void vector_add(__global const float* a, __global float* result) {\n"
        "    int gid = get_global_id(0);\n"
        "    result[gid] = a[gid] + 1.0f;\n"
        "}\n";
    
    cl_program program = clCreateProgramWithSource(context, 1, &kernel_source, NULL, &err);
    if (err != CL_SUCCESS) {
        printf("❌ Failed to create program: %d\n", err);
        return 1;
    }
    
    err = clBuildProgram(program, 1, &device, NULL, NULL, NULL);
    if (err != CL_SUCCESS) {
        printf("❌ Failed to build program: %d\n", err);
        return 1;
    }
    
    cl_kernel kernel = clCreateKernel(program, "vector_add", &err);
    if (err != CL_SUCCESS) {
        printf("❌ Failed to create kernel: %d\n", err);
        return 1;
    }
    
    // Prepare data
    float* input_data = (float*)malloc(BUFFER_SIZE);
    float* output_data = (float*)malloc(BUFFER_SIZE);
    
    for (int i = 0; i < BUFFER_SIZE / sizeof(float); i++) {
        input_data[i] = (float)i;
    }
    
    // Set kernel arguments
    clSetKernelArg(kernel, 0, sizeof(cl_mem), &input_buffer);
    clSetKernelArg(kernel, 1, sizeof(cl_mem), &output_buffer);
    
    size_t global_size = BUFFER_SIZE / sizeof(float);
    
    printf("🔥 Running OpenCL stress test for %d iterations...\n", ITERATIONS);
    
    clock_t start = clock();
    
    // Run stress test
    for (int i = 0; i < ITERATIONS; i++) {
        // Write data
        clEnqueueWriteBuffer(queue, input_buffer, CL_TRUE, 0, BUFFER_SIZE, input_data, 0, NULL, NULL);
        
        // Run kernel
        clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &global_size, NULL, 0, NULL, NULL);
        
        // Read results
        clEnqueueReadBuffer(queue, output_buffer, CL_TRUE, 0, BUFFER_SIZE, output_data, 0, NULL, NULL);
        
        if (i % 100 == 0) {
            printf("  Progress: %d/%d iterations\n", i, ITERATIONS);
        }
    }
    
    clock_t end = clock();
    double time_spent = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("✅ OpenCL stress test completed in %.2f seconds\n", time_spent);
    printf("   Average time per iteration: %.2f ms\n", (time_spent * 1000) / ITERATIONS);
    
    // Cleanup
    clReleaseMemObject(input_buffer);
    clReleaseMemObject(output_buffer);
    clReleaseKernel(kernel);
    clReleaseProgram(program);
    clReleaseCommandQueue(queue);
    clReleaseContext(context);
    
    free(input_data);
    free(output_data);
    
    return 0;
}
EOF

# Compile OpenCL stress test
echo "🔧 Compiling OpenCL stress test..."
gcc -o opencl_stress opencl_stress.c -lOpenCL

if [ $? -eq 0 ]; then
    echo "✅ OpenCL stress test compiled successfully"
else
    echo "❌ Failed to compile OpenCL stress test"
    exit 1
fi

# Create Vulkan stress test
echo "🔧 Creating Vulkan stress test..."
cat > vulkan_stress.c << 'EOF'
#include <vulkan/vulkan.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BUFFER_SIZE 1024*1024
#define ITERATIONS 500

int main() {
    VkInstance instance;
    VkPhysicalDevice physicalDevice = VK_NULL_HANDLE;
    VkDevice device;
    VkResult result;
    
    printf("🔥 Starting Vulkan Stress Test...\n");
    
    // Create instance
    VkInstanceCreateInfo createInfo = {
        .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        .pApplicationInfo = NULL,
        .enabledLayerCount = 0,
        .enabledExtensionCount = 0
    };
    
    result = vkCreateInstance(&createInfo, NULL, &instance);
    if (result != VK_SUCCESS) {
        printf("❌ Failed to create Vulkan instance: %d\n", result);
        return 1;
    }
    
    // Enumerate physical devices
    uint32_t deviceCount = 0;
    vkEnumeratePhysicalDevices(instance, &deviceCount, NULL);
    
    if (deviceCount == 0) {
        printf("❌ No Vulkan devices found\n");
        vkDestroyInstance(instance, NULL);
        return 1;
    }
    
    VkPhysicalDevice* devices = malloc(sizeof(VkPhysicalDevice) * deviceCount);
    vkEnumeratePhysicalDevices(instance, &deviceCount, devices);
    
    // Find Mali device
    for (uint32_t i = 0; i < deviceCount; i++) {
        VkPhysicalDeviceProperties deviceProperties;
        vkGetPhysicalDeviceProperties(devices[i], &deviceProperties);
        
        if (strstr(deviceProperties.deviceName, "Mali") != NULL) {
            physicalDevice = devices[i];
            printf("✅ Found Mali device: %s\n", deviceProperties.deviceName);
            break;
        }
    }
    
    if (physicalDevice == VK_NULL_HANDLE) {
        printf("❌ No Mali device found\n");
        free(devices);
        vkDestroyInstance(instance, NULL);
        return 1;
    }
    
    // Create logical device
    VkDeviceCreateInfo deviceCreateInfo = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
        .queueCreateInfoCount = 0,
        .enabledExtensionCount = 0
    };
    
    result = vkCreateDevice(physicalDevice, &deviceCreateInfo, NULL, &device);
    if (result != VK_SUCCESS) {
        printf("❌ Failed to create logical device: %d\n", result);
        free(devices);
        vkDestroyInstance(instance, NULL);
        return 1;
    }
    
    printf("🔥 Running Vulkan stress test for %d iterations...\n", ITERATIONS);
    
    clock_t start = clock();
    
    // Simulate Vulkan operations
    for (int i = 0; i < ITERATIONS; i++) {
        // Simulate buffer operations
        VkBufferCreateInfo bufferInfo = {
            .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
            .size = BUFFER_SIZE,
            .usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT,
            .sharingMode = VK_SHARING_MODE_EXCLUSIVE
        };
        
        VkBuffer buffer;
        result = vkCreateBuffer(device, &bufferInfo, NULL, &buffer);
        
        if (result == VK_SUCCESS) {
            vkDestroyBuffer(device, buffer, NULL);
        }
        
        if (i % 100 == 0) {
            printf("  Progress: %d/%d iterations\n", i, ITERATIONS);
        }
    }
    
    clock_t end = clock();
    double time_spent = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("✅ Vulkan stress test completed in %.2f seconds\n", time_spent);
    printf("   Average time per iteration: %.2f ms\n", (time_spent * 1000) / ITERATIONS);
    
    // Cleanup
    vkDestroyDevice(device, NULL);
    free(devices);
    vkDestroyInstance(instance, NULL);
    
    return 0;
}
EOF

# Compile Vulkan stress test
echo "🔧 Compiling Vulkan stress test..."
gcc -o vulkan_stress vulkan_stress.c -lvulkan

if [ $? -eq 0 ]; then
    echo "✅ Vulkan stress test compiled successfully"
else
    echo "❌ Failed to compile Vulkan stress test (this is normal if Vulkan headers aren't installed)"
    echo "   Continuing with OpenCL stress test only..."
fi

echo ""
echo "🚀 Starting Comprehensive Stress Test..."
echo "======================================"
echo ""

# Start ytop monitoring in background
echo "📊 Starting ytop monitoring in background..."
ytop 2 > ytop_output.log 2>&1 &
YTOP_PID=$!

# Wait a moment for ytop to start
sleep 3

echo "🔥 Phase 1: CPU Stress Test (30 seconds)"
echo "----------------------------------------"
stress-ng --cpu 8 --timeout 30 --metrics-brief &
STRESS_PID=$!

# Monitor during CPU stress
for i in {1..30}; do
    echo -ne "  CPU Stress: $i/30 seconds\r"
    sleep 1
done
echo ""

wait $STRESS_PID

echo ""
echo "🔥 Phase 2: OpenCL Stress Test (60 seconds)"
echo "-------------------------------------------"
./opencl_stress &
OPENCL_PID=$!

# Monitor during OpenCL stress
for i in {1..60}; do
    echo -ne "  OpenCL Stress: $i/60 seconds\r"
    sleep 1
done
echo ""

wait $OPENCL_PID

if [ -f "./vulkan_stress" ]; then
    echo ""
    echo "🔥 Phase 3: Vulkan Stress Test (60 seconds)"
    echo "--------------------------------------------"
    ./vulkan_stress &
    VULKAN_PID=$!
    
    # Monitor during Vulkan stress
    for i in {1..60}; do
        echo -ne "  Vulkan Stress: $i/60 seconds\r"
        sleep 1
    done
    echo ""
    
    wait $VULKAN_PID
fi

echo ""
echo "🔥 Phase 4: Combined Stress Test (30 seconds)"
echo "---------------------------------------------"
# Run multiple stress tests simultaneously
stress-ng --cpu 4 --gpu 1 --timeout 30 --metrics-brief &
./opencl_stress &
if [ -f "./vulkan_stress" ]; then
    ./vulkan_stress &
fi

# Monitor during combined stress
for i in {1..30}; do
    echo -ne "  Combined Stress: $i/30 seconds\r"
    sleep 1
done
echo ""

# Wait for all stress tests to complete
wait

echo ""
echo "🛑 Stopping ytop monitoring..."
kill $YTOP_PID 2>/dev/null

echo ""
echo "📊 Stress Test Results"
echo "====================="
echo ""

# Show ytop output summary
if [ -f "ytop_output.log" ]; then
    echo "📈 YTop Monitoring Log (last 20 lines):"
    echo "----------------------------------------"
    tail -20 ytop_output.log
    echo ""
fi

# Show system status
echo "🔍 Final System Status:"
echo "----------------------"

# Check temperatures
echo "🌡️  Temperature Check:"
for i in {0..6}; do
    if [ -f "/sys/class/thermal/thermal_zone$i/temp" ]; then
        temp=$(cat "/sys/class/thermal/thermal_zone$i/temp")
        temp_c=$(echo "scale=1; $temp/1000" | bc -l 2>/dev/null || echo "N/A")
        echo "   Thermal zone $i: ${temp_c}°C"
    fi
done

# Check GPU status
echo ""
echo "🎮 GPU Status:"
if [ -f "/sys/class/devfreq/fb000000.gpu-mali/cur_freq" ]; then
    freq=$(cat "/sys/class/devfreq/fb000000.gpu-mali/cur_freq")
    freq_mhz=$(echo "scale=0; $freq/1000000" | bc -l 2>/dev/null || echo "N/A")
    echo "   GPU Frequency: ${freq_mhz} MHz"
fi

if [ -f "/sys/class/devfreq/fb000000.gpu-mali/load" ]; then
    load=$(cat "/sys/class/devfreq/fb000000.gpu-mali/load")
    echo "   GPU Load: ${load}%"
fi

# Check power
echo ""
echo "⚡ Power Status:"
if [ -f "/sys/class/power_supply/usb-c0/voltage_now" ]; then
    voltage=$(cat "/sys/class/power_supply/usb-c0/voltage_now")
    voltage_v=$(echo "scale=2; $voltage/1000000" | bc -l 2>/dev/null || echo "N/A")
    echo "   Voltage: ${voltage_v}V"
fi

if [ -f "/sys/class/power_supply/usb-c0/current_now" ]; then
    current=$(cat "/sys/class/power_supply/usb-c0/current_now")
    current_ma=$(echo "scale=1; $current/1000" | bc -l 2>/dev/null || echo "N/A")
    echo "   Current: ${current_ma}mA"
fi

# Check fan
echo ""
echo "💨 Fan Status:"
fan_paths=(
    "/sys/class/thermal/cooling_device0/cur_state"
    "/sys/class/thermal/cooling_device1/cur_state"
    "/sys/class/hwmon/hwmon*/fan1_input"
    "/sys/class/hwmon/hwmon*/pwm1"
)

fan_found=false
for path in "${fan_paths[@]}"; do
    if [ -f "$path" ]; then
        fan_value=$(cat "$path" 2>/dev/null)
        if [ "$fan_value" -gt 0 ] 2>/dev/null; then
            echo "   Fan: Running (${fan_value})"
            fan_found=true
            break
        fi
    fi
done

if [ "$fan_found" = false ]; then
    echo "   Fan: Not detected or not running"
fi

echo ""
echo "✅ Comprehensive Stress Test Completed!"
echo "======================================"
echo ""
echo "📋 Summary:"
echo "  • CPU Stress: 30 seconds"
echo "  • OpenCL Stress: 60 seconds"
if [ -f "./vulkan_stress" ]; then
    echo "  • Vulkan Stress: 60 seconds"
fi
echo "  • Combined Stress: 30 seconds"
echo "  • Total Duration: ~3 minutes"
echo ""
echo "📊 Check ytop_output.log for detailed monitoring data"
echo "🔥 System stress tested with OpenCL and Vulkan workloads"
echo "⚡ Power, temperature, and performance monitored in real-time"
