#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Error handling
set -e
trap 'echo -e "${RED}Error occurred. Exiting...${NC}" >&2' ERR

# Check if project name was provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: init-project.sh <project-name>${NC}"
    exit 1
fi

PROJECT_NAME=$1
CURRENT_DIR=$(pwd)

echo -e "${BLUE}Initializing project: $PROJECT_NAME${NC}"

# Create project structure
echo -e "${GREEN}Creating project structure...${NC}"
mkdir -p .cline/{tasks/{active,archive,templates},configs,docs}

# Create project-specific task template
echo -e "${GREEN}Creating task template...${NC}"
cat > .cline/tasks/templates/task.md << 'EOF'
# Task: {TITLE}
Date: $(date +%Y-%m-%d_%H-%M-%S)

## Context
- Previous Tasks: [Link to relevant tasks]
- Related Docs: [Documentation links]
- Tickets: [Issue/ticket links]

## Environment
- Development: [development environment details]
- Staging: [staging environment details]
- Production: [production environment details]

## Pre-Execution Checklist
- [ ] Verified environment
- [ ] Checked service health
- [ ] Backed up relevant data
- [ ] Reviewed previous tasks

## Steps
1. [Step details]
   ```bash
   # Command to execute
   ```

## Verification
1. [Verification steps]
   ```bash
   # Verification commands
   ```

## Rollback
1. [Rollback steps if needed]
   ```bash
   # Rollback commands
   ```

## Results
- [ ] Task completed successfully
- [ ] Documentation updated
- [ ] Changes verified
- [ ] Rollback tested if applicable

## Notes
- Historical context: [Reference to previous tasks]
- Known issues: [Document any issues]
- Future improvements: [Suggestions]
EOF

# Create project README
echo -e "${GREEN}Creating project documentation...${NC}"
cat > .cline/README.md << EOF
# $PROJECT_NAME - Cline Tasks

## Project Structure
\`\`\`
.cline/
├── tasks/              # Task management
│   ├── active/        # Current tasks
│   ├── archive/       # Completed tasks
│   └── templates/     # Task templates
├── configs/           # Project configurations
└── docs/             # Project documentation
\`\`\`

## Task Management
1. Create new task:
   \`\`\`bash
   new-task.sh "Task Name"
   \`\`\`

2. View active tasks:
   \`\`\`bash
   ls -la .cline/tasks/active/
   \`\`\`

3. View task history:
   \`\`\`bash
   ls -la ~/Desktop/cline-tasks/$PROJECT_NAME/
   \`\`\`

## Documentation
- Project docs in .cline/docs/
- Configuration in .cline/configs/
- Task templates in .cline/tasks/templates/

## Best Practices
1. Always create tasks for changes
2. Document steps and results
3. Include rollback procedures
4. Archive completed tasks
EOF

# Create symlink in cline-tasks
if [ -d ~/Desktop/cline-tasks ]; then
    mkdir -p ~/Desktop/cline-tasks/"$PROJECT_NAME"
    ln -sf "$CURRENT_DIR/.cline/tasks/active" ~/Desktop/cline-tasks/"$PROJECT_NAME"/active
    ln -sf "$CURRENT_DIR/.cline/tasks/archive" ~/Desktop/cline-tasks/"$PROJECT_NAME"/archive
    echo -e "${GREEN}Created project links in cline-tasks${NC}"
fi

# Add .cline to .gitignore if it exists
if [ -f .gitignore ]; then
    if ! grep -q "^.cline/" .gitignore; then
        echo -e "\n# Cline task management\n.cline/" >> .gitignore
        echo -e "${GREEN}Added .cline to .gitignore${NC}"
    fi
else
    echo -e "# Cline task management\n.cline/" > .gitignore
    echo -e "${GREEN}Created .gitignore with .cline${NC}"
fi

echo -e "${GREEN}Project initialized successfully!${NC}"
echo -e "${BLUE}Project location: $CURRENT_DIR/.cline${NC}"
echo -e "${BLUE}Task history: ~/Desktop/cline-tasks/$PROJECT_NAME${NC}"
echo -e "\nNext steps:"
echo "1. Create your first task: new-task.sh \"Initial Setup\""
echo "2. Document project configuration in .cline/configs/"
echo "3. Add project documentation in .cline/docs/"
