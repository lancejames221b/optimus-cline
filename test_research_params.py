#!/usr/bin/env python3
"""
Research API Parameters
--------------------

Research the correct parameter names for the OpenAI API.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research API parameters"""
    research = ResearchManager()
    
    query = "What are the correct parameter names for controlling token limits in the latest OpenAI API? Include examples with chat.completions.create()"
    
    print("Researching API parameters...\n")
    print(f"Query: {query}\n")
    
    try:
        result = await research.research(query)
        print("Response:")
        print("-" * 80)
        print(result.response)
        print("-" * 80)
        print(f"Tokens: {result.tokens}")
        print(f"Model: {result.model}\n")
    except Exception as e:
        print(f"Error: {e}\n")

if __name__ == '__main__':
    asyncio.run(main())
