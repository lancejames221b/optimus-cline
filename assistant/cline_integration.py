import os
import re
import json
import logging
import asyncio
import subprocess
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ToolUse:
    """Represents a tool use request from Cline"""
    tool: str
    params: Dict[str, Any]
    timestamp: str
    approved: bool = False
    result: Optional[str] = None

class ClineMonitor:
    """Monitors and interacts with Cline CLI"""
    
    def __init__(self, check_path: bool = True, custom_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Track Cline process
        self.process: Optional[asyncio.subprocess.Process] = None
        
        # History of tool uses
        self.history: List[ToolUse] = []
        
        # Cache directory
        self.cache_dir = os.path.expanduser('~/.mac-assistant/cline_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Find Cline executable
        if custom_path:
            self.cline_path = custom_path
        elif check_path:
            self.cline_path = self._find_cline()
        else:
            self.cline_path = 'cline'
        
        # Load history
        self._load_history()
    
    def _find_cline(self) -> str:
        """Find Cline executable path"""
        # Check common locations
        paths = [
            os.path.expanduser('~/.cargo/bin/cline'),  # Cargo install
            '/usr/local/bin/cline',  # Homebrew install
            os.path.expanduser('~/bin/cline'),  # Manual install
            os.path.expanduser('~/.local/bin/cline'),  # User install
            '/opt/homebrew/bin/cline'  # M1 Mac Homebrew
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        # Try finding in PATH
        try:
            result = subprocess.run(
                ['which', 'cline'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        raise FileNotFoundError(
            "Could not find Cline executable. Please ensure it's installed and in your PATH.\n"
            "Common install locations:\n"
            "- ~/.cargo/bin/cline\n"
            "- /usr/local/bin/cline\n"
            "- ~/bin/cline\n"
            "- ~/.local/bin/cline\n"
            "- /opt/homebrew/bin/cline"
        )
    
    def _load_history(self):
        """Load tool use history from cache"""
        history_path = os.path.join(self.cache_dir, 'tool_history.json')
        if os.path.exists(history_path):
            try:
                with open(history_path) as f:
                    data = json.load(f)
                    self.history = [ToolUse(**tool) for tool in data]
            except Exception as e:
                self.logger.error(f"Error loading history: {e}")
    
    def _save_history(self):
        """Save tool use history to cache"""
        history_path = os.path.join(self.cache_dir, 'tool_history.json')
        try:
            with open(history_path, 'w') as f:
                json.dump([tool.__dict__ for tool in self.history], f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    def _parse_tool_use(self, text: str) -> Optional[ToolUse]:
        """Parse tool use from Cline output"""
        try:
            # Extract tool name and parameters
            tool_match = re.search(r'<(\w+)>(.*?)</\1>', text, re.DOTALL)
            if not tool_match:
                return None
            
            tool = tool_match.group(1)
            params_text = tool_match.group(2)
            
            # Extract parameters
            params = {}
            param_matches = re.finditer(
                r'<(\w+)>(.*?)</\1>',
                params_text,
                re.DOTALL
            )
            for match in param_matches:
                params[match.group(1)] = match.group(2).strip()
            
            return ToolUse(
                tool=tool,
                params=params,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing tool use: {e}")
            return None
    
    def _analyze_safety(self, tool_use: ToolUse) -> bool:
        """Analyze tool use for safety"""
        try:
            # Check for dangerous commands
            if tool_use.tool == 'execute_command':
                command = tool_use.params.get('command', '')
                dangerous = ['rm', 'sudo', 'mv', '>', '|']
                return not any(cmd in command for cmd in dangerous)
            
            # Check for file operations
            if tool_use.tool in ['write_to_file', 'read_file']:
                path = tool_use.params.get('path', '')
                return '..' not in path and not path.startswith('/')
            
            # Default to safe
            return True
            
        except Exception as e:
            self.logger.error(f"Error analyzing safety: {e}")
            return False
    
    async def start_monitoring(self, callback: Optional[Callable[[ToolUse], None]] = None):
        """Start monitoring Cline output"""
        try:
            # Start Cline process
            self.process = await asyncio.create_subprocess_exec(
                self.cline_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            # Monitor output
            while True:
                if self.process.stdout:
                    line = await self.process.stdout.readline()
                    if not line:
                        break
                    
                    # Parse output
                    text = line.decode().strip()
                    tool_use = self._parse_tool_use(text)
                    
                    if tool_use:
                        # Analyze safety
                        tool_use.approved = self._analyze_safety(tool_use)
                        
                        # Add to history
                        self.history.append(tool_use)
                        self._save_history()
                        
                        # Notify callback
                        if callback:
                            callback(tool_use)
                
        except Exception as e:
            self.logger.error(f"Error monitoring Cline: {e}")
            raise
        finally:
            if self.process:
                self.process.terminate()
    
    async def approve_tool(self, tool_use: ToolUse) -> bool:
        """Approve a tool use request"""
        try:
            # Safety check
            if not self._analyze_safety(tool_use):
                return False
            
            # Mark as approved
            tool_use.approved = True
            self._save_history()
            
            # Send approval
            if self.process and self.process.stdin:
                self.process.stdin.write(b'y\n')
                await self.process.stdin.drain()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error approving tool: {e}")
            return False
    
    def get_history(self, limit: Optional[int] = None) -> List[ToolUse]:
        """Get tool use history"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """Clear tool use history"""
        self.history.clear()
        self._save_history()
