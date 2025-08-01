#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Create .gitignore for build artifacts
echo_info "Creating .gitignore..."
cat > .gitignore << EOF
*.o
*.ko
*.mod
*.mod.c
*.cmd
.tmp_versions/
modules.order
Module.symvers
build/
*.img
*.img.xz
EOF

# Add all our modified kernel files
echo_info "Adding kernel modifications..."
git add linux/drivers/misc/rock5b_*.c
git add linux/drivers/misc/Makefile
git add linux/drivers/misc/Kconfig
git add linux/arch/arm64/boot/dts/rockchip/overlay/rock-5b-plus-enhanced.dts

# Add all configuration files
echo_info "Adding configuration files..."
git add configs/etc/apt/preferences.d/mali
git add configs/etc/modprobe.d/panfrost.conf
git add configs/etc/environment
git add configs/etc/systemd/system/*.service

# Add all scripts
echo_info "Adding scripts..."
git add scripts/*.py
git add scripts/*.sh

# Add documentation
echo_info "Adding documentation..."
git add README.md INSTRUCTIONS.md QUICK-START.md

# Create commit
echo_info "Creating commit..."
git commit -m "Add Rock 5B Plus kernel enhancements

- Added kernel logging system with rotation
- Implemented power monitoring (voltage/current)
- Added crash reporting with boot-time detection
- Configured Mali GPU driver with OpenCL/Vulkan support
- Added build and verification scripts
- Added comprehensive documentation"

echo_success "Repository prepared for pushing"
echo "
Next steps:
1. Create a Personal Access Token on GitHub:
   https://github.com/settings/tokens
   
2. Configure the remote with your token:
   git remote set-url origin https://[USERNAME]:[TOKEN]@github.com/syedayanzeeshan/RadxaAt.git
   
3. Push the changes:
   git push -u origin main"

# Show current status
echo -e "\nCurrent repository status:"
git status