#!/usr/bin/env python3
"""
Test Search Implementation
------------------------

Test the updated search functionality with Perplexity's small online model.
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Test search functionality"""
    research = ResearchManager()
    
    # Test cases
    tests = [
        # Basic search
        {
            'query': "What are the latest developments in AI language models?",
            'context': "Focus on providing accurate, technical information about recent AI developments."
        },
        
        # JSON response
        {
            'query': "List the top 3 programming languages for AI development",
            'context': "Respond with a JSON object containing the languages and their key strengths."
        },
        
        # Error handling
        {
            'query': "",  # Empty query
            'context': None
        },
        
        # Long query
        {
            'query': "Explain in detail how transformer neural networks work, including attention mechanisms, positional encoding, and multi-head attention. Include code examples in Python.",
            'context': "Provide a technical but clear explanation with practical examples."
        },
        
        # Special characters
        {
            'query': "What is the meaning of symbols like λ (lambda) and π (pi) in mathematics?",
            'context': "Explain mathematical symbols and their significance."
        }
    ]
    
    print("Testing search with small online model...\n")
    
    for test in tests:
        print(f"Query: {test['query']}\n")
        
        try:
            # Test cache first
            print("Testing cache...")
            cached_result = research._check_cache(test['query'])
            if cached_result:
                print("Found in cache:")
                print(f"Timestamp: {cached_result.timestamp}")
                print(f"Model: {cached_result.model}")
                print("-" * 80 + "\n")
            
            # Test live search
            print("Testing live search...")
            result = await research.research(
                query=test['query'],
                context=test['context']
            )
            
            print("Response:")
            print("-" * 80)
            print(result.response)
            print("-" * 80)
            print(f"Tokens: {result.tokens}")
            print(f"Model: {result.model}")
            print(f"Timestamp: {result.timestamp}\n")
            
            # Verify cache was saved
            print("Verifying cache...")
            new_cached = research._check_cache(test['query'])
            if new_cached:
                print("Successfully cached")
            else:
                print("Cache verification failed")
            print("-" * 80 + "\n")
            
        except Exception as e:
            print(f"Error: {e}\n")
            print("-" * 80 + "\n")
    
    # Test history
    print("Testing history...")
    history = research.get_history()
    print(f"History entries: {len(history)}")
    if history:
        print("Latest search:")
        print(f"Query: {history[-1].query}")
        print(f"Model: {history[-1].model}")
        print(f"Tokens: {history[-1].tokens}")
    print("-" * 80 + "\n")
    
    # Clear history
    print("Testing clear history...")
    research.clear_history()
    print(f"History entries after clear: {len(research.get_history())}")
    print("-" * 80 + "\n")

if __name__ == '__main__':
    asyncio.run(main())
