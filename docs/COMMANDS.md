# Command Execution Guide

## Overview

The Cline GUI integrates with VS Code and the command line in several ways:

1. Task Management
   - Select a task in the GUI
   - Click "Set Current" to make it the active task
   - This creates:
     - `.cline/current_task.md` - Symlink to task file
     - `.cline/current_task.txt` - Contains task ID
   - Cline CLI reads current_task.txt to find active task

2. Command Execution Flow
   ```
   [Task Creation]
   1. Create task with credentials in GUI
   2. Set as current task
   3. Configure keys.txt in project settings
   
   [Command Execution]
   1. Cline reads current_task.txt
   2. Loads task.md to get required credentials
   3. Reads values from keys.txt
   4. Injects credentials into command
   5. Executes command
   ```

3. VS Code Integration
   - VS Code commands (git.acceptChange, etc.) are executed through VS Code CLI
   - Automated approval using pyautogui for red buttons:
     ```
     [Approval Flow]
     1. Command executed in VS Code
     2. VS Code shows red approval button
     3. PyAutoGUI scans screen for red pixels
     4. Verifies security checks
     5. Clicks button if checks pass
     ```

## PyAutoGUI Setup

1. Install dependencies:
   ```bash
   # macOS
   brew install python-tk python-imaging
   pip install pyautogui pillow
   
   # Linux
   sudo apt-get install python3-tk python3-dev scrot
   pip install pyautogui
   
   # Windows
   pip install pyautogui
   ```

2. Test Setup:
   ```bash
   # Run test script
   python3 test_pyautogui.py
   
   # Test features:
   - Screenshot capability
   - Mouse movement
   - Click detection
   ```

3. Troubleshooting:
   - macOS: Enable Screen Recording permission in System Preferences
   - Linux: Install python3-xlib
   - Windows: No additional setup needed

## Usage Example

1. Create Task:
   ```
   # In GUI:
   1. Click "New Task"
   2. Enter description
   3. Add credentials:
      Service: AWS
      Keys: AWS_PROFILE, AWS_REGION
   4. Click "Create"
   5. Select task and click "Set Current"
   ```

2. Configure keys.txt:
   ```
   # In project settings:
   1. Configure keys.txt path
   
   # In keys.txt:
   [AWS]
   AWS_PROFILE=development
   AWS_REGION=us-west-2
   ```

3. Use with Cline:
   ```bash
   # Cline automatically:
   1. Reads current_task.txt
   2. Gets credentials from task.md
   3. Injects values from keys.txt
   
   # Example command:
   aws s3 ls --profile ${AWS_PROFILE} --region ${AWS_REGION}
   # Becomes:
   aws s3 ls --profile development --region us-west-2
   ```

## Security Notes

1. Security Checks:
   - Added in Security tab
   - Must pass before:
     - Executing dangerous commands
     - Automated VS Code approvals
     - Credential injection
   - Status included in task system prompts

2. Custom Security Checks:
   - Click "Add Check" in Security tab
   - Enter check description
   - Check appears in:
     - Security tab
     - Task system prompts
     - Command verification

3. Keys File:
   - Store in secure location outside project
   - Configure path in project settings
   - Values masked in GUI
   - Never committed to version control

4. VS Code Automation:
   - Only clicks red approval buttons
   - Requires security checks to pass
   - Can be disabled by unchecking security items
   - Logs all automated actions
