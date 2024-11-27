#!/usr/bin/env python3
"""
Research OpenAI Models
---------------------

Quick script to research latest OpenAI models and their pricing.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research OpenAI models"""
    research = ResearchManager()
    
    queries = [
        "What are the latest OpenAI models and their pricing? Focus on the most cost-effective options for JSON structured output.",
        "What is the cheapest OpenAI model that supports function calling and JSON mode? Include pricing details.",
        "Compare GPT-3.5-turbo vs GPT-4-turbo for structured output tasks. Include pricing and capabilities."
    ]
    
    print("Researching OpenAI models and pricing...\n")
    
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
