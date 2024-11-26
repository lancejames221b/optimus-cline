import os
import json
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import tiktoken

class ModelCapability(Enum):
    """Capabilities that models can have"""
    COMPUTER_USE = "computer_use"
    CODING = "coding"
    REASONING = "reasoning"
    PLANNING = "planning"
    VERIFICATION = "verification"
    LARGE_CONTEXT = "large_context"
    BULK_PROCESSING = "bulk_processing"
    GENERAL = "general"

@dataclass
class ModelSpec:
    """Specification for an AI model"""
    name: str
    capabilities: List[ModelCapability]
    cost_per_1k: float
    context_window: int
    priority: int = 1  # Higher number = higher priority

@dataclass
class TaskRequirement:
    """Requirements for a task"""
    capabilities: List[ModelCapability]
    input_size: int
    max_cost: float
    priority: int = 1

class BudgetError(Exception):
    """Raised when a task would exceed budget"""
    pass

class ModelNotFoundError(Exception):
    """Raised when no suitable model is found"""
    pass

class OpenRouterClient:
    """Client for OpenRouter API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.available_models = self._get_model_specs()
    
    def _get_model_specs(self) -> Dict[str, ModelSpec]:
        """Get specifications for available models"""
        return {
            'claude-3-sonnet': ModelSpec(
                name='claude-3-sonnet',
                capabilities=[
                    ModelCapability.COMPUTER_USE,
                    ModelCapability.CODING,
                    ModelCapability.GENERAL
                ],
                cost_per_1k=0.003,
                context_window=200000,
                priority=3
            ),
            'gpt-4': ModelSpec(
                name='gpt-4',
                capabilities=[
                    ModelCapability.REASONING,
                    ModelCapability.PLANNING,
                    ModelCapability.VERIFICATION
                ],
                cost_per_1k=0.01,
                context_window=8000,
                priority=2
            ),
            'gemini-pro-1.5': ModelSpec(
                name='gemini-pro-1.5',
                capabilities=[
                    ModelCapability.LARGE_CONTEXT,
                    ModelCapability.BULK_PROCESSING
                ],
                cost_per_1k=0.0005,
                context_window=1000000,
                priority=1
            )
        }
    
    async def complete(self, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send completion request to OpenRouter"""
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"OpenRouter API error: {error}")
                return await response.json()

class CostTracker:
    """Tracks and manages AI usage costs"""
    
    def __init__(self):
        self.project_budgets: Dict[str, float] = {}
        self.usage_history: List[Dict[str, Any]] = []
        self.alert_threshold = 0.8  # Alert at 80% of budget
    
    def set_project_budget(self, project_id: str, budget: float):
        """Set budget for a project"""
        self.project_budgets[project_id] = budget
    
    def get_usage(self, project_id: str) -> float:
        """Get total usage for a project"""
        return sum(
            entry['cost'] for entry in self.usage_history
            if entry['project_id'] == project_id
        )
    
    def check_budget(self, project_id: str, estimated_cost: float) -> bool:
        """Check if task is within budget"""
        if project_id not in self.project_budgets:
            return True  # No budget set
            
        current_usage = self.get_usage(project_id)
        budget = self.project_budgets[project_id]
        
        return (current_usage + estimated_cost) <= budget
    
    def track_usage(self, project_id: str, task_id: str,
                   model: str, tokens: int, cost: float):
        """Track usage of AI models"""
        self.usage_history.append({
            'project_id': project_id,
            'task_id': task_id,
            'model': model,
            'tokens': tokens,
            'cost': cost,
            'timestamp': 'now'  # TODO: Add proper timestamp
        })
        
        # Check if we should alert
        if project_id in self.project_budgets:
            usage = self.get_usage(project_id)
            budget = self.project_budgets[project_id]
            if usage >= (budget * self.alert_threshold):
                logging.warning(
                    f"Project {project_id} has used {usage}/{budget} "
                    f"({usage/budget*100:.1f}%) of its budget"
                )

class ModelSelector:
    """Selects appropriate model for tasks"""
    
    def __init__(self, openrouter: OpenRouterClient):
        self.openrouter = openrouter
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def estimate_cost(self, model: str, token_count: int) -> float:
        """Estimate cost for token count"""
        if model not in self.openrouter.available_models:
            raise ValueError(f"Unknown model: {model}")
            
        spec = self.openrouter.available_models[model]
        return (token_count * spec.cost_per_1k) / 1000
    
    def select_model(self, requirements: TaskRequirement) -> str:
        """Select best model for task requirements"""
        suitable_models = []
        
        for model, spec in self.openrouter.available_models.items():
            # Check capabilities
            if not all(cap in spec.capabilities for cap in requirements.capabilities):
                continue
            
            # Check context window
            if requirements.input_size > spec.context_window:
                continue
            
            # Check cost
            estimated_cost = self.estimate_cost(model, requirements.input_size)
            if estimated_cost > requirements.max_cost:
                continue
            
            suitable_models.append((model, spec))
        
        if not suitable_models:
            raise ModelNotFoundError(
                "No suitable model found for requirements: "
                f"{requirements}"
            )
        
        # Sort by priority and cost
        suitable_models.sort(
            key=lambda x: (-x[1].priority, x[1].cost_per_1k)
        )
        
        return suitable_models[0][0]

class AIModelManager:
    """Manages AI model integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.openrouter = OpenRouterClient(api_key)
        self.cost_tracker = CostTracker()
        self.model_selector = ModelSelector(self.openrouter)
    
    async def execute_task(self, project_id: str, task_id: str,
                         requirements: TaskRequirement,
                         messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute a task with appropriate model"""
        try:
            # Count tokens
            total_tokens = sum(
                self.model_selector.count_tokens(msg['content'])
                for msg in messages
            )
            
            # Select model
            model = self.model_selector.select_model(requirements)
            
            # Estimate cost
            estimated_cost = self.model_selector.estimate_cost(
                model, total_tokens
            )
            
            # Check budget
            if not self.cost_tracker.check_budget(project_id, estimated_cost):
                raise BudgetError(
                    f"Task would exceed budget. Estimated cost: ${estimated_cost:.4f}"
                )
            
            # Execute task
            result = await self.openrouter.complete(model, messages)
            
            # Track usage
            self.cost_tracker.track_usage(
                project_id=project_id,
                task_id=task_id,
                model=model,
                tokens=result['usage']['total_tokens'],
                cost=estimated_cost
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error executing task {task_id}: {e}")
            raise
