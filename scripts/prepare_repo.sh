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

# Initialize kernel as submodule
echo_info "Setting up kernel source as submodule..."
if [ -d "linux/.git" ]; then
    rm -rf linux/.git
fi

# Initialize git submodule
git submodule init
git submodule add https://github.com/Joshua-Riek/linux-rockchip.git linux
cd linux
git checkout rk3588
cd ..

# Add our kernel modifications
echo_info "Adding kernel modifications..."
cp -r linux/drivers/misc/rock5b_*.c linux/drivers/misc/
cp -r linux/arch/arm64/boot/dts/rockchip/overlay/rock-5b-plus-enhanced.dts linux/arch/arm64/boot/dts/rockchip/overlay/

# Update Makefiles and Kconfig
echo_info "Updating build configuration..."
git add linux/drivers/misc/Makefile
git add linux/drivers/misc/Kconfig

# Add all configuration files
echo_info "Adding configuration files..."
git add configs/

# Add all scripts
echo_info "Adding scripts..."
git add scripts/

# Add documentation
echo_info "Adding documentation..."
git add README.md INSTRUCTIONS.md QUICK-START.md

echo_success "Repository prepared for pushing"
echo "
Next steps:
1. Create a Personal Access Token on GitHub
2. Configure the remote with your token:
   git remote set-url origin https://[USERNAME]:[TOKEN]@github.com/syedayanzeeshan/RadxaAt.git
3. Push the changes:
   git push -u origin main"

# Show current status
echo -e "\nCurrent repository status:"
git status