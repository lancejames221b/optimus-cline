# Command Execution Guide

## Overview

The Cline GUI integrates with VS Code and the command line in several ways:

1. Task Management
   - Select a task in the GUI
   - Click "Set Current" to make it the active task
   - This creates:
     - `.cline/current_task.md` - Symlink to task file
     - `.cline/current_task.txt` - Contains task ID

2. Command Execution
   - Enter commands in the Commands tab
   - Commands can use credential placeholders:
     ```bash
     # If task requires AWS credentials:
     aws s3 ls --profile ${AWS_PROFILE}
     ```
   - Credentials are injected from keys.txt based on task requirements

3. VS Code Integration
   - VS Code commands (git.acceptChange, etc.) are executed through VS Code CLI
   - Automated approval using pyautogui for red buttons
   - Security checks must pass before automation

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

2. Test PyAutoGUI:
   ```python
   import pyautogui
   
   # Safety features
   pyautogui.FAILSAFE = True  # Move mouse to corner to abort
   pyautogui.PAUSE = 1.0      # 1 second pause between actions
   
   # Get screen size
   width, height = pyautogui.size()
   print(f"Screen size: {width}x{height}")
   
   # Test screenshot
   screenshot = pyautogui.screenshot()
   screenshot.save("test.png")
   ```

3. Troubleshooting:
   - macOS: Enable Screen Recording permission
   - Linux: Install python3-xlib
   - Windows: No additional setup needed

## Usage Example

1. Create a new task with credentials:
   ```
   Service: AWS
   Keys: AWS_PROFILE, AWS_REGION
   ```

2. Configure keys.txt:
   ```
   [AWS]
   AWS_PROFILE=development
   AWS_REGION=us-west-2
   ```

3. Enter command in GUI:
   ```bash
   aws s3 ls --profile ${AWS_PROFILE} --region ${AWS_REGION}
   ```

4. Command is executed with injected credentials:
   ```bash
   aws s3 ls --profile development --region us-west-2
   ```

## Security Notes

1. Security checks must pass before:
   - Executing dangerous commands
   - Automated VS Code approvals
   - Credential injection

2. Custom security checks can be added:
   - Click "Add Check" in Security tab
   - Enter check description
   - Check appears in task system prompts

3. Keys file:
   - Store in secure location
   - Configure path in project settings
   - Values are never displayed in GUI
