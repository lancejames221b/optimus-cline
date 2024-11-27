#!/usr/bin/env python3
"""
Test OpenRouter Integration
------------------------

Test using various models through OpenRouter.ai's unified API.
"""

import asyncio
from typing import List
from pydantic import BaseModel, Field
from assistant.openrouter_manager import OpenRouterManager

class CodeSolution(BaseModel):
    """Model for code solution output"""
    code: str = Field(..., description="Implementation code")
    explanation: str = Field(..., description="Explanation of the code")
    complexity: str = Field(..., description="Time and space complexity")
    best_practices: List[str] = Field(default_factory=list, description="Best practices to follow")

async def test_structured_output():
    """Test getting structured output"""
    print("\nTesting structured output with GPT-4o-mini...")
    
    router = OpenRouterManager()
    
    prompt = """
    Write a Python function that implements binary search.
    Include type hints and docstring.
    Explain the time and space complexity.
    """
    
    try:
        result = await router.get_structured_output(
            query=prompt,
            output_model=CodeSolution,
            model="gpt-4o-mini"
        )
        
        print("Response:")
        print("-" * 80)
        print(f"Code:\n{result.response.code}\n")
        print(f"Explanation:\n{result.response.explanation}\n")
        print(f"Complexity:\n{result.response.complexity}\n")
        print("Best Practices:")
        for practice in result.response.best_practices:
            print(f"- {practice}")
        print("-" * 80)
        print(f"Model Used: {result.model}")
        print(f"Timestamp: {result.timestamp}\n")
        
    except Exception as e:
        print(f"Error: {e}")

async def test_chat():
    """Test chat completion"""
    print("\nTesting chat completion with various models...")
    
    router = OpenRouterManager()
    
    models = [
        "gpt-4o-mini",           # Cost-effective GPT-4
        "o1-mini",               # OpenAI's latest reasoning model
        "pplx-small",            # Perplexity's online model
        "claude-3.5-sonnet",     # Claude for computer use
        "claude-3.5-haiku",      # Fast Claude for computer use
        "claude-3.5-sonnet-beta",# Self-moderated Claude for computer use
        "claude-3.5-haiku-beta"  # Self-moderated fast Claude for computer use
    ]
    
    messages = [{
        "role": "user",
        "content": "What are your main capabilities and limitations?"
    }]
    
    for model in models:
        print(f"\nTesting {model}...")
        try:
            result = await router.chat(
                messages=messages,
                model=model
            )
            
            print("Response:")
            print("-" * 80)
            print(result.response)
            print("-" * 80)
            print(f"Model Used: {result.model}")
            print(f"Timestamp: {result.timestamp}\n")
            
        except Exception as e:
            print(f"Error: {e}")

async def test_computer_use():
    """Test computer use capabilities"""
    print("\nTesting computer use capabilities with Claude models...")
    
    router = OpenRouterManager()
    
    models = [
        "claude-3.5-sonnet",
        "claude-3.5-haiku",
        "claude-3.5-sonnet-beta",
        "claude-3.5-haiku-beta"
    ]
    
    messages = [{
        "role": "user",
        "content": """
        Given this Python code:
        ```python
        def process_file(filename):
            with open(filename, 'r') as f:
                content = f.read()
            return content.upper()
        ```
        
        Analyze its computer use capabilities and potential issues:
        1. What system resources does it use?
        2. What error handling should be added?
        3. How could it be made more efficient?
        """
    }]
    
    for model in models:
        print(f"\nTesting {model}...")
        try:
            result = await router.chat(
                messages=messages,
                model=model
            )
            
            print("Response:")
            print("-" * 80)
            print(result.response)
            print("-" * 80)
            print(f"Model Used: {result.model}")
            print(f"Timestamp: {result.timestamp}\n")
            
        except Exception as e:
            print(f"Error: {e}")

async def test_streaming():
    """Test streaming chat completion"""
    print("\nTesting streaming with GPT-4o-mini...")
    
    router = OpenRouterManager()
    
    messages = [{
        "role": "user",
        "content": "Write a haiku about artificial intelligence."
    }]
    
    try:
        stream = await router.chat(
            messages=messages,
            model="gpt-4o-mini",
            stream=True
        )
        
        print("Response:")
        print("-" * 80)
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='', flush=True)
        print("\n" + "-" * 80)
        
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run tests"""
    # Test structured output
    await test_structured_output()
    
    # Test chat completion
    await test_chat()
    
    # Test computer use capabilities
    await test_computer_use()
    
    # Test streaming
    await test_streaming()

if __name__ == '__main__':
    asyncio.run(main())
