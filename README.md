# Mac Assistant

An AI-powered assistant that learns and automates your daily Mac OS workflow. It uses screen analysis and computer control to perform tasks across applications, with intelligent search capabilities powered by Perplexity AI.

## Features

- **Natural Language Interface**: Describe tasks in plain English
- **Screen Analysis**: Understands what's on your screen
- **Application Control**: Works with Chrome, VSCode, Slack, Gmail, etc.
- **Intelligent Search**: Uses Perplexity AI for research and context
- **Learning System**: Adapts to your workflow patterns
- **Task History**: Tracks and learns from past operations

## Requirements

- macOS
- Python 3.8+
- Tesseract OCR (`brew install tesseract`)
- API Keys:
  - Perplexity API key (for intelligent search)

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
Create or edit `/Volumes/SeXternal/keys.txt`:
```ini
[AI Models]
PERPLEXITY_API_KEY=your_key_here
```

5. Grant permissions:
- System Settings > Privacy & Security > Accessibility
- System Settings > Privacy & Security > Screen Recording

## Usage

1. Start the assistant:
```bash
python -m assistant
```

2. Example tasks:
```
task> Open Chrome and search for Python automation
task> Check my Gmail for new messages
task> Create a new document in VSCode
```

3. Available commands:
- `/help`: Show help message
- `/history`: Show task history
- `/clear`: Clear task history
- `/quit`: Exit assistant

## Components

- `search.py`: Intelligent search using Perplexity API
- `computer.py`: Screen analysis and computer control
- `agent.py`: Core assistant logic and task execution
- `chat.py`: Terminal-based chat interface

## Architecture

1. **Task Analysis**:
   - Natural language understanding
   - Task decomposition
   - Context gathering

2. **Screen Understanding**:
   - Real-time screen analysis
   - UI element detection
   - Text recognition (OCR)

3. **Task Execution**:
   - Application control
   - Mouse/keyboard automation
   - Error handling

4. **Learning System**:
   - Pattern recognition
   - Workflow optimization
   - Error correction

## Development

1. Create new branch:
```bash
git checkout -b feature/your-feature
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

## Security

- All operations are local
- No data collection
- Permission-based access
- Secure API handling
- Activity logging

## Future Enhancements

- Multi-monitor support
- Custom workflow creation
- Advanced pattern learning
- Integration with more apps
- Automated optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details
