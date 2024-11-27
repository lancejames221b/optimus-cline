# Optimus Cline

An AI system that can use a computer like a human, handling both development tasks and routine daily activities.

## Features

- Research-first approach using Perplexity AI
- Cost-effective reasoning with GPT-o1-mini
- Computer control with Claude (beta)
- Knowledge caching and pattern learning
- Task type detection and optimization
- Safety measures and monitoring

## File Organization

### Core Components
- `assistant/computer_workflow.py`: Main workflow manager
- `assistant/model_router.py`: Model selection and routing
- `assistant/search.py`: Perplexity integration
- `assistant/openai_manager.py`: OpenAI integration
- `assistant/claude_manager.py`: Claude integration

### Documentation
- `docs/PRD.md`: Product requirements
- `docs/KNOWLEDGE.md`: Knowledge base
- `docs/INTEGRATION.md`: Integration guide
- `docs/QUICKSTART.md`: Quick start guide
- `docs/COMMANDS.md`: Available commands

### Testing
- `test_computer_workflow.py`: Main workflow tests
- `test_search.py`: Search functionality tests
- `test_research_models.py`: Model research tests
- `test_claude.py`: Computer control tests

### Tasks
- `tasks/active/`: Active development tasks
- `tasks/archive/`: Completed tasks
- `tasks/templates/`: Task templates

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/optimus-cline.git
cd optimus-cline
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys:
```bash
cp .env.template .env
# Edit .env with your API keys
```

## Usage

1. Start the system:
```bash
python -m assistant
```

2. Run tests:
```bash
python test_computer_workflow.py
```

## Task Types

### Development Tasks
- Writing code
- Debugging
- System configuration
- Testing

### System Tasks
- File organization
- Application management
- System maintenance
- Backup routines

### Communication Tasks
- Email management
- Slack/Discord interaction
- Document creation
- Meeting notes

### Research Tasks
- Web searches
- Documentation reading
- Learning new tools
- Staying updated

## Model Strategy

### Perplexity AI
- Used for research and staying up-to-date
- Real-time information gathering
- Cost-effective for general queries
- Provides context and citations

### OpenAI GPT-o1-mini
- Used for reasoning and decision making
- Logical reasoning and task planning
- Pattern recognition
- Cost-effective compared to larger models

### Claude (Beta)
- Used for computer control
- Screen interpretation
- Cursor and keyboard control
- Safety measures

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude
- Perplexity for search capabilities
