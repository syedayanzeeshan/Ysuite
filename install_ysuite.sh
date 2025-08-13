#!/bin/bash

# YSuite Installation Script
# Comprehensive Rock 5B+ Monitoring and Management Suite

set -e

echo "YSuite - Rock 5B+ Monitoring Suite Installation"
echo "================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update package list
echo "Updating package list..."
apt update

# Install system dependencies
echo "Installing system dependencies..."
apt install -y python3-pip python3-psutil python3-requests

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install rich colorama

# Create installation directory
INSTALL_DIR="/usr/local/bin"
echo "Installing YSuite to $INSTALL_DIR..."

# Copy main script
cp ysuite.py "$INSTALL_DIR/ysuite"
chmod +x "$INSTALL_DIR/ysuite"

# Create symlinks for individual commands
echo "Creating command symlinks..."
ln -sf "$INSTALL_DIR/ysuite" "$INSTALL_DIR/ytop"
ln -sf "$INSTALL_DIR/ysuite" "$INSTALL_DIR/ylog"
ln -sf "$INSTALL_DIR/ysuite" "$INSTALL_DIR/ycrash"
ln -sf "$INSTALL_DIR/ysuite" "$INSTALL_DIR/ypower"
ln -sf "$INSTALL_DIR/ysuite" "$INSTALL_DIR/yhelp"

# Create data directories
echo "Creating data directories..."
mkdir -p /var/log/ysuite
mkdir -p /var/lib/ysuite/data
mkdir -p /etc/ysuite

# Set permissions
chmod 755 /var/log/ysuite
chmod 755 /var/lib/ysuite
chmod 755 /var/lib/ysuite/data
chmod 755 /etc/ysuite

echo ""
echo "✅ YSuite installation completed successfully!"
echo ""
echo "Available commands:"
echo "  ytop    - Real-time system performance monitor"
echo "  ylog    - System log monitoring and classification"
echo "  ycrash  - Crash detection and analysis"
echo "  ypower  - Power monitoring and PD negotiation"
echo "  yhelp   - Comprehensive help system"
echo ""
echo "Usage examples:"
echo "  ytop"
echo "  ylog -r"
echo "  ycrash -s"
echo "  ypower -v"
echo "  yhelp"
echo ""
echo "Log files are stored in: /var/log/ysuite/"
echo "Data files are stored in: /var/lib/ysuite/data/"
