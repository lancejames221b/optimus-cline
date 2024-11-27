# AI Model Integration Guide

## Overview

This guide covers the integration of various AI models in the system, including model selection, cost considerations, and best practices.

## Models

### OpenAI Models

#### Primary Models
- **GPT-4o-mini**
  - Model name: `gpt-4o-mini`
  - Cost: $3 per 1M input tokens, $12 per 1M output tokens
  - Use case: Default model for most tasks
  - Features:
    - Better performance than gpt-4-turbo
    - Cost-effective
    - 128K context window
    - Structured output support

- **GPT-4o**
  - Model name: `gpt-4o`
  - Cost: $15 per 1M input tokens, $60 per 1M output tokens
  - Use case: High-accuracy requirements
  - Features:
    - Best performance
    - Multimodal capabilities
    - 128K context window
    - Complex task handling

#### O1 Models (Not Available)
- **Status**: Experimental, not production-ready
- **Access Requirements**:
  - Tier 3: 7+ days history, $100+ spent
  - Tier 4: 14+ days history, $250+ spent
  - Tier 5: 30+ days history, $1000+ spent
- **Model Names**:
  - `o1-mini`
  - `o1-preview` or `o1-preview-new`
- **Note**: Not currently used in our system

### Claude Models

#### Computer Control
- **Claude 3.5 Sonnet**
  - Model name: `claude-3.5-sonnet-v2@20241022`
  - Use case: GUI interaction and computer control
  - Features:
    - Screen interpretation
    - Cursor/keyboard control
    - Safety measures

#### Backup Options
- **Claude 3 Opus**: `claude-3-opus-20240229`
- **Claude 3 Sonnet**: `claude-3-sonnet-20240229`
- **Claude 3.5 Haiku**: `claude-3.5-haiku@20241022`

### Perplexity Models

#### Research
- **Primary Model**
  - Name: `llama-3.1-sonar-small-128k-online`
  - Use case: Information gathering and research
  - Features:
    - Real-time information
    - Cost-effective
    - Context-aware

#### Alternatives
- **Large Model**: `llama-3.1-sonar-large-128k-online`
- **Chat Model**: `llama-3.1-sonar-small-128k-chat`
- **Instruct Model**: `mixtral-8x7b-instruct`

## Integration Strategy

### Model Selection
1. Research tasks:
   ```python
   research = ResearchManager()
   result = await research.research(query)
   ```

2. Reasoning tasks:
   ```python
   openai = OpenAIManager()
   openai.default_model = "gpt-4o-mini"
   result = await openai.get_structured_output(query, output_model)
   ```

3. Computer control:
   ```python
   claude = ClaudeManager()
   result = await claude.control_computer(task)
   ```

### Cost Management
1. Track usage:
   ```python
   def _update_costs(self, amount: float, category: str):
       self.costs[category] += amount
       self.costs['total'] += amount
   ```

2. Estimate costs:
   ```python
   def _estimate_cost(self, tokens: int, model: str) -> float:
       costs = {
           'gpt-4o-mini': {
               'input': 0.000003,  # $3 per 1M tokens
               'output': 0.000012   # $12 per 1M tokens
           }
       }
       # Calculate based on token count
   ```

### Error Handling
1. Model errors:
   ```python
   try:
       result = await model.process(input)
   except ModelError as e:
       logger.error(f"Model error: {e}")
       # Fall back to alternative model
   ```

2. Rate limits:
   ```python
   if response.status == 429:  # Rate limit
       await asyncio.sleep(retry_after)
       return await self.retry_request()
   ```

## Best Practices

### Model Usage
1. Start with research using Perplexity
2. Use GPT-4o-mini for most tasks
3. Upgrade to GPT-4o only when needed
4. Use Claude for computer control

### Cost Optimization
1. Cache frequent queries
2. Batch requests when possible
3. Monitor token usage
4. Set cost alerts

### Safety
1. Validate all outputs
2. Implement rate limiting
3. Handle errors gracefully
4. Monitor performance

## Environment Setup

### API Keys
```bash
# .env file
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
```

### Dependencies
```bash
pip install openai anthropic aiohttp pydantic
```

## Monitoring

### Metrics to Track
1. Response times
2. Token usage
3. Error rates
4. Cost per request
5. Cache hit rates

### Alerts
1. Cost thresholds
2. Error spikes
3. Performance degradation
4. Rate limit warnings

## Future Improvements

### Planned
1. Dynamic model selection
2. Advanced caching
3. Cost optimization
4. Performance monitoring

### Considering
1. Model fallbacks
2. Request batching
3. Response streaming
4. Custom fine-tuning
