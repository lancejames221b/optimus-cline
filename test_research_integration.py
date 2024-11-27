#!/usr/bin/env python3
"""
Research integration of Anthropic and OpenRouter APIs
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

async def research_api_integration():
    """Research how to best integrate both APIs"""
    
    # Save research results
    results_dir = Path("research_results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"api_integration_{timestamp}.json"
    
    research_topics = [
        {
            "topic": "Anthropic API Capabilities",
            "query": """
            What are the unique capabilities of Anthropic's Claude API, specifically:
            1. Computer vision and image analysis
            2. Computer use and UI automation
            3. System interaction capabilities
            4. Any other specialized features
            Focus on practical implementation details and limitations.
            """,
            "context": "Need to understand what tasks should be routed to Anthropic API"
        },
        {
            "topic": "OpenRouter API Benefits",
            "query": """
            What are the advantages of using OpenRouter API for:
            1. Cost optimization
            2. Model selection flexibility
            3. Fallback options
            4. Performance considerations
            Focus on practical benefits and trade-offs.
            """,
            "context": "Need to understand when to use OpenRouter vs direct APIs"
        },
        {
            "topic": "Integration Architecture",
            "query": """
            How to design a system that integrates both APIs:
            1. Request routing logic
            2. API key management
            3. Error handling and fallbacks
            4. Performance optimization
            Focus on practical implementation patterns.
            """,
            "context": "Need to implement a robust integration"
        }
    ]
    
    results = []
    for topic in research_topics:
        print(f"\nResearching: {topic['topic']}")
        print("-" * 80)
        
        try:
            # Use Perplexity for research
            from assistant.search import ResearchManager
            research = ResearchManager()
            
            result = await research.research(
                query=topic['query'],
                context=topic['context']
            )
            
            results.append({
                "topic": topic['topic'],
                "query": topic['query'],
                "response": result.response,
                "model": result.model,
                "timestamp": result.timestamp
            })
            
            print(f"Response from {result.model}:")
            print(result.response)
            print("-" * 80)
            
        except Exception as e:
            print(f"Error researching {topic['topic']}: {e}")
    
    # Save results
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_file}")

if __name__ == '__main__':
    asyncio.run(research_api_integration())
