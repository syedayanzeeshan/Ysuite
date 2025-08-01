#!/bin/bash

# Exit on error
set -e

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

# Configure git if not already configured
if [ -z "$(git config --get user.name)" ]; then
    git config user.name "Syed Ayan Zeeshan"
fi
if [ -z "$(git config --get user.email)" ]; then
    git config user.email "syedayanzeeshan@gmail.com"
fi

# Add files
echo "Adding files..."
git add .

# Create commit
echo "Creating commit..."
git commit -m "Add enhanced kernel features

- Added kernel logging system with rotation
- Implemented power monitoring (voltage/current)
- Added crash reporting with boot-time detection
- Configured Mali GPU driver with OpenCL/Vulkan support
- Added build and verification scripts
- Added comprehensive documentation"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

echo_success "Successfully pushed to GitHub"
echo "Repository URL: https://github.com/syedayanzeeshan/RadxaAt"