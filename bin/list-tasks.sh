#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

TASKS_DIR="/Volumes/SeXternal/221B/Code/optimus-cline/tasks"
RECENT_COUNT=5

# List active tasks
echo -e "${GREEN}Active Tasks:${NC}"
ls -1t "$TASKS_DIR/active/task_"*.md 2>/dev/null | while read task; do
    title=$(head -n 1 "$task" | sed 's/# Task: //')
    echo "- $(basename "$task"): $title"
done || echo "No active tasks found"

# List recent archived tasks
echo -e "\n${GREEN}Recent Archived Tasks:${NC}"
ls -1t "$TASKS_DIR/archive/task_"*.md 2>/dev/null | head -n $RECENT_COUNT | while read task; do
    title=$(head -n 1 "$task" | sed 's/# Task: //')
    echo "- $(basename "$task"): $title"
done || echo "No archived tasks found"

# Show Desktop cline-tasks if they exist
if [ -d ~/Desktop/cline-tasks ]; then
    echo -e "\n${BLUE}Tasks in ~/Desktop/cline-tasks:${NC}"
    ls -1t ~/Desktop/cline-tasks/task_*.md 2>/dev/null | while read task; do
        if [ -f "$task" ]; then
            title=$(head -n 1 "$task" | sed 's/# Task: //')
            echo "- $(basename "$task"): $title"
        fi
    done || echo "No tasks found in cline-tasks"
fi

echo -e "\n${BLUE}Quick Tips:${NC}"
echo "1. Create new task: new-task.sh \"Task Name\""
echo "2. Archive task: archive-task.sh <task-file>"
echo "3. View all archived: ls -la $TASKS_DIR/archive/"
