#!/usr/bin/env python3
"""
Test OpenAI Integration
----------------------

Test structured output and function calling with OpenAI.
"""

import asyncio
from typing import Optional, List
from pydantic import BaseModel
from assistant.openai_manager import OpenAIManager

# Define some test models
class AppLaunch(BaseModel):
    """Model for launching applications"""
    app_name: str
    command: str
    arguments: Optional[List[str]] = None

class SystemCommand(BaseModel):
    """Model for system commands"""
    command: str
    sudo: bool = False
    directory: Optional[str] = None

class SearchQuery(BaseModel):
    """Model for web searches"""
    query: str
    search_engine: str = "google"
    filters: Optional[List[str]] = None

async def main():
    """Test OpenAI integration"""
    openai = OpenAIManager()
    
    # Register test functions
    openai.register_function(
        "launch_app",
        AppLaunch,
        "Launch a macOS application"
    )
    
    openai.register_function(
        "execute_command",
        SystemCommand,
        "Execute a system command"
    )
    
    openai.register_function(
        "web_search",
        SearchQuery,
        "Perform a web search"
    )
    
    # Test structured output
    print("Testing structured output...\n")
    try:
        result = await openai.analyze_task("Open Chrome and go to gmail.com")
        print("Task Analysis:")
        print(f"Type: {result.response.type}")
        print(f"Action: {result.response.action}")
        print(f"Response: {result.response.response}")
        print(f"Confidence: {result.response.confidence}\n")
    except Exception as e:
        print(f"Error testing structured output: {e}\n")
    
    # Test function calling
    print("Testing function calling...\n")
    try:
        result = await openai.call_function(
            "Launch Google Chrome",
            "launch_app",
            "You are a helpful assistant that launches applications on macOS."
        )
        print("Function Call:")
        print(f"Function: {result.function_name}")
        print(f"Arguments: {result.function_args}\n")
    except Exception as e:
        print(f"Error testing function calling: {e}\n")
    
    # Test system command
    print("Testing system command...\n")
    try:
        result = await openai.call_function(
            "Show me the current directory contents",
            "execute_command",
            "You are a helpful assistant that executes system commands safely."
        )
        print("System Command:")
        print(f"Function: {result.function_name}")
        print(f"Arguments: {result.function_args}\n")
    except Exception as e:
        print(f"Error testing system command: {e}\n")

if __name__ == '__main__':
    asyncio.run(main())
