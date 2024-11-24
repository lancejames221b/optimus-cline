#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Error handling
set -e
trap 'echo -e "${RED}Error occurred. Exiting...${NC}" >&2' ERR

echo -e "${BLUE}Initializing Optimus Cline repository...${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed. Please install git first.${NC}"
    exit 1
fi

# Initialize git repo
git init

# Create optimus-cline branch
git checkout -b optimus-cline

# Create .gitignore
cat > .gitignore << 'EOF'
# Environment specific
.DS_Store
.env
*.log

# Sensitive information
**/keys.txt
**/config
**/*.key
**/*.pem
EOF

# Copy all files
cp -r /tmp/optimus-cline/* .

# Initial commit
git add .
git commit -m "Initial commit: Optimus Cline environment setup"

echo -e "${GREEN}Repository initialized successfully!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "1. Add remote: git remote add origin git@github.com:lancejames221b/cline.git"
echo "2. Push changes: git push -u origin optimus-cline"
echo "3. Create pull request on GitHub"
