import os
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ToolRequest:
    """Represents a tool request in VSCode"""
    tool: str
    params: Dict[str, Any]
    timestamp: str
    approved: bool = False
    result: Optional[str] = None

class VSCodeIntegration:
    """Integrates with VSCode for tool handling"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # VSCode extension path
        self.extension_dir = os.path.expanduser('~/.vscode/extensions')
        
        # Cache directory
        self.cache_dir = os.path.expanduser('~/.mac-assistant/vscode_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Tool history
        self.history: List[ToolRequest] = []
        self._load_history()
    
    def _load_history(self):
        """Load tool history from cache"""
        history_path = os.path.join(self.cache_dir, 'tool_history.json')
        if os.path.exists(history_path):
            try:
                with open(history_path) as f:
                    data = json.load(f)
                    self.history = [ToolRequest(**tool) for tool in data]
            except Exception as e:
                self.logger.error(f"Error loading history: {e}")
    
    def _save_history(self):
        """Save tool history to cache"""
        history_path = os.path.join(self.cache_dir, 'tool_history.json')
        try:
            with open(history_path, 'w') as f:
                json.dump([tool.__dict__ for tool in self.history], f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    def _analyze_safety(self, tool_request: ToolRequest) -> bool:
        """Analyze tool request for safety"""
        try:
            # Check for dangerous commands
            if tool_request.tool == 'execute_command':
                command = tool_request.params.get('command', '')
                dangerous = ['rm', 'sudo', 'mv', '>', '|']
                return not any(cmd in command for cmd in dangerous)
            
            # Check for file operations
            if tool_request.tool in ['write_to_file', 'read_file']:
                path = tool_request.params.get('path', '')
                return '..' not in path and not path.startswith('/')
            
            # Default to safe
            return True
            
        except Exception as e:
            self.logger.error(f"Error analyzing safety: {e}")
            return False
    
    def handle_tool_request(self, tool: str, params: Dict[str, Any]) -> ToolRequest:
        """Handle a tool request from VSCode"""
        try:
            # Create tool request
            request = ToolRequest(
                tool=tool,
                params=params,
                timestamp=datetime.now().isoformat()
            )
            
            # Analyze safety
            request.approved = self._analyze_safety(request)
            
            # Add to history
            self.history.append(request)
            self._save_history()
            
            return request
            
        except Exception as e:
            self.logger.error(f"Error handling tool request: {e}")
            raise
    
    def get_history(self, limit: Optional[int] = None) -> List[ToolRequest]:
        """Get tool request history"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """Clear tool request history"""
        self.history.clear()
        self._save_history()
    
    def find_cline_extension(self) -> Optional[str]:
        """Find Cline extension directory"""
        try:
            # Look for Cline extension
            for entry in os.listdir(self.extension_dir):
                if entry.startswith('saoudrizwan.claude-dev-'):
                    return os.path.join(self.extension_dir, entry)
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding Cline extension: {e}")
            return None
