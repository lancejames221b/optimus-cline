#!/usr/bin/env python3
"""
Search for Anthropic and OpenRouter integration
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Search for API integration details"""
    research = ResearchManager()
    
    query = """
    How to integrate both Anthropic and OpenRouter APIs in the same application?
    Need to know:
    1. What capabilities should be routed to each API?
    2. How to handle API keys and configuration?
    3. Best practices for switching between APIs?
    4. Error handling and fallback strategies?
    Focus on practical implementation details.
    
    Specific areas to cover:
    - Computer vision/image analysis (Anthropic)
    - Computer use automation (Anthropic)
    - General text completion (OpenRouter)
    - Cost optimization strategies
    """
    
    context = "Focus on real-world implementation examples and best practices."
    
    try:
        result = await research.research(query=query, context=context)
        print("\nResponse:")
        print("-" * 80)
        print(result.response)
        print("-" * 80)
        print(f"Model: {result.model}")
        print(f"Timestamp: {result.timestamp}\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
