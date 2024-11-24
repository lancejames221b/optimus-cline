#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Error handling
set -e
trap 'echo -e "${RED}Error occurred. Exiting...${NC}" >&2' ERR

# Function to create directory if it doesn't exist
create_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo -e "${GREEN}Created directory: $1${NC}"
    else
        echo -e "${BLUE}Directory exists: $1${NC}"
    fi
}

# Function to create symlink if it doesn't exist
create_symlink() {
    if [ ! -L "$2" ]; then
        ln -sf "$1" "$2"
        echo -e "${GREEN}Created symlink: $2 -> $1${NC}"
    else
        echo -e "${BLUE}Symlink exists: $2${NC}"
    fi
}

echo -e "${BLUE}Setting up eWitness environment...${NC}"

# Create core directory structure
echo -e "${GREEN}Creating directory structure...${NC}"
create_dir ~/.ewitness
create_dir ~/.ewitness/bin
create_dir ~/.ewitness/access/ssh/config
create_dir ~/.ewitness/access/ssh/keys
create_dir ~/.ewitness/access/keys/current
create_dir ~/.ewitness/access/keys/archive
create_dir ~/.ewitness/access/digitalocean/tokens
create_dir ~/.ewitness/access/digitalocean/configs
create_dir ~/.ewitness/history/cline-tasks
create_dir ~/.ewitness/history/fixes
create_dir ~/.ewitness/history/runbooks
create_dir ~/.ewitness/templates

# Set secure permissions
chmod -R 700 ~/.ewitness
echo -e "${GREEN}Set secure permissions on ~/.ewitness${NC}"

# Create project directories
echo -e "${GREEN}Creating project directories...${NC}"
create_dir "/Volumes/SeXternal/221B/Code/eWitness/tasks/active"
create_dir "/Volumes/SeXternal/221B/Code/eWitness/tasks/archive"
create_dir "/Volumes/SeXternal/221B/Code/eWitness/tasks/templates"
create_dir "/Volumes/SeXternal/221B/Code/eWitness/docs/confluence/EWITNESS"
create_dir "/Volumes/SeXternal/221B/Code/eWitness/docs/confluence/sync"
create_dir "/Volumes/SeXternal/221B/Code/eWitness/docs/templates"

# Create symlinks
echo -e "${GREEN}Creating symlinks...${NC}"
if [ -d ~/Desktop/cline-tasks ]; then
    create_symlink ~/Desktop/cline-tasks ~/.ewitness/history/cline-tasks
else
    echo -e "${RED}Warning: ~/Desktop/cline-tasks not found${NC}"
fi

# Add scripts to PATH if not already added
if ! grep -q "export PATH=\$PATH:~/.ewitness/bin" ~/.zshrc; then
    echo -e "\n# eWitness utility scripts" >> ~/.zshrc
    echo "export PATH=\$PATH:~/.ewitness/bin" >> ~/.zshrc
    echo -e "${GREEN}Added scripts to PATH in ~/.zshrc${NC}"
else
    echo -e "${BLUE}Scripts already in PATH${NC}"
fi

# Create README
echo -e "${GREEN}Creating README...${NC}"
cat > ~/.ewitness/README.md << 'EOF'
# eWitness Environment

## Directory Structure
```
~/.ewitness/
├── access/               # Access configurations and credentials
│   ├── ssh/             # SSH configurations and keys
│   ├── keys/            # API keys and tokens
│   └── digitalocean/    # Digital Ocean specific configs
├── history/             # Historical context
│   ├── cline-tasks/     # Previous tasks (linked from Desktop)
│   ├── fixes/           # System fixes and patches
│   └── runbooks/        # Operational runbooks
├── templates/           # Task and documentation templates
└── bin/                # Utility scripts
```

## Project Structure
```
/Volumes/SeXternal/221B/Code/eWitness/
├── tasks/              # Task management
│   ├── active/        # Current tasks
│   ├── archive/       # Completed tasks
│   └── templates/     # Task templates
└── docs/              # Documentation
    ├── confluence/    # Confluence sync
    └── templates/     # Doc templates
```

## Available Scripts
- new-task.sh: Create new task from template
- archive-task.sh: Archive completed task
- manage-keys.sh: Manage access credentials
- setup-environment.sh: Initialize environment
- sync-docs.sh: Sync documentation

## Quick Start
1. Create new task:
   ```bash
   new-task.sh "Task Name"
   ```

2. Access credentials:
   ```bash
   cat ~/.ewitness/access/keys/current/keys.txt
   ```

3. View task history:
   ```bash
   ls -la ~/.ewitness/history/cline-tasks/
   ```

## Best Practices
1. Task Management
   - Use task templates for consistency
   - Document steps and results
   - Include rollback procedures
   - Archive completed tasks

2. Access Management
   - Store credentials in ~/.ewitness/access/keys
   - Regular key rotation with manage-keys.sh
   - Keep SSH configs updated
   - Use secure permissions

3. Documentation
   - Keep Git and Confluence in sync
   - Document all changes
   - Include context and rationale
   - Reference related tasks

4. Historical Context
   - Link to previous tasks
   - Document fixes and improvements
   - Maintain runbooks
   - Track system changes
EOF

echo -e "${GREEN}Environment setup complete!${NC}"
echo -e "${BLUE}See ~/.ewitness/README.md for usage instructions${NC}"
echo -e "${BLUE}Run 'source ~/.zshrc' to update PATH${NC}"
