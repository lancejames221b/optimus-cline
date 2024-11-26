import os
import json
import openai
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class SearchModel(Enum):
    """Available Perplexity models"""
    SMALL = "llama-3.1-sonar-small-128k-online"
    LARGE = "llama-3.1-sonar-large-128k-online"
    HUGE = "llama-3.1-sonar-huge-128k-online"

@dataclass
class SearchResult:
    """Result from a search query"""
    query: str
    model: SearchModel
    response: str
    timestamp: str
    cost: float
    tokens: int

class SearchEngine:
    """Intelligent search using Perplexity API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            with open(os.path.expanduser('~/keys.txt')) as f:
                for line in f:
                    if line.startswith('PERPLEXITY_API_KEY='):
                        self.api_key = line.split('=')[1].strip()
                        break
        
        # Configure OpenAI client for Perplexity
        openai.api_key = self.api_key
        openai.api_base = 'https://api.perplexity.ai'
        
        # Cache for search results
        self.cache_dir = os.path.expanduser('~/.cline/search_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cost tracking
        self.cost_per_1k = {
            SearchModel.SMALL: 0.0001,  # Example costs, adjust as needed
            SearchModel.LARGE: 0.0002,
            SearchModel.HUGE: 0.0004
        }
    
    def _get_cache_path(self, query: str, model: SearchModel) -> str:
        """Get cache file path for query"""
        # Create safe filename from query
        safe_query = "".join(x for x in query if x.isalnum() or x in "._- ")
        safe_query = safe_query[:100]  # Limit length
        return os.path.join(
            self.cache_dir,
            f"{safe_query}_{model.value}.json"
        )
    
    def _check_cache(self, query: str, model: SearchModel) -> Optional[SearchResult]:
        """Check if result is cached"""
        cache_path = self._get_cache_path(query, model)
        if os.path.exists(cache_path):
            try:
                with open(cache_path) as f:
                    data = json.load(f)
                    # Check if cache is less than 24 hours old
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    age = datetime.now() - timestamp
                    if age.total_seconds() < 86400:  # 24 hours
                        return SearchResult(**data)
            except Exception as e:
                logging.error(f"Error reading cache: {e}")
        return None
    
    def _save_cache(self, result: SearchResult):
        """Save result to cache"""
        cache_path = self._get_cache_path(result.query, result.model)
        try:
            with open(cache_path, 'w') as f:
                json.dump(result.__dict__, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving cache: {e}")
    
    def _estimate_cost(self, tokens: int, model: SearchModel) -> float:
        """Estimate cost for tokens"""
        return (tokens * self.cost_per_1k[model]) / 1000
    
    async def search(self, query: str, model: SearchModel = SearchModel.SMALL,
                    system_prompt: Optional[str] = None) -> SearchResult:
        """Perform search query"""
        # Check cache first
        cached = self._check_cache(query, model)
        if cached:
            logging.info(f"Using cached result for: {query}")
            return cached
        
        # Default system prompt
        if not system_prompt:
            system_prompt = (
                "You are a search assistant providing accurate, up-to-date "
                "information. Focus on recent developments and current best "
                "practices. Be concise and factual."
            )
        
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        try:
            # Make API request
            response = await openai.ChatCompletion.acreate(
                model=model.value,
                messages=messages
            )
            
            # Extract response
            content = response['choices'][0]['message']['content']
            tokens = response['usage']['total_tokens']
            cost = self._estimate_cost(tokens, model)
            
            # Create result
            result = SearchResult(
                query=query,
                model=model,
                response=content,
                timestamp=datetime.now().isoformat(),
                cost=cost,
                tokens=tokens
            )
            
            # Cache result
            self._save_cache(result)
            
            return result
            
        except Exception as e:
            logging.error(f"Search error: {e}")
            raise

class SearchManager:
    """Manages search operations and results"""
    
    def __init__(self):
        self.engine = SearchEngine()
        self.history: List[SearchResult] = []
        self.total_cost = 0.0
    
    async def search(self, query: str, context: Optional[str] = None,
                    force_model: Optional[SearchModel] = None) -> SearchResult:
        """Perform search with automatic model selection"""
        # Select model based on query complexity
        if force_model:
            model = force_model
        elif len(query) > 1000 or context and len(context) > 1000:
            model = SearchModel.LARGE
        elif any(term in query.lower() for term in ['latest', 'current', 'new']):
            model = SearchModel.LARGE  # Use larger model for recent info
        else:
            model = SearchModel.SMALL  # Default to small model
        
        # Create system prompt with context
        if context:
            system_prompt = (
                f"Context: {context}\n\n"
                "Provide accurate information relevant to the context. "
                "Focus on recent developments and current best practices."
            )
        else:
            system_prompt = None
        
        # Perform search
        result = await self.engine.search(query, model, system_prompt)
        
        # Update history and costs
        self.history.append(result)
        self.total_cost += result.cost
        
        return result
    
    def get_history(self, limit: Optional[int] = None) -> List[SearchResult]:
        """Get search history"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def get_total_cost(self) -> float:
        """Get total cost of searches"""
        return self.total_cost
    
    def clear_history(self):
        """Clear search history"""
        self.history.clear()
        self.total_cost = 0.0
