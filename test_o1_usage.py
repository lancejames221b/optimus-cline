#!/usr/bin/env python3
"""
Test O1 Model Usage
-----------------

Test using OpenAI's o1-mini and o1-preview models with proper parameters.
"""

import asyncio
from openai import AsyncOpenAI
from assistant.key_manager import get_openai_key

async def test_o1_mini():
    """Test o1-mini model"""
    print("\nTesting o1-mini model...")
    
    # Initialize client with key from manager
    client = AsyncOpenAI(
        api_key=get_openai_key()
    )
    
    # Test parameters based on model specs
    prompt = """
    Write a Python function that implements merge sort. 
    Include type hints and docstring.
    Explain the time and space complexity.
    """
    
    try:
        response = await client.chat.completions.create(
            model="o1-mini",  # Points to latest o1-mini snapshot
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=65536,  # Max output tokens for o1-mini
            temperature=0,  # Deterministic output
            stream=True  # Enable streaming
        )
        
        print("Response:")
        print("-" * 80)
        async for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='', flush=True)
        print("\n" + "-" * 80)
        
    except Exception as e:
        print(f"Error: {e}")

async def test_o1_preview():
    """Test o1-preview model"""
    print("\nTesting o1-preview model...")
    
    # Initialize client with key from manager
    client = AsyncOpenAI(
        api_key=get_openai_key()
    )
    
    # Test parameters based on model specs
    prompt = """
    Analyze this code for potential improvements:
    
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    Suggest optimizations for:
    1. Time complexity
    2. Space complexity
    3. Error handling
    4. Type safety
    """
    
    try:
        response = await client.chat.completions.create(
            model="o1-preview",  # Points to latest o1-preview snapshot
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=32768,  # Max output tokens for o1-preview
            temperature=0,  # Deterministic output
            stream=True  # Enable streaming
        )
        
        print("Response:")
        print("-" * 80)
        async for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='', flush=True)
        print("\n" + "-" * 80)
        
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run tests"""
    # Test o1-mini
    await test_o1_mini()
    
    # Test o1-preview
    await test_o1_preview()

if __name__ == '__main__':
    asyncio.run(main())
