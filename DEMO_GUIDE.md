# 🎯 Demo & Testing Guide

## 🚀 **Quick Start (5-minute demo)**

```bash
# 1. Setup environment
cd /home/yan/kernel-logging-env
source bin/activate

# 2. Test all components
cd scripts/analysis && python kernel_log_analyzer.py
cd ../monitoring && python build_monitor.py
cd ../utils && python kernel_config.py
```

## 🧪 **Comprehensive Testing**

### **Test 1: Error Detection**
```bash
cd scripts/analysis
python kernel_log_analyzer.py
```
**Expected**: Rich console output with error categorization

### **Test 2: Build Monitoring**
```bash
cd scripts/monitoring
python build_monitor.py
```
**Expected**: Real-time build progress with completion report

### **Test 3: Configuration Management**
```bash
cd scripts/utils
python kernel_config.py
```
**Expected**: Kernel validation and config backup

## 🎭 **Interactive Demo Scenarios**

### **Demo 1: Error Simulation**
```bash
cd scripts/analysis
python -c "
from kernel_log_analyzer import KernelLogAnalyzer
analyzer = KernelLogAnalyzer()
errors = [
    'Kernel panic: unable to mount root filesystem',
    'rk3588-pcie: PCIe link training failed',
    'mali-gpu: GPU fault detected',
    'thermal: Critical temperature reached on RK3588'
]
for error in errors:
    criticality, pattern = analyzer.analyze_log_line(error)
    analyzer.log_error(error, criticality, {'board': 'radxa-rock5b+'})
    print(f'Detected: {criticality.upper()} - {error}')
"
```

### **Demo 2: Log Analysis**
```bash
# View generated logs
cat logs/critical.log
cat logs/error.log
cat logs/warning.log
```

### **Demo 3: Build Performance**
```bash
cd scripts/monitoring
python build_monitor.py
# Watch real-time build progress and final report
```

## 📊 **Performance Testing**

### **Accuracy Test**
```bash
cd scripts/analysis
python -c "
from kernel_log_analyzer import KernelLogAnalyzer
import time
analyzer = KernelLogAnalyzer()
test_cases = [
    ('Kernel panic: unable to mount root filesystem', 'critical'),
    ('ERROR: Failed to load module', 'error'),
    ('WARNING: Deprecated API', 'warning'),
    ('rk3588-pcie: PCIe link training failed', 'critical')
]
start = time.time()
correct = sum(1 for error, expected in test_cases 
             if analyzer.analyze_log_line(error)[0] == expected)
accuracy = (correct / len(test_cases)) * 100
duration = time.time() - start
print(f'Accuracy: {accuracy:.1f}% ({correct}/{len(test_cases)})')
print(f'Speed: {len(test_cases)/duration:.1f} patterns/second')
"
```

## 🎪 **Complete Demo Script**

```bash
# Create demo script
cat > demo_complete.py << 'EOF'
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path("scripts/analysis")))
from analysis.kernel_log_analyzer import KernelLogAnalyzer

print("🎯 Enhanced Kernel Logging System Demo")
print("=" * 40)

# Test error detection
analyzer = KernelLogAnalyzer()
rock5b_errors = [
    "Kernel panic: unable to mount root filesystem",
    "rk3588-pcie: PCIe link training failed", 
    "mali-gpu: GPU fault detected",
    "thermal: Critical temperature reached on RK3588"
]

print("\n🔍 Error Detection Test:")
for error in rock5b_errors:
    criticality, pattern = analyzer.analyze_log_line(error)
    analyzer.log_error(error, criticality, {"board": "radxa-rock5b+"})
    print(f"  {criticality.upper()}: {error}")

print("\n✅ Demo completed! Check logs/ directory for results.")
EOF

# Run complete demo
python demo_complete.py
```

## 🎯 **Demo Checklist**

### **Pre-Demo**
- [ ] Environment activated
- [ ] Kernel source available
- [ ] All scripts working
- [ ] Logs directory exists

### **Demo Flow**
1. **Error Detection** - Show pattern recognition
2. **Build Monitoring** - Show real-time tracking  
3. **Configuration** - Show automated management
4. **Log Analysis** - Show intelligent reporting

### **Key Points**
- **Real-time vs post-mortem** analysis
- **Hardware-specific** error patterns
- **Automated management** vs manual work
- **Rich context** vs basic logging
- **Integrated workflow** vs standalone tools

## 🚀 **Quick Commands**

```bash
# 1-minute demo
cd /home/yan/kernel-logging-env
source bin/activate
python demo_complete.py

# 5-minute detailed demo  
cd scripts/analysis && python kernel_log_analyzer.py
cd ../monitoring && python build_monitor.py
cd ../utils && python kernel_config.py

# View results
ls -la logs/
cat logs/critical.log
cat logs/build/build_report.txt
```

This demo guide shows how to test and demonstrate all enhanced features! 🎉 