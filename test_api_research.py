#!/usr/bin/env python3
"""
Research Anthropic and OpenRouter API integration
"""

import asyncio
from assistant.search import ResearchManager

async def main():
    """Research API capabilities and integration"""
    research = ResearchManager()
    
    queries = [
        {
            "topic": "Anthropic Direct API Features",
            "query": """
            What are the unique features only available through Anthropic's direct API?
            Focus on:
            1. Computer vision and image analysis capabilities
            2. Computer use and UI automation features
            3. System interaction capabilities
            4. Beta features and headers required
            Include specific API parameters and examples.
            """
        },
        {
            "topic": "OpenRouter Model Support",
            "query": """
            What models are available through OpenRouter for:
            1. o1-preview and o1-mini
            2. Latest Claude models (Opus, Sonnet)
            3. GPT-4o-mini and GPT-4o
            4. Perplexity Llama models
            Include token limits and pricing.
            """
        },
        {
            "topic": "Integration Strategy",
            "query": """
            How to effectively integrate both Anthropic and OpenRouter APIs:
            1. When to use each API
            2. How to handle API keys and configuration
            3. Best practices for routing requests
            4. Error handling and fallbacks
            Focus on practical implementation.
            """
        }
    ]
    
    for query_info in queries:
        print(f"\nResearching: {query_info['topic']}")
        print("-" * 80)
        
        try:
            result = await research.research(
                query=query_info['query'],
                context="Focus on practical implementation details"
            )
            
            print(f"Response from {result.model}:")
            print(result.response)
            print("-" * 80)
            
        except Exception as e:
            print(f"Error researching {query_info['topic']}: {e}")

if __name__ == '__main__':
    asyncio.run(main())
