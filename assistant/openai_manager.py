"""
OpenAI Integration Manager
------------------------

Handles structured output and function calling using OpenAI's API.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List, Type, Literal
from dataclasses import dataclass
from datetime import datetime
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

@dataclass
class OpenAIResult:
    """Result from OpenAI API"""
    query: str
    response: Any  # Can be structured data or text
    function_name: Optional[str]
    function_args: Optional[Dict[str, Any]]
    model: str
    timestamp: str

class TaskAnalysis(BaseModel):
    """Task analysis result"""
    type: Literal['app_launch', 'web_search', 'system_command', 'general_query'] = Field(
        ...,  # Required field
        description="The type of task to perform"
    )
    action: Optional[str] = Field(
        None,
        description="Command or URL if applicable"
    )
    response: Optional[str] = Field(
        None,
        description="Natural language response if needed"
    )
    confidence: float = Field(
        ...,  # Required field
        description="Number 0-1 indicating confidence",
        ge=0.0,
        le=1.0
    )

class OpenAIManager:
    """Manages OpenAI API interactions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            with open('/Volumes/SeXternal/keys.txt') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.split('=')[1].strip()
                        break
        
        if not api_key:
            self.logger.warning("OpenAI API key not found")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        
        # Default model - using gpt-o1-mini for best cost/performance ratio
        self.default_model = "gpt-o1-mini"
        
        # Function definitions
        self.functions = {}
    
    def register_function(self, func_name: str, model: Type[BaseModel], description: str):
        """Register a function with its Pydantic model"""
        self.functions[func_name] = {
            'model': model,
            'description': description,
            'schema': model.model_json_schema()
        }
    
    def _create_function_spec(self, func_name: str) -> Dict[str, Any]:
        """Create OpenAI function specification"""
        func_info = self.functions[func_name]
        return {
            'name': func_name,
            'description': func_info['description'],
            'parameters': func_info['schema']
        }
    
    async def get_structured_output(self, 
                                  query: str, 
                                  output_model: Type[BaseModel],
                                  context: Optional[str] = None,
                                  research_context: Optional[str] = None,
                                  model: Optional[str] = None) -> OpenAIResult:
        """Get structured output adhering to a Pydantic model"""
        if not self.client:
            raise Exception("OpenAI client not initialized")
        
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
            
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                response_format={'type': 'json_object'}
            )
            
            # Parse response into model
            response_text = response.choices[0].message.content
            structured_data = output_model.model_validate_json(response_text)
            
            return OpenAIResult(
                query=query,
                response=structured_data,
                function_name=None,
                function_args=None,
                model=model or self.default_model,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting structured output: {e}")
            raise
    
    async def call_function(self,
                          query: str,
                          func_name: str,
                          context: Optional[str] = None,
                          model: Optional[str] = None) -> OpenAIResult:
        """Call a registered function with OpenAI"""
        if not self.client:
            raise Exception("OpenAI client not initialized")
        
        if func_name not in self.functions:
            raise ValueError(f"Function {func_name} not registered")
        
        try:
            messages = []
            if context:
                messages.append({
                    'role': 'system',
                    'content': context
                })
            
            messages.append({
                'role': 'user',
                'content': query
            })
            
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                tools=[{
                    'type': 'function',
                    'function': self._create_function_spec(func_name)
                }],
                tool_choice={'type': 'function', 'function': {'name': func_name}}
            )
            
            # Get function call details
            tool_call = response.choices[0].message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            
            # Validate args with Pydantic model
            model_class = self.functions[func_name]['model']
            validated_args = model_class(**function_args)
            
            return OpenAIResult(
                query=query,
                response=None,  # Response will come from actual function execution
                function_name=func_name,
                function_args=validated_args.model_dump(),
                model=model or self.default_model,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error calling function: {e}")
            raise
    
    async def analyze_task(self, description: str) -> OpenAIResult:
        """Analyze a task to determine required actions"""
        return await self.get_structured_output(
            query=description,
            output_model=TaskAnalysis,
            context=(
                "You are a task analyzer that determines how to handle user requests.\n\n"
                "Task Types:\n"
                "- app_launch: For launching applications (e.g., 'Open Chrome')\n"
                "- web_search: For internet searches or real-time info (e.g., weather, news)\n"
                "- system_command: For file/directory operations (e.g., 'list files')\n"
                "- general_query: For knowledge-based questions (e.g., 'What is Python?')\n\n"
                "Analyze the task and output a JSON object with these fields:\n"
                "1. type: Must be one of the task types above\n"
                "2. action: Command or URL if applicable (optional)\n"
                "3. response: Natural language response if needed (optional)\n"
                "4. confidence: Number between 0 and 1 indicating confidence\n\n"
                "Example responses:\n"
                "{\n"
                '  "type": "app_launch",\n'
                '  "action": "open -a \\"Google Chrome\\"",\n'
                '  "response": "Launching Google Chrome for you",\n'
                '  "confidence": 0.95\n'
                "}\n\n"
                "{\n"
                '  "type": "web_search",\n'
                '  "action": "https://www.google.com/search?q=weather+san+francisco",\n'
                '  "response": "Searching for current weather in San Francisco",\n'
                '  "confidence": 0.9\n'
                "}"
            )
        )
