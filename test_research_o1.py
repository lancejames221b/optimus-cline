#!/usr/bin/env python3
"""
Research O1 Models
----------------

Research OpenAI's o1 models and their availability.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research o1 models"""
    research = ResearchManager()
    
    queries = [
        "Are OpenAI's o1 models available for public API use? Include any information about o1-preview and o1-mini.",
        "What are the alternatives to o1 models for complex reasoning tasks? Include GPT-4 turbo and other options.",
        "What is the status of o1 models - are they in testing, beta, or generally available?"
    ]
    
    print("Researching o1 models...\n")
    
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
