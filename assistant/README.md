# Optimus Cline

VSCode extension integration for AI assistance with advanced tool execution, error recovery, and performance optimization.

## Features

- VSCode extension integration
- Safe tool execution
- Browser control with screenshots
- Error recovery with retries
- Performance optimization
- Comprehensive monitoring

## Installation

### From PyPI

```bash
pip install optimus-cline
```

### From Source

```bash
git clone https://github.com/lancejames221b/optimus-cline.git
cd optimus-cline/assistant
pip install -e .
```

## Quick Start

1. Install the VSCode extension
2. Install optimus-cline
3. Run the assistant:

```bash
optimus-cline
```

## Usage

### Basic Usage

```python
from assistant import ToolExecutor, ToolRequest

# Create executor
executor = ToolExecutor()

# Execute command
result = await executor.execute(ToolRequest(
    tool='execute_command',
    params={'command': 'echo "Hello World"'},
    timestamp='now'
))

# Check result
if result.success:
    print(f"Output: {result.output}")
```

### Browser Control

```python
# Launch browser
result = await executor.execute(ToolRequest(
    tool='browser_action',
    params={
        'action': 'launch',
        'url': 'https://example.com'
    },
    timestamp='now'
))

# Take screenshot
print(f"Screenshot: {result.output['screenshot']}")
```

### Error Recovery

```python
from assistant import ErrorRecovery

# Create recovery
recovery = ErrorRecovery()

# Handle error
result = await recovery.recover(
    'browser_error',
    'Navigation timeout',
    {'url': 'https://example.com'}
)

if result.success:
    print(f"Recovery succeeded: {result.action}")
```

### Performance Optimization

```python
from assistant import PerformanceOptimizer

# Create optimizer
optimizer = PerformanceOptimizer()

# Batch operations
for i in range(10):
    await optimizer.batch_operation('file_write', {
        'path': f'file_{i}.txt',
        'content': f'Content {i}'
    })
```

## Configuration

Configuration is done through environment variables:

```bash
# VSCode extension path
CLINE_EXTENSION_PATH=~/.vscode/extensions/saoudrizwan.claude-dev-2.1.6.backup

# Browser settings
CLINE_BROWSER_WIDTH=900
CLINE_BROWSER_HEIGHT=600

# Performance settings
CLINE_CACHE_SIZE=1000
CLINE_BATCH_SIZE=10
CLINE_BATCH_TIMEOUT=0.1
```

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

# Run specific test
pytest assistant/test_executor.py

# Run with coverage
pytest --cov=assistant
```

### Build Documentation

```bash
# Build docs
cd docs
make html
```

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
