# Implement AI Model Integration

## Objective
Integrate multiple AI models through OpenRouter with cost management and intelligent model selection.

## Implementation Plan

### 1. OpenRouter Integration
- [ ] Create OpenRouter API client
- [ ] Add API key management
- [ ] Implement model availability checking
- [ ] Add usage tracking
- [ ] Handle API errors and rate limits

### 2. Cost Management
- [ ] Implement token counting
- [ ] Add cost calculation
- [ ] Create budget management
- [ ] Add usage alerts
- [ ] Implement cost optimization

### 3. Model Selection Framework
```python
class ModelSelector:
    def __init__(self):
        self.models = {
            'claude-3-sonnet': {
                'capabilities': ['computer_use', 'coding', 'general'],
                'cost_per_1k': 0.003,
                'context_window': 200000
            },
            'gpt-4': {
                'capabilities': ['reasoning', 'planning', 'verification'],
                'cost_per_1k': 0.01,
                'context_window': 8000
            },
            'gemini-pro-1.5': {
                'capabilities': ['large_context', 'bulk_processing'],
                'cost_per_1k': 0.0005,
                'context_window': 1000000
            }
        }
        
    def select_model(self, task_type, input_size, budget):
        """Select best model based on task requirements and budget"""
        suitable_models = []
        for model, specs in self.models.items():
            if (task_type in specs['capabilities'] and
                input_size <= specs['context_window'] and
                self._estimate_cost(input_size, specs['cost_per_1k']) <= budget):
                suitable_models.append((model, specs))
        
        return self._optimize_selection(suitable_models)
```

### 4. Cost Tracking System
```python
class CostTracker:
    def __init__(self):
        self.project_budgets = {}
        self.usage_history = []
        self.alerts = []
    
    def estimate_cost(self, task):
        """Estimate cost before task execution"""
        token_count = self._count_tokens(task)
        model = self._get_model_for_task(task)
        return token_count * model['cost_per_1k'] / 1000
    
    def track_usage(self, task_id, model, tokens_used, cost):
        """Track actual usage after task completion"""
        self.usage_history.append({
            'task_id': task_id,
            'model': model,
            'tokens': tokens_used,
            'cost': cost,
            'timestamp': 'now'
        })
        
        self._check_budget_alerts()
```

### 5. Model Integration
```python
class AIModelManager:
    def __init__(self):
        self.selector = ModelSelector()
        self.cost_tracker = CostTracker()
        self.openrouter = OpenRouterClient()
    
    async def execute_task(self, task):
        """Execute task with appropriate model"""
        # Estimate cost
        estimated_cost = self.cost_tracker.estimate_cost(task)
        if not self._check_budget(estimated_cost):
            raise BudgetError("Task would exceed budget")
        
        # Select model
        model = self.selector.select_model(
            task.type,
            task.input_size,
            self._get_available_budget()
        )
        
        # Execute task
        result = await self.openrouter.complete(
            model=model,
            messages=task.messages
        )
        
        # Track usage
        self.cost_tracker.track_usage(
            task.id,
            model,
            result.usage.total_tokens,
            result.cost
        )
        
        return result
```

## Integration Points

### 1. OpenRouter API
- Authentication
- Model selection
- Request handling
- Response processing
- Error handling

### 2. Cost Management
- Budget configuration
- Cost tracking
- Usage analytics
- Alert system
- Optimization rules

### 3. Model Selection
- Task analysis
- Capability matching
- Cost optimization
- Performance tracking
- Fallback handling

## Security Considerations

1. API Key Management
- Secure storage
- Access control
- Key rotation
- Usage monitoring

2. Cost Controls
- Budget limits
- Usage alerts
- Approval workflows
- Emergency cutoffs

3. Task Verification
- Input validation
- Output verification
- Security checks
- Resource limits

## Next Steps

1. Begin with OpenRouter integration:
   - Implement API client
   - Add key management
   - Test basic completions

2. Add cost management:
   - Implement token counting
   - Add budget system
   - Create usage tracking

3. Build model selection:
   - Define selection rules
   - Add cost optimization
   - Implement fallbacks

4. Enhance security:
   - Add approval system
   - Implement monitoring
   - Add safety checks

## Notes
- Focus on cost efficiency
- Implement robust error handling
- Add comprehensive logging
- Build flexible model selection
- Consider caching for optimization
