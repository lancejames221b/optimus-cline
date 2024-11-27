#!/usr/bin/env python3
"""Test Perplexity search functionality"""

import asyncio
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assistant.search import ResearchManager

async def test_search():
    """Test Perplexity search functionality"""
    research = ResearchManager()
    
    # Test query about Claude computer use
    query = "What are the latest examples and best practices for using Claude 3.5 Sonnet beta for computer control and automation? Include code examples and safety measures."
    
    print(f"\n=== Query: {query} ===\n")
    
    try:
        result = await research.research(query)
        
        print(f"Response:\n{result.response}\n")
        print(f"Model: {result.model}")
        print(f"Tokens: {result.tokens}")
        print(f"Timestamp: {result.timestamp}")
        print("\n" + "="*80 + "\n")
        
        # Save results
        with open(f'search_results_{result.timestamp}.json', 'w') as f:
            json.dump({
                'query': result.query,
                'response': result.response,
                'model': result.model,
                'tokens': result.tokens,
                'timestamp': result.timestamp
            }, f, indent=2)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(test_search())
