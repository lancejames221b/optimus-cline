"""
Tool Executor Module
------------------

Executes tool requests with safety checks.
"""

import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ToolRequest:
    """Tool request"""
    tool: str
    params: Dict[str, Any]
    timestamp: str

@dataclass
class ToolResult:
    """Result of tool execution"""
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None

class ToolExecutor:
    """Executes tool requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Known tools
        self.tools = {
            'execute_command': self._execute_command,
            'read_file': self._read_file,
            'write_to_file': self._write_to_file,
            'list_files': self._list_files,
            'search_files': self._search_files,
            'browser_action': self._browser_action,
            'app_launch': self._app_launch,
            'app_close': self._app_close
        }
        
        # Common applications
        self.apps = {
            'chrome': {
                'name': 'Google Chrome',
                'process': 'chrome',
                'launch': 'open -a "Google Chrome"'
            },
            'firefox': {
                'name': 'Firefox',
                'process': 'firefox',
                'launch': 'open -a Firefox'
            },
            'safari': {
                'name': 'Safari',
                'process': 'safari',
                'launch': 'open -a Safari'
            },
            'vscode': {
                'name': 'Visual Studio Code',
                'process': 'code',
                'launch': 'code'
            },
            'terminal': {
                'name': 'Terminal',
                'process': 'terminal',
                'launch': 'open -a Terminal'
            },
            'mail': {
                'name': 'Mail',
                'process': 'mail',
                'launch': 'open -a Mail'
            }
        }
    
    async def execute(self, request: ToolRequest) -> ToolResult:
        """Execute tool request"""
        try:
            # Get tool handler
            tool = self.tools.get(request.tool)
            if not tool:
                return ToolResult(
                    success=False,
                    error=f"Unknown tool: {request.tool}"
                )
            
            # Execute tool
            return await tool(request.params)
            
        except Exception as e:
            self.logger.error(f"Error executing tool: {e}")
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _execute_command(self, params: Dict[str, Any]) -> ToolResult:
        """Execute system command"""
        try:
            command = params['command']
            
            # Basic safety check
            if any(x in command.lower() for x in ['rm', 'sudo', 'shutdown']):
                return ToolResult(
                    success=False,
                    error="Command not allowed"
                )
            
            # Execute command
            result = os.popen(command).read()
            return ToolResult(
                success=True,
                output=result
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _read_file(self, params: Dict[str, Any]) -> ToolResult:
        """Read file contents"""
        try:
            path = params['path']
            
            # Basic path validation
            if '..' in path or path.startswith('/'):
                return ToolResult(
                    success=False,
                    error="Invalid path"
                )
            
            # Read file
            with open(path, 'r') as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                output=content
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _write_to_file(self, params: Dict[str, Any]) -> ToolResult:
        """Write file contents"""
        try:
            path = params['path']
            content = params['content']
            
            # Basic path validation
            if '..' in path or path.startswith('/'):
                return ToolResult(
                    success=False,
                    error="Invalid path"
                )
            
            # Create directories if needed
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Write file
            with open(path, 'w') as f:
                f.write(content)
            
            return ToolResult(
                success=True
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _list_files(self, params: Dict[str, Any]) -> ToolResult:
        """List files in directory"""
        try:
            path = params.get('path', '.')
            recursive = params.get('recursive', False)
            
            # Basic path validation
            if '..' in path or path.startswith('/'):
                return ToolResult(
                    success=False,
                    error="Invalid path"
                )
            
            # List files
            if recursive:
                files = []
                for root, _, filenames in os.walk(path):
                    for filename in filenames:
                        files.append(os.path.join(root, filename))
            else:
                files = os.listdir(path)
            
            return ToolResult(
                success=True,
                output=files
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _search_files(self, params: Dict[str, Any]) -> ToolResult:
        """Search files for pattern"""
        try:
            path = params.get('path', '.')
            pattern = params['regex']
            file_pattern = params.get('file_pattern', '*')
            
            # Basic path validation
            if '..' in path or path.startswith('/'):
                return ToolResult(
                    success=False,
                    error="Invalid path"
                )
            
            # Search files
            results = []
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    if file_pattern == '*' or filename.endswith(file_pattern):
                        filepath = os.path.join(root, filename)
                        try:
                            with open(filepath, 'r') as f:
                                for line in f:
                                    if pattern in line:
                                        results.append({
                                            'file': filepath,
                                            'line': line.strip()
                                        })
                        except:
                            pass
            
            return ToolResult(
                success=True,
                output=results
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _browser_action(self, params: Dict[str, Any]) -> ToolResult:
        """Handle browser action"""
        try:
            action = params['action']
            
            if action == 'launch':
                url = params.get('url', 'about:blank')
                os.system(f'open -a "Google Chrome" "{url}"')
                return ToolResult(success=True)
                
            elif action == 'close':
                os.system('pkill Chrome')
                return ToolResult(success=True)
                
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown browser action: {action}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _app_launch(self, params: Dict[str, Any]) -> ToolResult:
        """Launch application"""
        try:
            app_name = params['app_name'].lower()
            
            # Check known apps
            if app_name in self.apps:
                app = self.apps[app_name]
                os.system(app['launch'])
                return ToolResult(success=True)
            
            # Try generic launch
            os.system(f'open -a "{app_name}"')
            return ToolResult(success=True)
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _app_close(self, params: Dict[str, Any]) -> ToolResult:
        """Close application"""
        try:
            app_name = params['app_name'].lower()
            
            # Check known apps
            if app_name in self.apps:
                app = self.apps[app_name]
                os.system(f'pkill {app["process"]}')
                return ToolResult(success=True)
            
            # Try generic close
            os.system(f'pkill "{app_name}"')
            return ToolResult(success=True)
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
