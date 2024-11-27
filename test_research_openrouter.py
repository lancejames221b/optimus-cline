#!/usr/bin/env python3
"""
Research OpenRouter.ai
-------------------

Research OpenRouter.ai model availability and integration.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research OpenRouter.ai"""
    research = ResearchManager()
    
    queries = [
        "What models are available through OpenRouter.ai? Include GPT-4, Claude, and o1 models if available.",
        "How to use OpenRouter.ai API in Python? Show example code with parameters.",
        "What are the pricing and rate limits for OpenRouter.ai? Compare with direct API access."
    ]
    
    print("Researching OpenRouter.ai...\n")
    
    for query in queries:
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
