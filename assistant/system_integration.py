import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
from extension_monitor import ExtensionMonitor
from tool_executor import ToolExecutor
from vscode_integration import ToolRequest

@dataclass
class SystemEvent:
    """Represents a system event"""
    type: str
    data: Dict[str, Any]
    timestamp: str

class SystemIntegration:
    """Integrates extension monitor with tool executor"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.monitor = ExtensionMonitor()
        self.executor = ToolExecutor()
        
        # Event handlers
        self.handlers: Dict[str, List[Callable[[SystemEvent], None]]] = {
            'tool_request': [],
            'tool_response': [],
            'error': []
        }
        
        # Set up monitor handlers
        self.monitor.on('tool_request', self._handle_tool_request)
        self.monitor.on('tool_response', self._handle_tool_response)
        self.monitor.on('error', self._handle_error)
    
    def on(self, event_type: str, handler: Callable[[SystemEvent], None]):
        """Register event handler"""
        if event_type in self.handlers:
            self.handlers[event_type].append(handler)
    
    def _emit(self, event_type: str, data: Dict[str, Any]):
        """Emit event to handlers"""
        event = SystemEvent(
            type=event_type,
            data=data,
            timestamp=datetime.now().isoformat()
        )
        
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error in {event_type} handler: {e}")
    
    async def _handle_tool_request(self, event: Dict[str, Any]):
        """Handle tool request from monitor"""
        try:
            # Extract request
            request = event.get('request')
            if not request:
                raise ValueError("No request in event")
            
            # Create tool request
            tool_request = ToolRequest(**request)
            
            # Emit request event
            self._emit('tool_request', {
                'request': tool_request.__dict__
            })
            
            # Execute tool
            result = await self.executor.execute(tool_request)
            
            # Emit response event
            self._emit('tool_response', {
                'request': tool_request.__dict__,
                'result': result.__dict__
            })
            
        except Exception as e:
            self.logger.error(f"Error handling tool request: {e}")
            self._emit('error', {
                'error': str(e),
                'request': request
            })
    
    async def _handle_tool_response(self, event: Dict[str, Any]):
        """Handle tool response from monitor"""
        try:
            # Extract response
            response = event.get('response')
            if not response:
                raise ValueError("No response in event")
            
            # Emit response event
            self._emit('tool_response', {
                'response': response
            })
            
        except Exception as e:
            self.logger.error(f"Error handling tool response: {e}")
            self._emit('error', {
                'error': str(e),
                'response': response
            })
    
    async def _handle_error(self, event: Dict[str, Any]):
        """Handle error from monitor"""
        try:
            # Extract error
            error = event.get('error')
            if not error:
                raise ValueError("No error in event")
            
            # Emit error event
            self._emit('error', {
                'error': error
            })
            
        except Exception as e:
            self.logger.error(f"Error handling error event: {e}")
            self._emit('error', {
                'error': str(e),
                'original_error': error
            })
    
    async def start(self):
        """Start system integration"""
        try:
            # Start monitor
            await self.monitor.start()
            
        except Exception as e:
            self.logger.error(f"Error starting system: {e}")
            raise
        finally:
            self.logger.info("System integration stopped")
