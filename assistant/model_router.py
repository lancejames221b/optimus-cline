"""
Model Router for handling requests between Anthropic and OpenRouter APIs
"""

import os
import logging
from enum import Enum
from typing import Optional, Dict, Any, List
import anthropic
import aiohttp
import json
from datetime import datetime

class TaskType(Enum):
    VISION = "vision"
    SYSTEM = "system"
    COMPUTER_USE = "computer_use"
    GENERAL = "general"

class ModelRouter:
    """Routes requests to appropriate API based on task type"""
    
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        # Initialize clients
        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configure endpoints
        self.openrouter_endpoint = "https://openrouter.ai/api/v1/chat/completions"
        
        # Track usage
        self.usage_log = []
    
    async def route_request(
        self,
        task_type: TaskType,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Route request to appropriate API based on task type"""
        
        try:
            # Log request
            self.usage_log.append({
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type.value,
                "model": model,
                "message_count": len(messages)
            })
            
            # Route based on task type
            if task_type in [TaskType.VISION, TaskType.SYSTEM, TaskType.COMPUTER_USE]:
                if not self.anthropic_key:
                    raise ValueError("Anthropic API key required for this task type")
                return await self._anthropic_request(messages, model, **kwargs)
            else:
                return await self._openrouter_request(messages, model, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Error routing request: {e}")
            return await self._handle_error(task_type, messages, model, e, **kwargs)
    
    async def _anthropic_request(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send request to Anthropic API"""
        
        try:
            # Convert messages to Anthropic format
            anthropic_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    # Handle system messages
                    anthropic_messages.append({
                        "role": "assistant",
                        "content": f"System: {msg['content']}"
                    })
                else:
                    anthropic_messages.append(msg)
            
            # Send request
            response = await self.anthropic_client.messages.create(
                model=model or "claude-3-opus-20240229",
                messages=anthropic_messages,
                **kwargs
            )
            
            return {
                "model": response.model,
                "choices": [{"message": response.content[0].text}],
                "usage": response.usage
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise
    
    async def _openrouter_request(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send request to OpenRouter API"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model or "anthropic/claude-3-sonnet-20240229",
                "messages": messages,
                **kwargs
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.openrouter_endpoint,
                    headers=headers,
                    json=data
                ) as response:
                    return await response.json()
                    
        except Exception as e:
            self.logger.error(f"OpenRouter API error: {e}")
            raise
    
    async def _handle_error(
        self,
        task_type: TaskType,
        messages: List[Dict[str, str]],
        model: Optional[str],
        error: Exception,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle API errors with fallback strategies"""
        
        self.logger.warning(f"Attempting error recovery for {task_type.value}")
        
        try:
            if task_type in [TaskType.VISION, TaskType.SYSTEM, TaskType.COMPUTER_USE]:
                # Fallback to OpenRouter for non-specialized tasks
                self.logger.info("Falling back to OpenRouter API")
                return await self._openrouter_request(messages, model, **kwargs)
            else:
                # Fallback to different model
                fallback_model = "anthropic/claude-3-haiku-20240307"
                self.logger.info(f"Falling back to {fallback_model}")
                return await self._openrouter_request(messages, fallback_model, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Error recovery failed: {e}")
            raise RuntimeError(f"All fallback attempts failed: {str(error)} -> {str(e)}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        
        stats = {
            "total_requests": len(self.usage_log),
            "requests_by_type": {},
            "requests_by_model": {}
        }
        
        for entry in self.usage_log:
            # Count by task type
            task_type = entry["task_type"]
            stats["requests_by_type"][task_type] = stats["requests_by_type"].get(task_type, 0) + 1
            
            # Count by model
            if entry["model"]:
                model = entry["model"]
                stats["requests_by_model"][model] = stats["requests_by_model"].get(model, 0) + 1
        
        return stats
