#!/bin/bash
# YSuite v2.1.0 Installation Script
# Comprehensive System Monitoring and Management Suite
set -e
echo "YSuite v2.1.0 - System Monitoring Suite Installation"
echo "===================================================="
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi
echo "Updating package list..."
apt update
echo "Installing system dependencies..."
apt install -y python3-pip python3-psutil python3-requests python3-rich python3-colorama
echo "Installing Python dependencies via apt..."
# Note: Using apt instead of pip3 to avoid externally-managed-environment error
# python3-rich and python3-colorama should be available in Debian repositories
echo "Installing YSuite to /usr/local/bin..."
cp ysuite.py /usr/local/bin/ysuite
chmod +x /usr/local/bin/ysuite
echo "Creating command symlinks..."
ln -sf /usr/local/bin/ysuite /usr/local/bin/ytop
ln -sf /usr/local/bin/ysuite /usr/local/bin/ylog
ln -sf /usr/local/bin/ysuite /usr/local/bin/ycrash
ln -sf /usr/local/bin/ysuite /usr/local/bin/ypower
ln -sf /usr/local/bin/ysuite /usr/local/bin/yhelp
echo "Creating data directories..."
mkdir -p /var/log/ysuite
mkdir -p /var/lib/ysuite/data
mkdir -p /etc/ysuite
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
