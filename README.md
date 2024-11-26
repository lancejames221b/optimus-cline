# Cline: AI-Powered Computer Use and Task Automation

Cline is an intelligent computer use and task automation system that leverages multiple AI models to provide comprehensive automation capabilities. It combines Claude's computer use abilities with Perplexity's search capabilities for efficient and cost-effective task automation.

## Features

- **AI-Powered Automation**
  - Computer use automation with Claude Sonnet
  - Intelligent search with Perplexity models
  - Cost-optimized model selection
  - Result caching and reuse

- **Task Management**
  - Task creation and tracking
  - Command history
  - Project organization
  - Documentation generation

- **Security**
  - API key management
  - Permission system
  - Usage monitoring
  - Audit logging

- **Cost Management**
  - Budget controls
  - Usage tracking
  - Cost optimization
  - Performance monitoring

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lancejames221b/optimus-cline.git
cd optimus-cline
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API keys:
Create a `keys.txt` file in your home directory with:
```
PERPLEXITY_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

## Usage

1. Run the application:
```bash
python run_gui.py
```

2. Select or create a project:
   - Use "Select Project" to open existing project
   - Use "New Project" to create new project

3. Use the available tabs:
   - Tasks: Manage tasks and workflows
   - Computer Use: Control computer automation
   - AI Models: Configure AI settings
   - Search: Perform intelligent searches
   - Security: Manage permissions

## Project Structure

```
optimus-cline/
├── gui/                    # GUI components
│   ├── ai_models.py       # AI model integration
│   ├── search_engine.py   # Search capabilities
│   ├── computer_use.py    # Computer automation
│   └── ...
├── docs/                  # Documentation
│   ├── PRD.md            # Product Requirements
│   └── COMMANDS.md       # Available commands
├── tasks/                 # Task management
│   ├── active/           # Active tasks
│   └── archive/          # Archived tasks
├── templates/            # Project templates
├── requirements.txt      # Dependencies
└── run_gui.py           # Main entry point
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
```

4. Run linter:
```bash
flake8
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details
