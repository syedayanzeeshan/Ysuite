#!/bin/bash

# Exit on error
set -e

# Configuration
KERNEL_VERSION="5.10.0-rock5b"
KERNEL_LOCALVERSION="-enhanced"
ARCH=arm64
CROSS_COMPILE=aarch64-linux-gnu-
JOBS=$(nproc)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

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

# Install required packages
echo "Installing build dependencies..."
apt-get update
apt-get install -y \
    build-essential \
    flex \
    bison \
    libssl-dev \
    libelf-dev \
    bc \
    kmod \
    cpio \
    dwarves \
    dpkg-dev \
    debhelper \
    fakeroot

# Prepare kernel config
echo "Preparing kernel configuration..."
cd linux
make ARCH=$ARCH CROSS_COMPILE=$CROSS_COMPILE defconfig
./scripts/config --file .config \
    --enable ROCK5B_LOGGER \
    --enable ROCK5B_POWER_MONITOR \
    --enable ROCK5B_CRASH_REPORTER \
    --disable DRM_PANFROST \
    --enable MALI_MIDGARD \
    --enable MALI_VALHALL \
    --set-str LOCALVERSION "$KERNEL_LOCALVERSION"

# Build kernel and modules
echo "Building kernel..."
make ARCH=$ARCH CROSS_COMPILE=$CROSS_COMPILE -j$JOBS

echo "Building modules..."
make ARCH=$ARCH CROSS_COMPILE=$CROSS_COMPILE modules -j$JOBS

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/DEBIAN" \
         "$TEMP_DIR/boot" \
         "$TEMP_DIR/lib/modules/$KERNEL_VERSION$KERNEL_LOCALVERSION"

# Install modules
echo "Installing modules..."
make ARCH=$ARCH CROSS_COMPILE=$CROSS_COMPILE \
    INSTALL_MOD_PATH="$TEMP_DIR" modules_install

# Copy kernel and DTBs
echo "Copying kernel and device trees..."
cp arch/$ARCH/boot/Image "$TEMP_DIR/boot/vmlinuz-$KERNEL_VERSION$KERNEL_LOCALVERSION"
cp arch/$ARCH/boot/dts/rockchip/rk3588*.dtb "$TEMP_DIR/boot/"
cp arch/$ARCH/boot/dts/rockchip/overlay/*.dtbo "$TEMP_DIR/boot/"

# Generate initrd
echo "Generating initrd..."
update-initramfs -c -k "$KERNEL_VERSION$KERNEL_LOCALVERSION" \
    -b "$TEMP_DIR/boot"

# Create DEBIAN/control
cat > "$TEMP_DIR/DEBIAN/control" << EOF
Package: linux-image-$KERNEL_VERSION$KERNEL_LOCALVERSION
Version: 1.0.0
Architecture: arm64
Maintainer: Your Name <your.email@example.com>
Description: Enhanced Linux kernel for Rock 5B Plus
 This package contains the enhanced Linux kernel with:
 - Mali GPU driver support
 - Enhanced logging system
 - Power monitoring
 - Crash reporting
EOF

# Create postinst script
cat > "$TEMP_DIR/DEBIAN/postinst" << EOF
#!/bin/sh
set -e

# Update bootloader configuration
if [ -x /usr/sbin/update-grub ]; then
    update-grub
fi

# Enable services
systemctl enable kernel-logger
systemctl enable power-monitor
systemctl enable crash-reporter

# Apply device tree overlay
dtoverlay rock-5b-plus-enhanced
EOF
chmod 755 "$TEMP_DIR/DEBIAN/postinst"

# Create prerm script
cat > "$TEMP_DIR/DEBIAN/prerm" << EOF
#!/bin/sh
set -e

# Disable services
systemctl disable kernel-logger
systemctl disable power-monitor
systemctl disable crash-reporter
EOF
chmod 755 "$TEMP_DIR/DEBIAN/prerm"

# Build package
echo "Building kernel package..."
dpkg-deb --build "$TEMP_DIR" \
    "linux-image-$KERNEL_VERSION$KERNEL_LOCALVERSION.deb"

# Cleanup
rm -rf "$TEMP_DIR"

echo_success "Kernel package built successfully:"
echo "linux-image-$KERNEL_VERSION$KERNEL_LOCALVERSION.deb"