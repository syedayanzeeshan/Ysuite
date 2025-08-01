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

# Initialize git repository
echo "Initializing git repository..."
git init

# Configure git
git config user.name "Syed Ayan Zeeshan"
git config user.email "syedayanzeeshan@gmail.com"

# Add files
echo "Adding files..."
git add .

# Initial commit
echo "Creating initial commit..."
git commit -m "Initial commit: Rock 5B Plus Enhanced Kernel

- Added kernel logging system
- Implemented power monitoring
- Added crash reporting
- Configured Mali GPU driver
- Added build and verification scripts"

# Add remote
echo "Adding remote repository..."
git remote add origin https://github.com/syedayanzeeshan/RadxaAt.git

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo_success "Successfully pushed to GitHub"
echo "Repository URL: https://github.com/syedayanzeeshan/RadxaAt"