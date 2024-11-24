#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check for task file argument
if [ -z "$1" ]; then
    echo -e "${RED}Usage: archive-task.sh <task-file>${NC}"
    echo -e "Example: archive-task.sh tasks/active/task_2024-11-24_my_task.md"
    
    echo -e "\n${BLUE}Available tasks:${NC}"
    ls -1 /Volumes/SeXternal/221B/Code/optimus-cline/tasks/active/task_*.md 2>/dev/null || echo "No active tasks found"
    exit 1
fi

TASK_FILE="$1"
DATE=$(date +%Y-%m-%d)
TASK_NAME=$(basename "$TASK_FILE")
ARCHIVE_DIR="/Volumes/SeXternal/221B/Code/optimus-cline/tasks/archive"

# Move task file to archive
if [ -f "$TASK_FILE" ]; then
    mv "$TASK_FILE" "$ARCHIVE_DIR/${DATE}_${TASK_NAME}"
    echo -e "${GREEN}Archived task to: $ARCHIVE_DIR/${DATE}_${TASK_NAME}${NC}"
    
    # Update symlink in cline-tasks if it exists
    if [ -d ~/Desktop/cline-tasks ]; then
        ln -sf "$ARCHIVE_DIR/${DATE}_${TASK_NAME}" ~/Desktop/cline-tasks/
        echo -e "${GREEN}Updated symlink in ~/Desktop/cline-tasks/${NC}"
    fi
else
    echo -e "${RED}Error: Task file not found${NC}"
    exit 1
fi

echo -e "\n${BLUE}Quick Tips:${NC}"
echo "1. Review archived tasks: ls -la $ARCHIVE_DIR"
echo "2. Create new task: new-task.sh \"Task Name\""
echo "3. Active tasks: ls -la /Volumes/SeXternal/221B/Code/optimus-cline/tasks/active/"
