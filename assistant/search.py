import os
import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from openai import AsyncOpenAI

@dataclass
class SearchResult:
    """Result from a search query"""
    query: str
    response: str
    context: Optional[str]
    timestamp: str
    tokens: int
    model: str

class PerplexitySearch:
    """Intelligent search using Perplexity API"""
    
    def __init__(self):
        self.api_key = self._load_api_key()
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Cache directory
        self.cache_dir = os.path.expanduser('~/.mac-assistant/search_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Default to small model for efficiency
        self.default_model = "llama-3.1-sonar-small-128k-online"
    
    def _load_api_key(self) -> str:
        """Load Perplexity API key"""
        # Try environment first
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if api_key:
            return api_key
        
        # Try keys file
        keys_file = '/Volumes/SeXternal/keys.txt'
        if os.path.exists(keys_file):
            with open(keys_file) as f:
                for line in f:
                    if line.startswith('PERPLEXITY_API_KEY='):
                        return line.split('=')[1].strip()
        
        raise ValueError("Perplexity API key not found")
    
    def _get_cache_path(self, query: str) -> str:
        """Get cache file path for query"""
        # Create safe filename from query
        safe_query = "".join(x for x in query if x.isalnum() or x in "._- ")
        safe_query = safe_query[:100]  # Limit length
        return os.path.join(self.cache_dir, f"{safe_query}.json")
    
    def _check_cache(self, query: str) -> Optional[SearchResult]:
        """Check if result is cached"""
        cache_path = self._get_cache_path(query)
        if os.path.exists(cache_path):
            try:
                with open(cache_path) as f:
                    data = json.load(f)
                    # Check if cache is less than 1 hour old
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    age = datetime.now() - timestamp
                    if age.total_seconds() < 3600:  # 1 hour
                        return SearchResult(**data)
            except Exception as e:
                self.logger.error(f"Error reading cache: {e}")
        return None
    
    def _save_cache(self, result: SearchResult):
        """Save result to cache"""
        cache_path = self._get_cache_path(result.query)
        try:
            with open(cache_path, 'w') as f:
                json.dump(result.__dict__, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")
    
    async def search(self, query: str, context: Optional[str] = None) -> SearchResult:
        """Perform search query"""
        # Check cache first
        cached = self._check_cache(query)
        if cached:
            self.logger.info(f"Using cached result for: {query}")
            return cached
        
        # Create system prompt
        if context:
            system_prompt = (
                f"Context: {context}\n\n"
                "Provide accurate, relevant information based on the context. "
                "Focus on practical, actionable insights."
            )
        else:
            system_prompt = (
                "You are a research assistant helping with Mac OS automation and workflows. "
                "Provide accurate, practical information focused on implementation details "
                "and best practices."
            )
        
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        try:
            # Make API request
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=messages
            )
            
            # Create result
            result = SearchResult(
                query=query,
                response=response.choices[0].message.content,
                context=context,
                timestamp=datetime.now().isoformat(),
                tokens=response.usage.total_tokens,
                model=self.default_model
            )
            
            # Cache result
            self._save_cache(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            raise

class ResearchManager:
    """Manages research operations"""
    
    def __init__(self):
        self.search = PerplexitySearch()
        self.history: List[SearchResult] = []
    
    async def research(self, query: str, context: Optional[str] = None) -> SearchResult:
        """Perform research with context awareness"""
        # Add task-specific context
        if context:
            context = (
                f"Task Context: {context}\n"
                "Focus on practical implementation details for Mac OS automation."
            )
        
        # Perform search
        result = await self.search.search(query, context)
        
        # Update history
        self.history.append(result)
        
        return result
    
    def get_history(self, limit: Optional[int] = None) -> List[SearchResult]:
        """Get search history"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """Clear search history"""
        self.history.clear()
