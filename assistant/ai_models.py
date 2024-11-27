"""
AI Model Management
------------------

Handles model selection and API integration for Cline.
"""

import os
import json
import logging
import aiohttp
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    provider: str
    api_url: str
    context_window: int
    cost_per_1k: float
    capabilities: List[str]
    default_for: List[str]

@dataclass
class ModelUsage:
    """Model usage tracking"""
    tokens: int
    cost: float
    timestamp: str

class ModelSelector:
    """Selects appropriate model based on task requirements"""
    
    def __init__(self, openrouter_key: Optional[str] = None, perplexity_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Store API keys
        self.openrouter_key = openrouter_key
        self.perplexity_key = perplexity_key
        
        # Load configurations
        self.models = {
            'claude-sonnet': ModelConfig(
                name='claude-sonnet',
                provider='openrouter',
                api_url='https://openrouter.ai/api/v1',
                context_window=128000,
                cost_per_1k=0.0015,
                capabilities=['chat', 'code', 'analysis'],
                default_for=['computer_use', 'code']
            ),
            'llama-3.1-small': ModelConfig(
                name='llama-3.1-sonar-small-128k-online',
                provider='perplexity',
                api_url='https://api.perplexity.ai',
                context_window=128000,
                cost_per_1k=0.0001,
                capabilities=['search', 'qa'],
                default_for=['search']
            ),
            'llama-3.1-large': ModelConfig(
                name='llama-3.1-sonar-large-128k-online',
                provider='perplexity',
                api_url='https://api.perplexity.ai',
                context_window=128000,
                cost_per_1k=0.0003,
                capabilities=['search', 'qa', 'analysis'],
                default_for=[]
            )
        }
        
        # Usage tracking
        self.usage: Dict[str, List[ModelUsage]] = {
            model: [] for model in self.models
        }
    
    def select_model(self, task_type: str, input_size: int, budget: float) -> str:
        """Select appropriate model for task"""
        try:
            # Check API keys
            if task_type in ['computer_use', 'code'] and not self.openrouter_key:
                self.logger.warning("OpenRouter API key not available")
                task_type = 'search'  # Fall back to search
            
            if task_type == 'search' and not self.perplexity_key:
                self.logger.warning("Perplexity API key not available")
                return 'claude-sonnet'  # Fall back to Claude
            
            # Check for default model
            for model, config in self.models.items():
                if task_type in config.default_for:
                    # Check API key
                    if config.provider == 'openrouter' and not self.openrouter_key:
                        continue
                    if config.provider == 'perplexity' and not self.perplexity_key:
                        continue
                        
                    # Verify budget
                    estimated_cost = (input_size / 1000) * config.cost_per_1k
                    if estimated_cost <= budget:
                        return model
            
            # No default or over budget, find cheapest suitable model
            candidates = []
            for model, config in self.models.items():
                # Check API key
                if config.provider == 'openrouter' and not self.openrouter_key:
                    continue
                if config.provider == 'perplexity' and not self.perplexity_key:
                    continue
                
                # Check capabilities
                if task_type in config.capabilities:
                    # Check context window
                    if input_size <= config.context_window:
                        # Check budget
                        estimated_cost = (input_size / 1000) * config.cost_per_1k
                        if estimated_cost <= budget:
                            candidates.append((model, estimated_cost))
            
            if candidates:
                # Return cheapest suitable model
                return min(candidates, key=lambda x: x[1])[0]
            
            # No suitable model found
            raise ValueError(
                f"No suitable model found for task_type={task_type}, "
                f"input_size={input_size}, budget={budget}"
            )
            
        except Exception as e:
            self.logger.error(f"Error selecting model: {e}")
            # Default to cheapest model
            return 'llama-3.1-small'
    
    async def query_model(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Query selected model"""
        try:
            config = self.models[model]
            
            # Get API key
            api_key = None
            if config.provider == 'openrouter':
                api_key = self.openrouter_key
            elif config.provider == 'perplexity':
                api_key = self.perplexity_key
            
            if not api_key:
                raise ValueError(f"No API key found for {config.provider}")
            
            # Prepare request
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config.name,
                'prompt': prompt,
                **kwargs
            }
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.api_url,
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
            
            # Track usage
            if 'usage' in result:
                self.usage[model].append(ModelUsage(
                    tokens=result['usage']['total_tokens'],
                    cost=(result['usage']['total_tokens'] / 1000) * config.cost_per_1k,
                    timestamp=datetime.now().isoformat()
                ))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error querying model: {e}")
            raise
    
    def get_usage(self, model: Optional[str] = None) -> Dict[str, float]:
        """Get usage statistics"""
        try:
            if model:
                # Get usage for specific model
                usage = self.usage[model]
                return {
                    'tokens': sum(u.tokens for u in usage),
                    'cost': sum(u.cost for u in usage)
                }
            else:
                # Get total usage
                return {
                    model: {
                        'tokens': sum(u.tokens for u in usage),
                        'cost': sum(u.cost for u in usage)
                    }
                    for model, usage in self.usage.items()
                }
        except Exception as e:
            self.logger.error(f"Error getting usage: {e}")
            return {}
