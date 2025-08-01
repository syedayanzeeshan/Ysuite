#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_step() {
    echo -e "\n${YELLOW}[STEP]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo_error "Please run as root"
fi

# Ensure we're in the right directory
cd "$(dirname "$0")/.."
WORK_DIR=$(pwd)

# Step 1: Prepare build environment
echo_step "Preparing build environment..."
./scripts/prepare_environment.sh || {
    echo_error "Failed to prepare environment"
}
echo_success "Build environment prepared"

# Step 2: Build kernel
echo_step "Building kernel..."
./scripts/build_kernel.sh || {
    echo_error "Failed to build kernel"
}
echo_success "Kernel built successfully"

# Step 3: Modify image
echo_step "Modifying Ubuntu image..."
./scripts/modify_image.sh || {
    echo_error "Failed to modify image"
}
echo_success "Image modified successfully"

# Print final status
echo -e "\n${GREEN}Build completed successfully!${NC}"
echo "Modified image is available at: build/ubuntu-22.04-enhanced-rock-5b-plus.img.xz"
echo -e "\nTo install on Rock 5B Plus:"
echo "1. Flash the image to an SD card or eMMC:"
echo "   xzcat ubuntu-22.04-enhanced-rock-5b-plus.img.xz | sudo dd of=/dev/sdX bs=4M status=progress"
echo "2. Boot the board"
echo "3. The system will automatically:"
echo "   - Switch to Mali GPU driver"
echo "   - Enable enhanced logging"
echo "   - Start power monitoring"
echo "   - Enable crash reporting"
echo -e "\nLogs will be available at:"
echo "- Kernel logs: /var/log/kernel/kernel.log"
echo "- Power monitoring: /var/log/kernel/power.log"
echo "- Crash reports: /var/log/kernel/crashes/"