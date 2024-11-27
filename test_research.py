#!/usr/bin/env python3
"""
Research Model Capabilities
-------------------------

Quick script to research model capabilities for structured output and computer control.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research model capabilities"""
    research = ResearchManager()
    
    queries = [
        "What are the differences between OpenAI, Claude, and Perplexity for structured JSON output? Include specific features and capabilities.",
        "How does OpenAI's function calling and structured output work? Include examples and best practices.",
        "What are Claude's capabilities for computer control and system operations? Include specific features and limitations.",
        "What are the latest AI models for structured output and computer control tasks?"
    ]
    
    print("Researching model capabilities...\n")
    
    for query in queries:
        print(f"Query: {query}\n")
        try:
            result = await research.research(query)
            print("Response:")
            print("-" * 80)
            print(result.response)
            print("-" * 80 + "\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == '__main__':
    asyncio.run(main())
