"""
Cline Chat Interface
------------------

Chat interface for interacting with Cline's capabilities.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from tool_executor import ToolExecutor, ToolRequest
from ai_models import ModelSelector
from computer_use import ComputerUse
from search_engine import SearchEngine
from error_recovery import ErrorRecovery
from key_manager import KeyManager

class ChatInterface:
    """Chat interface for Cline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize key manager
        self.key_manager = KeyManager()
        
        # Check required keys
        if not self.key_manager.has_key('OPENROUTER_API_KEY'):
            self.logger.warning("OpenRouter API key not found")
        if not self.key_manager.has_key('PERPLEXITY_API_KEY'):
            self.logger.warning("Perplexity API key not found")
        
        # Initialize components with keys
        self.executor = ToolExecutor()
        self.model_selector = ModelSelector(
            openrouter_key=self.key_manager.get_key('OPENROUTER_API_KEY'),
            perplexity_key=self.key_manager.get_key('PERPLEXITY_API_KEY')
        )
        self.computer = ComputerUse()
        self.search = SearchEngine(
            api_key=self.key_manager.get_key('PERPLEXITY_API_KEY')
        )
        self.recovery = ErrorRecovery()
        
        # Command history
        self.history = []
    
    async def handle_message(self, message: str) -> str:
        """Handle user message"""
        try:
            # Add to history
            self.history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Check if it's a command
            if message.startswith('!'):
                return await self._handle_command(message[1:])
            
            # Check if it's a search query
            if message.startswith('?'):
                return await self._handle_search(message[1:])
            
            # Otherwise analyze with Claude
            response = await self._handle_chat(message)
            
            # Add to history
            self.history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            
            # Attempt recovery
            try:
                recovery_result = await self.recovery.recover(
                    'chat_error',
                    str(e),
                    {'message': message}
                )
                if recovery_result.success:
                    return f"Recovered from error: {recovery_result.action}"
            except:
                pass
                
            return f"Error: {e}"
    
    async def _handle_command(self, command: str) -> str:
        """Handle system command"""
        try:
            # Execute command
            result = await self.executor.execute(ToolRequest(
                tool='execute_command',
                params={'command': command},
                timestamp='now'
            ))
            
            if result.success:
                return f"Command output:\n{result.output}"
            else:
                return f"Command failed: {result.error}"
                
        except Exception as e:
            return f"Error executing command: {e}"
    
    async def _handle_search(self, query: str) -> str:
        """Handle search query"""
        try:
            # Perform search
            results = await self.search.search(
                query=query,
                context=self.history[-5:]  # Last 5 messages for context
            )
            
            if results:
                return "Search results:\n" + "\n".join(
                    f"- {result.text}" for result in results[:5]
                )
            else:
                return "No results found"
                
        except Exception as e:
            return f"Error performing search: {e}"
    
    async def _handle_chat(self, message: str) -> str:
        """Handle chat message"""
        try:
            # First try computer task
            result = await self.computer.execute_task({
                'type': 'analyze',
                'content': message
            })
            
            if result.success and result.action:
                # Execute the action
                action_result = await self.executor.execute(ToolRequest(
                    tool=result.action,
                    params=result.params,
                    timestamp='now'
                ))
                
                if action_result.success:
                    return f"Completed action: {result.description}"
                else:
                    return f"Action failed: {action_result.error}"
            
            # If not a computer task, query Claude
            model = self.model_selector.select_model(
                task_type='chat',
                input_size=len(message),
                budget=0.01  # Default per-message budget
            )
            
            response = await self.model_selector.query_model(
                model=model,
                prompt=message
            )
            
            if 'error' in response:
                return f"Error: {response['error']}"
            
            return response.get('text', "I'm not sure how to help with that.")
                
        except Exception as e:
            return f"Error in chat: {e}"
