# Cline GUI Quick Start

## Installation

1. Clone and setup:
   ```bash
   git clone https://github.com/lancejames221b/optimus-cline.git
   cd optimus-cline
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Test PyAutoGUI:
   ```bash
   python3 test_pyautogui.py
   ```

## Basic Usage

1. Start the GUI:
   ```bash
   python3 run_gui.py
   ```

2. Configure Project:
   - Click "Select Project" or "New Project"
   - Configure keys.txt in project settings
   - Add any custom security checks

3. Create Task:
   - Click "New Task"
   - Enter description and system prompt
   - Add required credentials
   - Click "Create"

4. Set Current Task:
   - Select task in list
   - Click "Set Current"
   - Task is now active for Cline

5. Execute Commands:
   - Commands tab shows command history
   - VS Code tab for git operations
   - Credentials injected automatically
   - Security checks verified before execution

## Key Features

1. Task Management:
   - Create/edit tasks
   - Set active task
   - Preview task details
   - Archive completed tasks

2. Credential Management:
   - Secure credential storage
   - Automatic injection
   - Service-based organization

3. Security:
   - Custom security checks
   - Automated VS Code approvals
   - Command verification

4. VS Code Integration:
   - Git operations
   - Command automation
   - Security verification

## Common Workflows

1. New Task:
   ```
   New Task → Add Credentials → Set Current → Execute Commands
   ```

2. VS Code Automation:
   ```
   Security Checks → VS Code Command → Automated Approval
   ```

3. Credential Injection:
   ```
   Configure keys.txt → Add to Task → Use in Commands
   ```

## Tips

1. Security:
   - Keep keys.txt outside project
   - Enable required security checks
   - Review automated actions

2. Organization:
   - One task per feature/bug
   - Clear task descriptions
   - Regular task archival

3. Automation:
   - Test PyAutoGUI setup
   - Verify security checks
   - Monitor command history

## Next Steps

1. Read full documentation:
   - [Commands Guide](COMMANDS.md)
   - [Product Requirements](PRD.md)

2. Join development:
   - Check GitHub issues
   - Submit pull requests
   - Report bugs

3. Get help:
   - File GitHub issues
   - Check documentation
   - Contact maintainers
