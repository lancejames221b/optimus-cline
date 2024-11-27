"""
Search Engine Module
------------------

Handles intelligent search using Perplexity API.
"""

import os
import json
import logging
import aiohttp
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SearchResult:
    """Search result"""
    text: str
    source: Optional[str] = None
    relevance: float = 1.0
    timestamp: str = ''

class SearchCache:
    """Caches search results"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, List[SearchResult]] = {}
        self.timestamps: Dict[str, str] = {}
    
    def get(self, query: str) -> Optional[List[SearchResult]]:
        """Get cached results"""
        if query in self.cache:
            # Update timestamp
            self.timestamps[query] = datetime.now().isoformat()
            return self.cache[query]
        return None
    
    def set(self, query: str, results: List[SearchResult]):
        """Cache results"""
        # Check size
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest = min(self.timestamps.items(), key=lambda x: x[1])[0]
            del self.cache[oldest]
            del self.timestamps[oldest]
        
        # Add new entry
        self.cache[query] = results
        self.timestamps[query] = datetime.now().isoformat()

class SearchEngine:
    """Handles intelligent search"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Store API key
        self.api_key = api_key
        
        # Initialize cache
        self.cache = SearchCache()
        
        # Search configuration
        self.config = {
            'model': 'llama-3.1-sonar-small-128k-online',
            'max_tokens': 1000,
            'temperature': 0.7,
            'top_p': 0.9
        }
    
    async def search(self, query: str, context: Optional[List[Dict[str, str]]] = None) -> List[SearchResult]:
        """Perform search"""
        try:
            # Check API key
            if not self.api_key:
                self.logger.warning("No API key available")
                return []
            
            # Check cache
            cached = self.cache.get(query)
            if cached:
                return cached
            
            # Prepare request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.config['model'],
                'query': query,
                'max_tokens': self.config['max_tokens'],
                'temperature': self.config['temperature'],
                'top_p': self.config['top_p']
            }
            
            # Add context if provided
            if context:
                data['context'] = context
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.perplexity.ai/search',
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
            
            # Process results
            results = []
            for item in result.get('results', []):
                results.append(SearchResult(
                    text=item['text'],
                    source=item.get('source'),
                    relevance=item.get('relevance', 1.0),
                    timestamp=datetime.now().isoformat()
                ))
            
            # Cache results
            self.cache.set(query, results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error performing search: {e}")
            return []
    
    def get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions"""
        try:
            # Get similar cached queries
            suggestions = []
            for cached_query in self.cache.cache:
                # Simple string matching for now
                if query.lower() in cached_query.lower():
                    suggestions.append(cached_query)
            
            return sorted(suggestions, key=lambda x: self.cache.timestamps[x], reverse=True)[:5]
            
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
            return []
    
    def clear_cache(self):
        """Clear search cache"""
        try:
            self.cache = SearchCache()
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            return {
                'size': len(self.cache.cache),
                'max_size': self.cache.max_size,
                'queries': list(self.cache.cache.keys()),
                'timestamps': self.cache.timestamps
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {}
