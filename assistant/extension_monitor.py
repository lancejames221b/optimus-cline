import os
import json
import logging
import asyncio
import aiofiles
import psutil
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
from vscode_integration import VSCodeIntegration, ToolRequest

@dataclass
class ExtensionEvent:
    """Represents a VSCode extension event"""
    type: str
    data: Dict[str, Any]
    timestamp: str

class ExtensionMonitor:
    """Monitors VSCode extension for tool requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.integration = VSCodeIntegration()
        
        # Extension info
        self.extension_path = self.integration.find_cline_extension()
        if not self.extension_path:
            raise RuntimeError("Could not find Cline extension")
        
        # Event handlers
        self.handlers: Dict[str, List[Callable[[ExtensionEvent], None]]] = {
            'tool_request': [],
            'tool_response': [],
            'error': []
        }
    
    def on(self, event_type: str, handler: Callable[[ExtensionEvent], None]):
        """Register event handler"""
        if event_type in self.handlers:
            self.handlers[event_type].append(handler)
    
    def _emit(self, event_type: str, data: Dict[str, Any]):
        """Emit event to handlers"""
        event = ExtensionEvent(
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
    
    async def _watch_extension_logs(self):
        """Watch extension log file for events"""
        log_file = os.path.join(
            os.path.expanduser('~/.vscode/logs'),
            'cline.log'
        )
        
        # Create log file if it doesn't exist
        if not os.path.exists(log_file):
            open(log_file, 'a').close()
        
        # Watch log file
        async with aiofiles.open(log_file) as f:
            while True:
                line = await f.readline()
                if not line:
                    await asyncio.sleep(0.1)
                    continue
                
                try:
                    # Parse log line
                    data = json.loads(line)
                    
                    # Handle tool requests
                    if 'tool' in data:
                        tool_request = self.integration.handle_tool_request(
                            tool=data['tool'],
                            params=data.get('params', {})
                        )
                        
                        self._emit('tool_request', {
                            'request': tool_request.__dict__
                        })
                        
                        # Auto-approve safe tools
                        if tool_request.approved:
                            self._emit('tool_response', {
                                'request': tool_request.__dict__,
                                'approved': True
                            })
                    
                    # Handle errors
                    if 'error' in data:
                        self._emit('error', {
                            'error': data['error']
                        })
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing log line: {e}")
    
    async def _watch_extension_process(self):
        """Watch extension process"""
        try:
            # Find extension process
            extension_pid = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and 'claude-dev' in ' '.join(cmdline):
                        extension_pid = proc.info['pid']
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not extension_pid:
                self.logger.error("Could not find extension process")
                return
            
            # Watch process
            while True:
                try:
                    proc = psutil.Process(extension_pid)
                    await asyncio.sleep(1)
                except psutil.NoSuchProcess:
                    self.logger.error("Extension process died")
                    break
                
        except Exception as e:
            self.logger.error(f"Error watching extension process: {e}")
    
    async def start(self):
        """Start monitoring extension"""
        try:
            # Start watchers
            await asyncio.gather(
                self._watch_extension_logs(),
                self._watch_extension_process()
            )
            
        except Exception as e:
            self.logger.error(f"Error monitoring extension: {e}")
            raise
        finally:
            self.logger.info("Stopped monitoring extension")
