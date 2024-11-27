#!/usr/bin/env python3
"""
Research Claude Computer Use
--------------------------

Research Claude's computer control capabilities and setup.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research Claude computer control"""
    research = ResearchManager()
    
    queries = [
        "What are Claude's current computer control capabilities? Include setup requirements and limitations.",
        "How does Claude's computer vision and control work? Include technical details about the API.",
        "What are the best practices for implementing Claude's computer control features?",
        "What are the safety considerations and limitations when using Claude for computer control?"
    ]
    
    print("Researching Claude computer control...\n")
    
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
