#!/bin/bash

# YSuite - Rock 5B+ Monitoring Suite
# Direct Board Installation Guide

echo "YSuite - Rock 5B+ Monitoring Suite"
echo "=================================="
echo ""
echo "This script provides instructions for installing YSuite directly on your Rock 5B+ board."
echo ""
echo "INSTRUCTIONS:"
echo "1. Copy these files to your Rock 5B+ board (via USB, SD card, or direct transfer)"
echo "2. On the board, run: sudo ./install_ysuite.sh"
echo "3. After installation, use commands: ytop, ylog, ycrash, ypower, yhelp"
echo ""
echo "Files to copy to board:"
echo "- ysuite.py"
echo "- install_ysuite.sh"
echo "- YSUITE_SUMMARY.md"
echo ""
echo "Alternative installation methods:"
echo "- Copy files to /tmp/ on board and run: sudo bash /tmp/install_ysuite.sh"
echo "- Or copy to home directory and run: sudo bash ~/install_ysuite.sh"
echo ""
echo "YSuite is designed to run directly on the board for real-time monitoring."
