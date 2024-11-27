"""
OpenRouter Integration Manager
---------------------------

Handles model interactions through OpenRouter.ai's unified API.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List, Type
from dataclasses import dataclass
from datetime import datetime
from openai import AsyncOpenAI
from pydantic import BaseModel
from .key_manager import get_key_manager

@dataclass
class OpenRouterResult:
    """Result from OpenRouter API"""
    query: str
    response: Any  # Can be structured data or text
    model: str
    timestamp: str

class OpenRouterManager:
    """Manages OpenRouter.ai API interactions"""
    
    # Model mappings
    MODEL_MAPPINGS = {
        # GPT-4o Models
        'gpt-4o': 'openai/gpt-4o-2024-11-20',
        'gpt-4o-mini': 'openai/gpt-4o-mini',
        
        # O1 Models
        'o1-preview': 'openai/o1-preview',
        'o1-mini': 'openai/o1-mini',
        
        # Perplexity Models
        'pplx-small': 'perplexity/llama-3.1-sonar-small-128k-online',
        'pplx-large': 'perplexity/llama-3.1-sonar-large-128k-online',
        
        # Claude Computer Use Models
        'claude-3.5-sonnet': 'anthropic/claude-3.5-sonnet',
        'claude-3.5-haiku': 'anthropic/claude-3.5-haiku',
        'claude-3.5-sonnet-beta': 'anthropic/claude-3.5-sonnet:beta',
        'claude-3.5-haiku-beta': 'anthropic/claude-3.5-haiku:beta'
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client with OpenRouter settings
        key_manager = get_key_manager()
        api_key = key_manager.get_key('OPENROUTER_API_KEY')
        if not api_key:
            self.logger.warning("OpenRouter API key not found")
            self.client = None
        else:
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                default_headers={
                    "HTTP-Referer": os.getenv('APP_URL', 'https://github.com/yourusername/optimus-cline'),
                    "X-Title": os.getenv('APP_TITLE', 'Optimus Cline')
                }
            )
        
        # Default model - using gpt-4o-mini for best cost/performance ratio
        self.default_model = "gpt-4o-mini"
    
    def _get_model_id(self, model: str) -> str:
        """Get OpenRouter model ID"""
        return self.MODEL_MAPPINGS.get(model, model)
    
    async def get_structured_output(self, 
                                  query: str, 
                                  output_model: Type[BaseModel],
                                  context: Optional[str] = None,
                                  research_context: Optional[str] = None,
                                  model: Optional[str] = None) -> OpenRouterResult:
        """Get structured output adhering to a Pydantic model"""
        if not self.client:
            raise Exception("OpenRouter client not initialized")
        
        try:
            messages = []
            
            # Add system context
            system_content = []
            if context:
                system_content.append(context)
            if research_context:
                system_content.append(research_context)
            
            system_content.extend([
                "You must respond with a valid JSON object that exactly matches this schema:",
                json.dumps(output_model.model_json_schema(), indent=2),
                "\nImportant rules:",
                "1. Only output valid JSON, no other text",
                "2. All required fields must be included",
                "3. String fields must match any enum restrictions",
                "4. Number fields must be within any specified ranges",
                "5. Follow the exact field names and types",
                "\nInclude the word 'json' in your response to enable JSON mode."
            ])
            
            messages.append({
                'role': 'system',
                'content': "\n\n".join(system_content)
            })
            
            messages.append({
                'role': 'user',
                'content': f"Analyze this and respond with json: {query}"
            })
            
            model_id = self._get_model_id(model or self.default_model)
            
            response = await self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                response_format={'type': 'json_object'}
            )
            
            # Parse response into model
            response_text = response.choices[0].message.content
            structured_data = output_model.model_validate_json(response_text)
            
            return OpenRouterResult(
                query=query,
                response=structured_data,
                model=model_id,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting structured output: {e}")
            raise
    
    async def chat(self,
                  messages: List[Dict[str, str]],
                  model: Optional[str] = None,
                  stream: bool = False) -> OpenRouterResult:
        """Simple chat completion"""
        if not self.client:
            raise Exception("OpenRouter client not initialized")
        
        try:
            model_id = self._get_model_id(model or self.default_model)
            
            response = await self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                stream=stream
            )
            
            if stream:
                return response
            
            return OpenRouterResult(
                query=messages[-1]['content'],
                response=response.choices[0].message.content,
                model=model_id,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error in chat: {e}")
            raise
