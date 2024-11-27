"""
Computer Use Module
------------------

Handles computer operations and task automation using AI models.
"""

import os
import json
import logging
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class TaskResult:
    """Result of a computer task"""
    success: bool
    action: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    error: Optional[str] = None

class ComputerUse:
    """Main computer use interface"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Known actions
        self.actions = {
            'browser': {
                'launch': 'browser_action',
                'params': lambda url: {
                    'action': 'launch',
                    'url': f'https://{url}' if not url.startswith(('http://', 'https://')) else url
                },
                'description': lambda url: f"Launch browser and navigate to {url}"
            },
            'app': {
                'launch': 'app_launch',
                'params': lambda name: {
                    'app_name': name
                },
                'description': lambda name: f"Launch {name}"
            },
            'file': {
                'read': 'read_file',
                'write': 'write_to_file',
                'list': 'list_files',
                'search': 'search_files'
            }
        }
        
        # URL patterns
        self.url_patterns = [
            r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+)(?:/\S*)?',
            r'([a-zA-Z0-9-]+\.(?:com|org|net|edu|gov|io|app)(?:/\S*)?)',
            r'(?:go to|visit|open)\s+(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+)(?:/\S*)?'
        ]
    
    async def execute_task(self, task: Dict[str, Any]) -> TaskResult:
        """Execute computer task"""
        try:
            if task['type'] == 'analyze':
                message = task['content'].lower()
                
                # Check for URLs first
                url = self._extract_url(message)
                if url:
                    return TaskResult(
                        success=True,
                        action=self.actions['browser']['launch'],
                        params=self.actions['browser']['params'](url),
                        description=self.actions['browser']['description'](url)
                    )
                
                # Check for app launch
                app_match = re.search(r'open\s+(?:up\s+)?(?:the\s+)?([a-zA-Z0-9\s]+?)(?:\s+and|\s+to|\s*$)', message)
                if app_match:
                    app_name = app_match.group(1).strip()
                    return TaskResult(
                        success=True,
                        action=self.actions['app']['launch'],
                        params=self.actions['app']['params'](app_name),
                        description=self.actions['app']['description'](app_name)
                    )
                
                # Check for file operations
                file_match = re.search(r'(?:read|write|create|list)\s+(?:file\s+)?([a-zA-Z0-9\s\./]+)', message)
                if file_match:
                    operation = 'read' if 'read' in message else 'write'
                    path = file_match.group(1).strip()
                    return TaskResult(
                        success=True,
                        action=self.actions['file'][operation],
                        params={'path': path},
                        description=f"{operation} file {path}"
                    )
                
                return TaskResult(
                    success=False,
                    error="Could not understand task"
                )
            
            return TaskResult(
                success=False,
                error=f"Unknown task type: {task['type']}"
            )
            
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            return TaskResult(
                success=False,
                error=str(e)
            )
    
    def _extract_url(self, message: str) -> Optional[str]:
        """Extract URL from message"""
        for pattern in self.url_patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        return None
