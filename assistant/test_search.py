import asyncio
import json
from search import ResearchManager

async def test_search():
    """Test Perplexity search functionality"""
    research = ResearchManager()
    
    # Test queries
    queries = [
        "What are the latest best practices for Python automation on Mac OS?",
        "How to control Chrome browser programmatically on Mac?",
        "What's the most efficient way to handle screen analysis and UI automation on Mac?",
        "Latest methods for Gmail automation without using official API?",
        "How to integrate VSCode automation with Python scripts?"
    ]
    
    print("\nTesting Perplexity Search...\n")
    
    for query in queries:
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
