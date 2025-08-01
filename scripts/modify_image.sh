#!/bin/bash

# Exit on error
set -e

# Configuration
IMAGE_URL="https://github.com/Joshua-Riek/ubuntu-rockchip/releases/download/v2.4.0/ubuntu-22.04-preinstalled-desktop-arm64-rock-5b-plus.img.xz"
IMAGE_NAME="ubuntu-22.04-preinstalled-desktop-arm64-rock-5b-plus.img.xz"
EXTRACTED_IMAGE="ubuntu-22.04-preinstalled-desktop-arm64-rock-5b-plus.img"
MOUNT_POINT="/mnt/rock5b_image"
KERNEL_VERSION="5.10.0-rock5b-enhanced"

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

cleanup() {
    echo "Cleaning up..."
    if mountpoint -q "$MOUNT_POINT"; then
        umount "$MOUNT_POINT"
    fi
    if [ -d "$MOUNT_POINT" ]; then
        rm -rf "$MOUNT_POINT"
    fi
    losetup -D
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo_error "Please run as root"
fi

# Ensure we're in the right directory
cd "$(dirname "$0")/.."
WORK_DIR=$(pwd)

# Set up cleanup trap
trap cleanup EXIT

# Create working directory
mkdir -p "$WORK_DIR/build"
cd "$WORK_DIR/build"

# Download image if not exists
if [ ! -f "$IMAGE_NAME" ]; then
    echo "Downloading Ubuntu image..."
    wget "$IMAGE_URL" -O "$IMAGE_NAME"
    echo_success "Image downloaded successfully"
fi

# Extract image if not already extracted
if [ ! -f "$EXTRACTED_IMAGE" ]; then
    echo "Extracting image..."
    xz -d -k "$IMAGE_NAME"
    echo_success "Image extracted successfully"
fi

# Get partition information
PARTITION_INFO=$(fdisk -l "$EXTRACTED_IMAGE")
SECTOR_SIZE=$(echo "$PARTITION_INFO" | grep "Sector size" | awk '{print $4}')
ROOT_PART_START=$(echo "$PARTITION_INFO" | grep "Linux filesystem" | awk '{print $2}')

# Calculate offset
OFFSET=$((ROOT_PART_START * SECTOR_SIZE))

# Setup mount point
mkdir -p "$MOUNT_POINT"

# Mount image
echo "Mounting image..."
mount -o loop,offset=$OFFSET "$EXTRACTED_IMAGE" "$MOUNT_POINT"
echo_success "Image mounted at $MOUNT_POINT"

# Prepare for chroot
echo "Preparing chroot environment..."
mount -t proc /proc "$MOUNT_POINT/proc"
mount -t sysfs /sys "$MOUNT_POINT/sys"
mount -o bind /dev "$MOUNT_POINT/dev"
mount -o bind /dev/pts "$MOUNT_POINT/dev/pts"

# Copy kernel package to image
echo "Copying kernel package..."
cp "linux-image-$KERNEL_VERSION.deb" "$MOUNT_POINT/tmp/"

# Install kernel package in chroot
echo "Installing kernel package..."
chroot "$MOUNT_POINT" /bin/bash -c "
    # Update package lists
    apt-get update

    # Install kernel package
    dpkg -i /tmp/linux-image-$KERNEL_VERSION.deb

    # Clean up
    rm /tmp/linux-image-$KERNEL_VERSION.deb
    apt-get clean
"

# Update extlinux.conf
echo "Updating boot configuration..."
cat > "$MOUNT_POINT/boot/extlinux/extlinux.conf" << EOF
timeout 10
default rock-5b-enhanced

label rock-5b-enhanced
    kernel /boot/vmlinuz-$KERNEL_VERSION
    initrd /boot/initrd.img-$KERNEL_VERSION
    fdt /boot/rk3588-rock-5b.dtb
    append root=LABEL=rootfs rootwait rw console=ttyS2,1500000n8 console=tty1 cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory swapaccount=1
EOF

# Unmount everything
echo "Unmounting..."
umount "$MOUNT_POINT/dev/pts"
umount "$MOUNT_POINT/dev"
umount "$MOUNT_POINT/sys"
umount "$MOUNT_POINT/proc"
umount "$MOUNT_POINT"

# Compress modified image
echo "Compressing modified image..."
xz -z "$EXTRACTED_IMAGE"
mv "$EXTRACTED_IMAGE.xz" "ubuntu-22.04-enhanced-rock-5b-plus.img.xz"

echo_success "Image modification completed successfully"
echo "Modified image: ubuntu-22.04-enhanced-rock-5b-plus.img.xz"