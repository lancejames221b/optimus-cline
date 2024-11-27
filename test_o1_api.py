#!/usr/bin/env python3
"""
Test O1 Model API Usage
---------------------

Research and test the OpenAI o1 model API usage.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research o1 API usage"""
    research = ResearchManager()
    
    queries = [
        "Show Python code examples for using OpenAI's o1-mini and o1-preview models in the API. Include complete working examples.",
        "What are the best practices and parameters for using o1 models in Python? Include rate limits, timeouts, and error handling.",
        "How to handle streaming responses with o1 models in Python? Show example code."
    ]
    
    print("Researching o1 API usage...\n")
    
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
