#!/usr/bin/env python3
"""
Research O1 Model Names
--------------------

Research the exact API model names for o1-mini and o1-preview.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research o1 model names"""
    research = ResearchManager()
    
    query = "What are the exact API model names for OpenAI's o1-mini and o1-preview models? Include the full model name as used in API calls."
    
    print("Researching o1 model names...\n")
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
