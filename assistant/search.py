"""
Search Implementation
-------------------

Handles research operations using Perplexity's small online model through OpenRouter.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assistant.openrouter_manager import OpenRouterManager

@dataclass
class SearchResult:
    """Result from a search query"""
    query: str
    response: str
    context: Optional[str]
    timestamp: str
    tokens: int
    model: str

class SearchError(Exception):
    """Base class for search errors"""
    pass

class ValidationError(SearchError):
    """Input validation errors"""
    pass

class CacheError(SearchError):
    """Cache-related errors"""
    pass

class ResearchManager:
    """Manages research operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenRouter manager
        self.router = OpenRouterManager()
        
        # Default model - using Perplexity through OpenRouter
        self.default_model = 'pplx-small'  # maps to llama-3.1-sonar-small-128k-online
        
        # Search history
        self.history: List[SearchResult] = []
        
        # Cache settings
        self.cache_dir = os.path.expanduser('~/.mac-assistant/search_cache')
        self.cache_duration = 3600  # 1 hour in seconds
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _validate_input(self, query: str):
        """Validate input parameters"""
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")
        if len(query) > 1000:
            raise ValidationError("Query too long (max 1000 characters)")
    
    def _get_cache_path(self, query: str) -> str:
        """Get cache file path for query"""
        # Create safe filename from query
        safe_query = "".join(x for x in query if x.isalnum() or x in "._- ")
        safe_query = safe_query[:100]  # Limit length
        timestamp = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.cache_dir, f"{safe_query}_{timestamp}.json")
    
    def _check_cache(self, query: str) -> Optional[SearchResult]:
        """Check if result is cached"""
        try:
            cache_path = self._get_cache_path(query)
            if os.path.exists(cache_path):
                with open(cache_path) as f:
                    data = json.load(f)
                    # Check if cache is still valid
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    age = datetime.now() - timestamp
                    if age.total_seconds() < self.cache_duration:
                        return SearchResult(**data)
                    else:
                        # Remove expired cache
                        os.remove(cache_path)
        except Exception as e:
            raise CacheError(f"Error reading cache: {e}")
        return None
    
    def _save_cache(self, result: SearchResult):
        """Save result to cache"""
        try:
            cache_path = self._get_cache_path(result.query)
            with open(cache_path, 'w') as f:
                json.dump(result.__dict__, f, indent=2)
        except Exception as e:
            raise CacheError(f"Error saving cache: {e}")
    
    def _clean_old_cache(self):
        """Clean expired cache files"""
        try:
            now = datetime.now()
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    # Check file age
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    age = now - mtime
                    if age.total_seconds() > self.cache_duration:
                        os.remove(filepath)
        except Exception as e:
            self.logger.error(f"Error cleaning cache: {e}")
    
    async def research(self, query: str, context: Optional[str] = None) -> SearchResult:
        """Perform research with context awareness"""
        try:
            # Validate input
            self._validate_input(query)
            
            # Clean old cache files
            self._clean_old_cache()
            
            # Check cache first
            try:
                cached = self._check_cache(query)
                if cached:
                    self.logger.info(f"Using cached result for: {query}")
                    return cached
            except CacheError as e:
                self.logger.warning(f"Cache error: {e}")
            
            # Build messages
            messages = []
            if context:
                messages.append({
                    'role': 'system',
                    'content': context
                })
            messages.append({
                'role': 'user',
                'content': query
            })
            
            # Get response through OpenRouter
            result = await self.router.chat(
                messages=messages,
                model=self.default_model
            )
            
            search_result = SearchResult(
                query=query,
                response=result.response,
                context=context,
                timestamp=datetime.now().isoformat(),
                tokens=0,  # OpenRouter doesn't provide token count yet
                model=result.model
            )
            
            # Cache result
            try:
                self._save_cache(search_result)
            except CacheError as e:
                self.logger.warning(f"Cache error: {e}")
            
            # Update history
            self.history.append(search_result)
            
            return search_result
            
        except Exception as e:
            self.logger.error(f"Research error: {e}")
            return SearchResult(
                query=query,
                response=f"Error: {str(e)}",
                context=context,
                timestamp=datetime.now().isoformat(),
                tokens=0,
                model="fallback"
            )
    
    def get_history(self, limit: Optional[int] = None) -> List[SearchResult]:
        """Get search history"""
        if limit and limit > 0:
            return self.history[-limit:]
        return self.history.copy()  # Return copy to prevent modification
    
    def clear_history(self):
        """Clear search history"""
        self.history.clear()
