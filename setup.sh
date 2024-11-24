#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Error handling
set -e
trap 'echo -e "${RED}Error occurred. Exiting...${NC}" >&2' ERR

echo -e "${BLUE}Setting up Optimus Cline...${NC}"

# Create core directory structure
echo -e "${GREEN}Creating directory structure...${NC}"
mkdir -p ~/.cline/{bin,templates}
chmod 755 ~/.cline

# Copy scripts
echo -e "${GREEN}Installing scripts...${NC}"
cp bin/* ~/.cline/bin/
chmod +x ~/.cline/bin/*

# Copy templates
echo -e "${GREEN}Installing templates...${NC}"
cp -r templates/* ~/.cline/templates/

# Create cline-tasks directory if it doesn't exist
if [ ! -d ~/Desktop/cline-tasks ]; then
    echo -e "${GREEN}Creating cline-tasks directory...${NC}"
    mkdir -p ~/Desktop/cline-tasks
fi

# Add scripts to PATH
if ! grep -q "export PATH=\$PATH:~/.cline/bin" ~/.zshrc; then
    echo -e "\n# Optimus Cline utility scripts" >> ~/.zshrc
    echo "export PATH=\$PATH:~/.cline/bin" >> ~/.zshrc
    echo -e "${GREEN}Added scripts to PATH in ~/.zshrc${NC}"
fi

# Create example project structure
cat > ~/.cline/templates/project.template << 'EOF'
.cline/
├── tasks/              # Task management
│   ├── active/        # Current tasks
│   ├── archive/       # Completed tasks
│   └── templates/     # Task templates
├── configs/           # Project configurations
└── docs/             # Project documentation
EOF

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "1. Run: source ~/.zshrc"
echo "2. Go to your project: cd /path/to/your/project"
echo "3. Initialize: init-project.sh \"project-name\""
echo "4. Create first task: new-task.sh \"Initial Setup\""
