# Optimus Cline

Intelligent task management with visual command history and secure credential handling.

## Features

- Visual command history with branching
- Secure credential management
- Task organization
- Command cost tracking
- Timeline visualization

## Quick Start

```bash
# Install
git clone git@github.com:lancejames221b/optimus-cline.git
cd optimus-cline
./setup.sh

# Create your first task
new-task.sh "My First Task"
```

See QUICKSTART.md for more details.

## Components

- GUI: Visual interface for command history and credentials
- VSCode Extension: Command detection and execution
- CLI Tools: Task and credential management

## Project Structure

```
.
├── .gitignore
├── init-repo.sh
├── publish-repo.sh
├── QUICKSTART.md
├── README.md
├── setup.sh
├── bin/
│   ├── archive-task.sh
│   ├── init-project.sh
│   ├── init-templates.sh
│   ├── list-tasks.sh
│   ├── new-task.sh
│   └── setup-environment.sh
├── docs/
├── gui/
│   ├── build/
│   │   └── entitlements.mac.plist
│   ├── build.sh
│   ├── command-history.js
│   ├── index.html
│   ├── main.js
│   ├── package-lock.json
│   ├── package.json
│   ├── package.sh
│   ├── preload.js
│   ├── renderer.js
│   ├── styles.css
│   ├── task-history.js
│   └── timeline-view.js
├── tasks/
│   ├── active/
│   │   ├── task_2024-11-24_12-10-34_Environment_Setup_Verification.md
│   │   └── task_2024-11-24_12-12-54_Fix_Discord_Collector_Scraping_Indexing_on_Live_system_as_it's_not_scraping.md
│   ├── archive/
│   └── templates/
├── templates/
│   ├── task.md
│   └── configs/
│       ├── keys.template
│       └── ssh_config.template
└── vscode-extension/
```

## Documentation

- QUICKSTART.md: Getting started guide
- INSTALL.md: Detailed installation instructions
- DEVELOPMENT.md: Contributing guidelines

## License

MIT License
