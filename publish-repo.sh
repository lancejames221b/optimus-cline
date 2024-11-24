#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Error handling
set -e
trap 'echo -e "${RED}Error occurred. Exiting...${NC}" >&2' ERR

REPO_NAME="cline"
BRANCH="optimus-cline"
GITHUB_USER="lancejames221b"

echo -e "${BLUE}Publishing Optimus Cline to GitHub...${NC}"

# Create temporary directory for the repository
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Initialize git repository
echo -e "${GREEN}Initializing Git repository...${NC}"
git init

# Create optimus-cline branch
git checkout -b "$BRANCH"

# Copy all files from /tmp/optimus-cline
echo -e "${GREEN}Copying repository files...${NC}"
cp -r /tmp/optimus-cline/* .

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

# Project specific
~/.ewitness/access/keys/
~/.ewitness/access/ssh/keys/
EOF

# Initial commit
git add .
git commit -m "Initial commit: Optimus Cline environment setup

- Task management system
- Environment organization
- Documentation structure
- Security best practices"

# Add remote and push
echo -e "${GREEN}Adding GitHub remote...${NC}"
git remote add origin "git@github.com:${GITHUB_USER}/${REPO_NAME}.git"

echo -e "${BLUE}Repository prepared successfully!${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo "1. Create repository on GitHub: https://github.com/new"
echo "   - Name: $REPO_NAME"
echo "   - Description: Intelligent task management and environment organization system"
echo "2. Push to GitHub:"
echo "   cd $TEMP_DIR"
echo "   git push -u origin $BRANCH"
echo "3. Create pull request on GitHub"
echo ""
echo "Repository location: $TEMP_DIR"

# Create installation instructions
cat > INSTALL.md << 'EOF'
# Installation Instructions

1. Clone the repository:
   ```bash
   git clone git@github.com:lancejames221b/cline.git
   cd cline
   git checkout optimus-cline
   ```

2. Run setup script:
   ```bash
   ./setup.sh
   ```

3. Initialize your first project:
   ```bash
   init-project.sh "project-name"
   ```

4. Create your first task:
   ```bash
   new-task.sh "Initial Setup Task"
   ```

## Directory Structure After Installation

```
~/.ewitness/                  # Core configuration
├── access/                   # Access configurations
│   ├── ssh/                 # SSH configurations
│   ├── keys/               # API keys and tokens
│   └── digitalocean/       # Cloud provider configs
├── history/                 # Historical context
│   ├── cline-tasks/        # Task history
│   ├── fixes/              # System fixes
│   └── runbooks/           # Operational guides
├── templates/               # Task templates
└── bin/                    # Utility scripts

/Volumes/SeXternal/221B/Code/  # Project space
└── your-project/
    ├── tasks/              # Task management
    │   ├── active/        # Current tasks
    │   ├── archive/       # Completed tasks
    │   └── templates/     # Task templates
    └── docs/              # Documentation
        ├── confluence/    # Confluence sync
        └── templates/     # Doc templates
```

## Configuration

1. SSH Configuration:
   ```bash
   cp templates/configs/ssh_config.template ~/.ewitness/access/ssh/config
   chmod 600 ~/.ewitness/access/ssh/config
   ```

2. Keys Configuration:
   ```bash
   cp templates/configs/keys.template ~/.ewitness/access/keys/current/keys.txt
   chmod 600 ~/.ewitness/access/keys/current/keys.txt
   ```

3. Update your shell configuration:
   ```bash
   source ~/.zshrc
   ```

## Usage

1. Create new tasks:
   ```bash
   new-task.sh "Task Name"
   ```

2. View task history:
   ```bash
   ls -la ~/Desktop/cline-tasks/
   ```

3. Manage credentials:
   ```bash
   manage-keys.sh
   ```

## Security Notes

- All sensitive files are stored in ~/.ewitness with 700 permissions
- Keys and credentials have 600 permissions
- SSH configs are secured by default
- Credentials are stored securely and can be rotated regularly
EOF

echo -e "${BLUE}Installation instructions created: $TEMP_DIR/INSTALL.md${NC}"
