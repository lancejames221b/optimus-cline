import os
import re
import sys
import json
import logging
import asyncio
import subprocess
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
from vscode_integration import ToolRequest
from browser_control import BrowserControl, BrowserAction

@dataclass
class ToolResult:
    """Represents a tool execution result"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None

class ToolExecutor:
    """Executes tool requests safely"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Working directory
        self.work_dir = os.getcwd()
        
        # Browser control
        self.browser = BrowserControl()
        
        # Tool handlers
        self.handlers: Dict[str, Callable[[Dict[str, Any]], ToolResult]] = {
            'execute_command': self._handle_command,
            'write_to_file': self._handle_write,
            'read_file': self._handle_read,
            'search_files': self._handle_search,
            'list_files': self._handle_list,
            'browser_action': self._handle_browser
        }
    
    async def execute(self, request: ToolRequest) -> ToolResult:
        """Execute a tool request"""
        try:
            # Get handler
            handler = self.handlers.get(request.tool)
            if not handler:
                return ToolResult(
                    success=False,
                    error=f"Unknown tool: {request.tool}"
                )
            
            # Time execution
            start = datetime.now()
            
            # Execute tool
            result = await handler(request.params)
            
            # Add duration
            result.duration = (datetime.now() - start).total_seconds()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing tool {request.tool}: {e}")
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _handle_command(self, params: Dict[str, Any]) -> ToolResult:
        """Handle execute_command tool"""
        try:
            command = params.get('command')
            if not command:
                return ToolResult(
                    success=False,
                    error="No command provided"
                )
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.work_dir
            )
            
            # Get output
            stdout, stderr = await process.communicate()
            
            # Check result
            if process.returncode == 0:
                return ToolResult(
                    success=True,
                    output=stdout.decode().strip()
                )
            else:
                return ToolResult(
                    success=False,
                    error=stderr.decode().strip()
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _handle_write(self, params: Dict[str, Any]) -> ToolResult:
        """Handle write_to_file tool"""
        try:
            path = params.get('path')
            content = params.get('content')
            
            if not path or content is None:
                return ToolResult(
                    success=False,
                    error="Missing path or content"
                )
            
            # Ensure path is relative to work dir
            full_path = os.path.join(self.work_dir, path)
            
            # Create directories
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write file
            with open(full_path, 'w') as f:
                f.write(content)
            
            return ToolResult(
                success=True,
                output=f"Wrote {len(content)} bytes to {path}"
            )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _handle_read(self, params: Dict[str, Any]) -> ToolResult:
        """Handle read_file tool"""
        try:
            path = params.get('path')
            if not path:
                return ToolResult(
                    success=False,
                    error="No path provided"
                )
            
            # Ensure path is relative to work dir
            full_path = os.path.join(self.work_dir, path)
            
            # Read file
            with open(full_path) as f:
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
    
    async def _handle_search(self, params: Dict[str, Any]) -> ToolResult:
        """Handle search_files tool"""
        try:
            path = params.get('path')
            regex = params.get('regex')
            file_pattern = params.get('file_pattern', '*')
            
            if not path or not regex:
                return ToolResult(
                    success=False,
                    error="Missing path or regex"
                )
            
            # Ensure path is relative to work dir
            full_path = os.path.join(self.work_dir, path)
            
            # Compile regex
            try:
                pattern = re.compile(regex, re.MULTILINE)
            except re.error as e:
                return ToolResult(
                    success=False,
                    error=f"Invalid regex pattern: {e}"
                )
            
            # Search files
            matches = []
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    if file_pattern == '*' or re.match(file_pattern.replace('*', '.*'), file):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path) as f:
                                content = f.read()
                                
                                # Find matches with context
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if pattern.search(line):
                                        # Get context lines
                                        start = max(0, i - 2)
                                        end = min(len(lines), i + 3)
                                        context = '\n'.join(lines[start:end])
                                        
                                        matches.append({
                                            'file': os.path.relpath(file_path, self.work_dir),
                                            'line': i + 1,
                                            'context': context
                                        })
                        except Exception as e:
                            self.logger.warning(f"Error reading {file_path}: {e}")
            
            return ToolResult(
                success=True,
                output=json.dumps(matches, indent=2)
            )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _handle_list(self, params: Dict[str, Any]) -> ToolResult:
        """Handle list_files tool"""
        try:
            path = params.get('path')
            recursive = params.get('recursive', False)
            
            if not path:
                return ToolResult(
                    success=False,
                    error="No path provided"
                )
            
            # Ensure path is relative to work dir
            full_path = os.path.join(self.work_dir, path)
            
            # List files
            if recursive:
                files = []
                for root, dirs, filenames in os.walk(full_path):
                    rel_root = os.path.relpath(root, self.work_dir)
                    for filename in filenames:
                        files.append(os.path.join(rel_root, filename))
            else:
                files = [
                    f for f in os.listdir(full_path)
                    if os.path.isfile(os.path.join(full_path, f))
                ]
            
            return ToolResult(
                success=True,
                output=json.dumps(files, indent=2)
            )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _handle_browser(self, params: Dict[str, Any]) -> ToolResult:
        """Handle browser_action tool"""
        try:
            action = params.get('action')
            if not action:
                return ToolResult(
                    success=False,
                    error="No action provided"
                )
            
            # Create browser action
            browser_action = BrowserAction(
                action=action,
                params=params,
                timestamp=datetime.now().isoformat()
            )
            
            # Execute action
            result = await self.browser.execute(browser_action)
            
            # Convert result
            if result.success:
                output = {
                    'screenshot': result.screenshot,
                    'logs': result.logs
                }
                return ToolResult(
                    success=True,
                    output=json.dumps(output, indent=2)
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.error
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
