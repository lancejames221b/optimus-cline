"""
Key Manager Module
----------------

Manages API keys and credentials.
"""

import os
import logging
from typing import Optional, Dict

class KeyManager:
    """Manages API keys and credentials"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keys: Dict[str, str] = {}
        
        # Load keys
        self._load_keys()
    
    def _load_keys(self):
        """Load keys from environment and files"""
        # Try environment variables
        env_keys = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY')
        }
        
        # Try keys file
        keys_file = '/Volumes/SeXternal/keys.txt'
        if os.path.exists(keys_file):
            with open(keys_file) as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_keys[key] = value
        
        # Store valid keys
        for key, value in env_keys.items():
            if value:
                self.keys[key] = value
    
    def has_key(self, key_name: str) -> bool:
        """Check if key exists"""
        return key_name in self.keys
    
    def get_key(self, key_name: str) -> Optional[str]:
        """Get key value"""
        return self.keys.get(key_name)
    
    def set_key(self, key_name: str, value: str):
        """Set key value"""
        self.keys[key_name] = value

# Global instance
_key_manager = KeyManager()

def get_openai_key() -> str:
    """Get OpenAI API key"""
    key = _key_manager.get_key('OPENAI_API_KEY')
    if not key:
        raise ValueError("OpenAI API key not found")
    return key

def get_perplexity_key() -> str:
    """Get Perplexity API key"""
    key = _key_manager.get_key('PERPLEXITY_API_KEY')
    if not key:
        raise ValueError("Perplexity API key not found")
    return key

def get_key_manager() -> KeyManager:
    """Get global key manager instance"""
    return _key_manager
