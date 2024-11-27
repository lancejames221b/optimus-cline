#!/usr/bin/env python3
"""
Research Model Names
------------------

Research current model names and capabilities.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research model names"""
    research = ResearchManager()
    
    queries = [
        "What are the current OpenAI GPT-4 model names for API use? Include latest versions like gpt-4-turbo-preview.",
        "What are OpenAI's o1 models? Are they different from GPT-4?",
        "What are the current Claude model names for API use? Include latest versions like claude-3-sonnet.",
        "What are the current Perplexity model names for API use? Include latest versions like llama-3-sonar."
    ]
    
    print("Researching current model names...\n")
    
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
