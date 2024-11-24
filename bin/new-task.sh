#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Get task name from argument
if [ -z "$1" ]; then
    echo -e "${RED}Usage: new-task.sh \"Task Name\"${NC}"
    exit 1
fi

# Set up variables
DATE=$(date +%Y-%m-%d_%H-%M-%S)
TASK_NAME="$1"
TASK_FILE="/Volumes/SeXternal/221B/Code/optimus-cline/tasks/active/task_${DATE}_${TASK_NAME// /_}.md"

# Create task file from template
cat > "$TASK_FILE" << EOL
# Task: $TASK_NAME
Date: $(date +%Y-%m-%d\ %H:%M:%S)

## Context
- Previous Tasks: [Link to relevant cline tasks]
- Related Docs: [Confluence/Git doc links]
- Tickets: [JIRA links]

## Access Requirements
- SSH: [Config details]
- DO Resources: [Droplet info]
- API Keys: [Key references]

## Steps
1. ...

## Verification
1. ...

## Rollback
1. ...
EOL

# Create symlink in cline-tasks
if [ -d ~/Desktop/cline-tasks ]; then
    ln -sf "$TASK_FILE" ~/Desktop/cline-tasks/
    echo -e "${GREEN}Created symlink in ~/Desktop/cline-tasks/${NC}"
fi

echo -e "${GREEN}Created new task: $TASK_FILE${NC}"
echo -e "${BLUE}Edit the task file to add details${NC}"
