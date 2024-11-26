import asyncio
from search import ResearchManager

async def research_cline():
    """Research Cline VSCode extension"""
    research = ResearchManager()
    
    # Core questions about Cline
    queries = [
        "What is Cline VSCode extension from github.com/cline/cline?",
        "How does Cline VSCode extension work with tool use and approvals?",
        "How to integrate with Cline VSCode extension programmatically?",
        "What is the architecture of Cline VSCode extension?"
    ]
    
    print("\nResearching Cline...\n")
    
    for query in queries:
        print(f"\n=== {query} ===\n")
        result = await research.research(query)
        print(result.response)
        print(f"\nModel: {result.model}")
        print(f"Tokens: {result.tokens}\n")
        print("="*80)

if __name__ == '__main__':
    asyncio.run(research_cline())
