# Migration Guide: 0.1.0 to 1.0.0

## Overview

Version 1.0.0 introduces significant improvements and new features. This guide helps you migrate from version 0.1.0 to 1.0.0.

## Key Changes

### 1. Configuration

#### Before (0.1.0)
```python
from assistant import MacAssistant

assistant = MacAssistant()
```

#### After (1.0.0)
```python
from assistant import MacAssistant
from assistant.chat import AssistantChat

# For programmatic use
assistant = MacAssistant()

# For interactive use
chat = AssistantChat()
await chat.run()
```

### 2. Task History

#### Before (0.1.0)
- Basic task tracking
- No persistence

#### After (1.0.0)
- Persistent task history in `~/.mac-assistant/cache/task_history.json`
- Rich task metadata including timestamps and results
- Command history in terminal interface

### 3. Error Handling

#### Before (0.1.0)
```python
try:
    result = assistant.execute_task(task)
except Exception as e:
    print(f"Error: {e}")
```

#### After (1.0.0)
```python
try:
    result = await assistant.execute_task(task)
except Exception as e:
    logger.error(f"Task failed: {e}")
    # Automatic recovery attempts
    await recovery.recover('task_error', str(e), {})
```

### 4. Research Capabilities

#### Before (0.1.0)
- Basic web searches
- No caching

#### After (1.0.0)
- AI-powered research using Perplexity API
- Context-aware searches
- Result caching with TTL
- Search history tracking

### 5. System Automation

#### Before (0.1.0)
- Basic mouse and keyboard control
- Limited application support

#### After (1.0.0)
- Enhanced UI element detection
- OCR capabilities
- AppleScript integration
- Application-specific commands
- Accessibility support

## Required Changes

1. Update Dependencies
```bash
pip install -r requirements.txt
```

2. Update Configuration
- Create `~/.mac-assistant` directory
- Set up API keys in environment or keys file
- Configure logging

3. Update Code
- Convert to async/await syntax
- Use new error handling
- Update task execution calls

4. Update Permissions
- Grant accessibility permissions
- Allow OCR capabilities
- Configure application control

## New Features

### 1. Chat Interface
```python
from assistant.chat import AssistantChat

chat = AssistantChat()
await chat.run()
```

### 2. Research Integration
```python
from assistant.search import ResearchManager

research = ResearchManager()
result = await research.research("How to automate browser tasks")
```

### 3. Enhanced Automation
```python
from assistant.computer import ComputerController

computer = ComputerController()
computer.activate_app("Chrome")
computer.type_text("Hello World")
```

## Breaking Changes

1. Task Execution
- Now requires async/await
- Returns structured results
- Includes error recovery

2. Configuration
- New directory structure
- Required API keys
- Logging configuration

3. Dependencies
- New required packages
- Updated minimum versions
- Additional system requirements

## Troubleshooting

### Common Issues

1. Task History Migration
```python
# Migrate old history
from assistant.utils import migrate_history
await migrate_history()
```

2. Permission Errors
- Check System Settings > Privacy & Security
- Grant necessary permissions
- Verify file access rights

3. API Configuration
- Ensure API keys are set
- Check API endpoints
- Verify network access

### Support

For additional help:
1. Check the [documentation](docs/QUICKSTART.md)
2. Review [example code](assistant/examples/)
3. Submit issues on GitHub

## Next Steps

1. Review the [CHANGELOG](CHANGELOG.md)
2. Update your code following this guide
3. Test thoroughly in development
4. Deploy to production
