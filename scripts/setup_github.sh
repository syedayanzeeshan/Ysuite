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

# Instructions
echo_info "GitHub Repository Setup Instructions"
echo "
1. First, create a Personal Access Token (PAT) on GitHub:
   - Go to https://github.com/settings/tokens
   - Click 'Generate new token (classic)'
   - Give it a name like 'Rock5B-Kernel'
   - Select scopes: 'repo' and 'workflow'
   - Copy the generated token

2. Configure git credentials:
   git config --global credential.helper store
   git config --global user.name \"Syed Ayan Zeeshan\"
   git config --global user.email \"syedayanzeeshan@gmail.com\"

3. Set up the repository:
   git remote set-url origin https://[YOUR_USERNAME]:[YOUR_PAT]@github.com/syedayanzeeshan/RadxaAt.git

4. Then run:
   git add .
   git commit -m \"Add enhanced kernel features\"
   git push -u origin main

The repository URL format should look like:
https://syedayanzeeshan:[YOUR_PAT]@github.com/syedayanzeeshan/RadxaAt.git

Replace [YOUR_PAT] with the token you generated.

Files to be pushed:
- Kernel modifications in linux/drivers/misc/
- Build scripts in scripts/
- Configuration files in configs/
- Documentation (README.md, INSTRUCTIONS.md, etc.)

Note: Make sure to keep your PAT secure and never commit it to the repository."

# Verify current git status
echo -e "\nCurrent git status:"
git status

echo -e "\nCurrent remote URL (should not show token if set):"
git remote -v