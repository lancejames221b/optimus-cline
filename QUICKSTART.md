# Quick Start Guide

## What is Optimus Cline?
A simple way to organize your work on any project:
- Track tasks and changes
- Document solutions
- Store configurations securely
- Maintain command history

## 5-Minute Setup

1. Clone and install:
```bash
# Just copy/paste these commands
git clone git@github.com:lancejames221b/cline.git
cd cline
git checkout optimus-cline
./setup.sh
source ~/.zshrc
```

2. Start using with any project:
```bash
# Go to your project directory
cd /path/to/your/project

# Initialize cline for this project
init-project.sh "project-name"
```

3. Create your first task:
```bash
# Example: "Set up development environment"
new-task.sh "My First Task"
```

That's it! You're ready to go! 🎉

## Daily Usage

1. Starting new work:
```bash
new-task.sh "What I'm going to do"
```
This creates a file with:
- Steps to follow
- Commands to run
- Place to note any issues

2. Finding past work:
```bash
# Look in your Desktop
open ~/Desktop/cline-tasks/your-project-name
```
All your work is organized by date and project

3. Storing project configs:
```bash
# Safely stored in your project's cline directory
.cline/configs/
```

## Need Help?

1. See what commands are available:
```bash
ls ~/.cline/bin/
```

2. Get help with a command:
```bash
command-name.sh --help
```

3. Check the docs:
```bash
cat README.md
```

## Tips for Beginners

1. Every time you start work:
   ```bash
   new-task.sh "What I'm doing"
   ```

2. In each task file:
   - Write down the commands you run
   - Note any errors you see
   - Write how you fixed things

3. Looking for past solutions:
   - Check ~/Desktop/cline-tasks/your-project/
   - Files are named by date and task
   - Everything is in plain text

4. Project organization:
   - Tasks in your-project/.cline/tasks/
   - Configs in your-project/.cline/configs/
   - History linked to ~/Desktop/cline-tasks/

## Common Questions

Q: Where are my files?
A: Everything is in two places:
   - your-project/.cline/ for project-specific stuff
   - ~/Desktop/cline-tasks/your-project/ for easy access

Q: How do I start a new task?
A: Just run: new-task.sh "Description of what you're doing"

Q: Where do I put project configs?
A: In your-project/.cline/configs/

Q: How do I find old work?
A: Look in ~/Desktop/cline-tasks/your-project/

## Remember

- Works with any project
- Every task gets documented
- History is easy to find
- Project-specific organization

That's all you need to know to get started! 🚀
