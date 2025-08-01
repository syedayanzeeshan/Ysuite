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

# Create new directory structure
echo_info "Creating directory structure..."
mkdir -p kernel-mods/drivers/misc
mkdir -p kernel-mods/arch/arm64/boot/dts/rockchip/overlay

# Copy our kernel modifications to new structure
echo_info "Copying kernel modifications..."
cp linux/drivers/misc/rock5b_*.c kernel-mods/drivers/misc/
cp linux/drivers/misc/Makefile kernel-mods/drivers/misc/Makefile.patch
cp linux/drivers/misc/Kconfig kernel-mods/drivers/misc/Kconfig.patch
cp linux/arch/arm64/boot/dts/rockchip/overlay/rock-5b-plus-enhanced.dts kernel-mods/arch/arm64/boot/dts/rockchip/overlay/

# Create patches directory
echo_info "Creating patches directory..."
mkdir -p patches
cat > patches/0001-add-rock5b-drivers.patch << EOF
diff --git a/drivers/misc/Kconfig b/drivers/misc/Kconfig
--- a/drivers/misc/Kconfig
+++ b/drivers/misc/Kconfig
$(diff linux/drivers/misc/Kconfig.orig linux/drivers/misc/Kconfig || true)

diff --git a/drivers/misc/Makefile b/drivers/misc/Makefile
--- a/drivers/misc/Makefile
+++ b/drivers/misc/Makefile
$(diff linux/drivers/misc/Makefile.orig linux/drivers/misc/Makefile || true)
EOF

# Add all files
echo_info "Adding files to repository..."
git add kernel-mods/
git add patches/
git add configs/
git add scripts/
git add README.md INSTRUCTIONS.md QUICK-START.md .gitignore

# Create commit
echo_info "Creating commit..."
git commit -m "Add Rock 5B Plus enhancements

- Kernel modifications:
  * Enhanced logging system
  * Power monitoring
  * Crash reporting
  * Mali GPU driver support
- Build and configuration scripts
- Documentation and installation guides
- Patch files for kernel integration"

echo_success "Repository reorganized and ready for pushing"
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