"""
Claude Integration Manager
------------------------

Handles computer control and system operations using Claude's API.
Beta implementation following Anthropic's computer use guidelines.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import anthropic
from pydantic import BaseModel, Field

@dataclass
class ClaudeResult:
    """Result from Claude API"""
    query: str
    response: str
    action: Optional[Dict[str, Any]]
    screenshot: Optional[str]
    cursor_pos: Optional[Tuple[int, int]]
    model: str
    timestamp: str

class ClaudeManager:
    """Manages Claude API interactions for computer control"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Claude client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            with open('/Volumes/SeXternal/keys.txt') as f:
                for line in f:
                    if line.startswith('ANTHROPIC_API_KEY='):
                        api_key = line.split('=')[1].strip()
                        break
        
        if not api_key:
            self.logger.warning("Claude API key not found")
            self.client = None
        else:
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
        # Default model - using latest Claude model
        self.default_model = "claude-3-sonnet-20240229"
        
        # Performance metrics
        self.metrics = {
            'success_rate': 0.0,
            'total_calls': 0,
            'successful_calls': 0,
            'average_latency': 0.0
        }
        
        # Safety settings
        self.safety_settings = {
            'max_cursor_speed': 50,      # pixels per second (reduced for safety)
            'restricted_areas': [         # screen regions to avoid
                # Menu bar
                {'x1': 0, 'y1': 0, 'x2': 1440, 'y2': 25},
                # Dock
                {'x1': 0, 'y1': 800, 'x2': 1440, 'y2': 900}
            ],
            'allowed_apps': [            # apps that can be controlled
                'Google Chrome',
                'Visual Studio Code',
                'Terminal',
                'Finder'
            ],
            'max_keystrokes': 50,        # max keystrokes per action
            'require_confirmation': True  # require confirmation before actions
        }
    
    def _update_metrics(self, success: bool, latency: float):
        """Update performance metrics"""
        self.metrics['total_calls'] += 1
        if success:
            self.metrics['successful_calls'] += 1
        self.metrics['success_rate'] = (
            self.metrics['successful_calls'] / self.metrics['total_calls']
        )
        
        # Update moving average of latency
        if self.metrics['average_latency'] == 0.0:
            self.metrics['average_latency'] = latency
        else:
            self.metrics['average_latency'] = (
                0.9 * self.metrics['average_latency'] + 
                0.1 * latency
            )
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """Validate action against safety settings"""
        if not action or 'type' not in action:
            return False
            
        if action['type'] == 'cursor_move':
            # Validate cursor movement
            speed = action.get('speed', 0)
            if speed > self.safety_settings['max_cursor_speed']:
                self.logger.warning(f"Cursor speed {speed} exceeds maximum {self.safety_settings['max_cursor_speed']}")
                return False
            
            target = action.get('target', (0, 0))
            for area in self.safety_settings['restricted_areas']:
                if self._point_in_area(target, area):
                    self.logger.warning(f"Target {target} is in restricted area {area}")
                    return False
        
        elif action['type'] == 'keyboard':
            # Validate keyboard input
            keys = action.get('keys', [])
            if len(keys) > self.safety_settings['max_keystrokes']:
                self.logger.warning(f"Keystrokes {len(keys)} exceeds maximum {self.safety_settings['max_keystrokes']}")
                return False
            
            # Check for dangerous key combinations
            dangerous_keys = ['cmd', 'alt', 'ctrl', 'shift']
            key_combo = [k for k in keys if k in dangerous_keys]
            if len(key_combo) > 1:
                self.logger.warning(f"Dangerous key combination detected: {key_combo}")
                return False
        
        elif action['type'] == 'app_control':
            # Validate app control
            app = action.get('app')
            if app not in self.safety_settings['allowed_apps']:
                self.logger.warning(f"App {app} not in allowed list: {self.safety_settings['allowed_apps']}")
                return False
        
        else:
            self.logger.warning(f"Unknown action type: {action['type']}")
            return False
        
        return True
    
    def _point_in_area(self, point: Tuple[int, int], area: Dict[str, int]) -> bool:
        """Check if point is in restricted area"""
        x, y = point
        return (
            area['x1'] <= x <= area['x2'] and
            area['y1'] <= y <= area['y2']
        )
    
    async def execute_task(self, 
                          task: str,
                          screenshot: Optional[str] = None,
                          context: Optional[str] = None) -> ClaudeResult:
        """Execute a computer control task"""
        if not self.client:
            raise Exception("Claude API key not found")
        
        try:
            start_time = datetime.now()
            
            # Build system message
            system = (
                "You are a computer control assistant that helps users interact with their computer. "
                "Analyze the task and screenshot, then provide specific actions to accomplish the task safely and efficiently.\n\n"
                "Important guidelines:\n"
                "1. Prefer keyboard shortcuts over mouse movements when possible\n"
                "2. Move the cursor slowly and deliberately\n"
                "3. Verify each action before proceeding\n"
                "4. Stay within allowed applications\n"
                "5. Avoid restricted screen areas\n\n"
                "Your response should be a JSON object with these fields:\n"
                "- type: The type of action ('cursor_move', 'keyboard', 'app_control')\n"
                "- target: For cursor_move, the (x,y) coordinates to move to\n"
                "- speed: For cursor_move, the speed in pixels per second\n"
                "- keys: For keyboard, array of keys to type\n"
                "- app: For app_control, the application name\n"
                "Example:\n"
                "{\n"
                '  "type": "cursor_move",\n'
                '  "target": [450, 300],\n'
                '  "speed": 50\n'
                "}"
            )
            
            # Build messages
            messages = [
                {
                    'role': 'system',
                    'content': system
                }
            ]
            
            # Add context if provided
            if context:
                messages.append({
                    'role': 'user',
                    'content': context
                })
            
            # Add task and screenshot
            content = [
                {
                    'type': 'text',
                    'text': task
                }
            ]
            if screenshot:
                content.append({
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': 'image/png',
                        'data': screenshot
                    }
                })
            
            messages.append({
                'role': 'user',
                'content': content
            })
            
            # Get response
            response = await self.client.messages.create(
                model=self.default_model,
                max_tokens=1024,
                messages=messages
            )
            
            # Parse response
            try:
                action_text = response.content[0].text
                action = json.loads(action_text)
            except:
                action = None
            
            # Validate action
            if action and not self._validate_action(action):
                raise ValueError("Action failed safety validation")
            
            # Calculate metrics
            end_time = datetime.now()
            latency = (end_time - start_time).total_seconds()
            self._update_metrics(True, latency)
            
            return ClaudeResult(
                query=task,
                response=response.content[0].text,
                action=action,
                screenshot=screenshot,
                cursor_pos=action.get('target') if action else None,
                model=self.default_model,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            self._update_metrics(False, 0.0)
            raise
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        return self.metrics
    
    def update_safety_settings(self, settings: Dict[str, Any]):
        """Update safety settings"""
        self.safety_settings.update(settings)
