# Cline Assistant

An AI-powered computer use and task automation system that leverages multiple AI models through OpenRouter and Perplexity.

## Features

- Natural language computer control
- Intelligent file operations
- Application automation
- Smart search capabilities
- Cost-optimized AI model selection
- Comprehensive error recovery

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/lancejames221b/optimus-cline.git
cd optimus-cline/assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
cp .env.template .env
# Edit .env with your API keys
```

4. Run the chat interface:
```bash
python run_chat.py
```

## Usage

### Commands

- `!command` - Execute system command
  ```
  > !ls
  > !pwd
  ```

- `?query` - Search for information
  ```
  > ?python error handling
  > ?how to use git
  ```

- Natural language computer tasks
  ```
  > open Chrome
  > create file test.txt
  > read file example.py
  ```

### Examples

1. File Operations
```
> create new file test.txt
> write to test.txt Hello World
> read test.txt
> list files
```

2. Application Control
```
> open Chrome
> open Visual Studio Code
> close Chrome
```

3. Search
```
> ?how to use git rebase
> ?python async await examples
```

4. System Commands
```
> !ls -la
> !pwd
> !python --version
```

## Components

### 1. AI Integration
- OpenRouter API for Claude Sonnet
- Perplexity API for search
- Model selection optimization
- Cost tracking and budgeting

### 2. Computer Use
- File system operations
- Application interaction
- Browser automation
- GUI element detection

### 3. Search
- Intelligent query processing
- Context-aware search
- Result caching
- Cost optimization

### 4. Error Recovery
- Automatic error recovery
- Retry mechanisms
- Resource cleanup
- Error history tracking

## Configuration

Configuration is done through environment variables in `.env`:

```ini
# AI API Keys
OPENROUTER_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here

# Settings
DEFAULT_MODEL=claude-sonnet
SEARCH_MODEL=llama-3.1-sonar-small-128k-online
MAX_BUDGET_PER_DAY=1.00
```

See `.env.template` for all available options.

## Development

### Setup Development Environment

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Install docs dependencies
pip install -e ".[docs]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=assistant
```

### Build Documentation

```bash
cd docs
make html
```

## Security

- All system commands require explicit approval
- File operations are restricted to working directory
- Application control is limited to allowed apps
- Cost limits prevent excessive API usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

- Lance James (lance@221b.sh)
- Contributors

## Links

- [Documentation](https://github.com/lancejames221b/optimus-cline/docs)
- [Source Code](https://github.com/lancejames221b/optimus-cline)
- [Issue Tracker](https://github.com/lancejames221b/optimus-cline/issues)
