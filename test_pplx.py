#!/usr/bin/env python3
"""
Test Perplexity API
------------------

Quick script to query Perplexity about their latest models.
"""

import os
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any

async def query_perplexity(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Query Perplexity API"""
    # Get API key
    if not api_key:
        api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        with open('/Volumes/SeXternal/keys.txt') as f:
            for line in f:
                if line.startswith('PERPLEXITY_API_KEY='):
                    api_key = line.split('=')[1].strip()
                    break
    
    # Make request
    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'mistral-7b-instruct',  # Use Mistral to start
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant focused on providing accurate information about Perplexity AI models and APIs.'
                },
                {
                    'role': 'user',
                    'content': query
                }
            ]
        }
        
        async with session.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=data
        ) as response:
            return await response.json()

async def main():
    """Main function"""
    # Query about models
    query = "What are all the available models in the Perplexity API? Please list them with their capabilities and use cases."
    
    print(f"Querying Perplexity API about available models...\n")
    try:
        result = await query_perplexity(query)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
