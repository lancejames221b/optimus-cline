import os
import json
import logging
import asyncio
import psutil
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from browser_control import BrowserControl

@dataclass
class RecoveryContext:
    """Represents recovery context"""
    error_type: str
    error: str
    context: Dict[str, Any]
    attempt: int

class RecoveryActions:
    """Implements recovery actions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Browser control
        self.browser = BrowserControl()
        
        # Cache directory
        self.cache_dir = os.path.join(
            os.getcwd(),
            '.cache'
        )
        os.makedirs(self.cache_dir, exist_ok=True)
    
    async def restart_browser(self, context: RecoveryContext) -> bool:
        """Restart browser with recovery"""
        try:
            self.logger.info("Restarting browser...")
            
            # Force close if needed
            if context.context.get('force'):
                await self._force_close_browser()
            
            # Clean up browser resources
            await self.browser.cleanup()
            
            # Clear browser cache
            await self._clear_browser_cache()
            
            # Wait before restart
            await asyncio.sleep(1)
            
            # Initialize new browser
            await self.browser._setup_browser()
            
            # Verify browser is running
            if not self.browser.browser:
                raise RuntimeError("Failed to restart browser")
            
            # Navigate to URL if provided
            url = context.context.get('url')
            if url:
                await self.browser.page.goto(
                    url,
                    {
                        'waitUntil': ['load', 'domcontentloaded', 'networkidle0'],
                        'timeout': 60000
                    }
                )
            
            self.logger.info("Browser restarted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restarting browser: {e}")
            return False
    
    async def retry_tool(self, context: RecoveryContext) -> bool:
        """Retry tool execution with recovery"""
        try:
            self.logger.info("Retrying tool execution...")
            
            # Get tool info
            tool = context.context.get('tool')
            if not tool:
                tool = context.context.get('request', {}).get('tool')
            if not tool:
                raise ValueError("No tool specified")
            
            # Clean up resources
            await self._cleanup_tool_resources(tool)
            
            # Get retry params
            params = context.context.get('params', {})
            if not params:
                params = context.context.get('request', {}).get('params', {})
            
            # Apply timeout if specified
            timeout = context.context.get('timeout')
            if timeout and hasattr(self.browser, 'page'):
                await self.browser.page.setDefaultNavigationTimeout(timeout)
            
            # Wait before retry
            await asyncio.sleep(context.attempt)
            
            # Execute retry
            if tool == 'browser_action':
                action = params.get('action')
                if action == 'launch':
                    await self.restart_browser(context)
                elif action == 'click':
                    await self.browser.page.mouse.click(
                        *map(int, params['coordinate'].split(','))
                    )
                elif action in ['scroll_down', 'scroll_up']:
                    direction = 1 if action == 'scroll_down' else -1
                    await self.browser.page.evaluate(
                        f'window.scrollBy(0, {direction} * window.innerHeight)'
                    )
            
            self.logger.info("Tool retry completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error retrying tool: {e}")
            return False
        finally:
            # Restore timeout
            if timeout and hasattr(self.browser, 'page'):
                await self.browser.page.setDefaultNavigationTimeout(30000)
    
    async def restart_extension(self, context: RecoveryContext) -> bool:
        """Restart VSCode extension"""
        try:
            self.logger.info("Restarting extension...")
            
            # Find extension process
            pid = context.context.get('pid')
            if pid:
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait()
                except:
                    pass
            
            # Clean up extension resources
            extension_dir = os.path.expanduser('~/.vscode/extensions')
            for entry in os.listdir(extension_dir):
                if entry.startswith('saoudrizwan.claude-dev-'):
                    # TODO: Implement proper extension restart
                    # This will need VSCode API integration
                    pass
            
            # Wait for restart
            await asyncio.sleep(2)
            
            self.logger.info("Extension restart completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restarting extension: {e}")
            return False
    
    async def cleanup_system(self, context: RecoveryContext) -> bool:
        """Clean up system resources"""
        try:
            self.logger.info("Cleaning up system resources...")
            
            # Full cleanup if specified
            full_cleanup = context.context.get('full', False)
            
            if full_cleanup:
                # Clean up all resources
                await self._cleanup_all_resources()
            else:
                # Clean up specific tool
                tool = context.context.get('tool')
                if tool:
                    await self._cleanup_tool_resources(tool)
            
            # Clear cache
            await self._clear_cache()
            
            self.logger.info("System cleanup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning up system: {e}")
            return False
    
    async def _force_close_browser(self):
        """Force close browser processes"""
        try:
            # Find chrome processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        proc.terminate()
                except:
                    pass
            
            # Wait for processes to close
            await asyncio.sleep(1)
            
        except Exception as e:
            self.logger.error(f"Error force closing browser: {e}")
    
    async def _clear_browser_cache(self):
        """Clear browser cache"""
        try:
            cache_dir = os.path.join(self.cache_dir, 'browser')
            if os.path.exists(cache_dir):
                for entry in os.listdir(cache_dir):
                    path = os.path.join(cache_dir, entry)
                    try:
                        if os.path.isfile(path):
                            os.remove(path)
                        elif os.path.isdir(path):
                            os.rmdir(path)
                    except:
                        pass
                        
        except Exception as e:
            self.logger.error(f"Error clearing browser cache: {e}")
    
    async def _cleanup_tool_resources(self, tool: str):
        """Clean up tool specific resources"""
        try:
            # Clean up based on tool type
            if tool == 'browser_action':
                await self.browser.cleanup()
            elif tool == 'write_to_file':
                # Clean up temp files
                pass
            elif tool == 'execute_command':
                # Clean up processes
                pass
                
        except Exception as e:
            self.logger.error(f"Error cleaning up tool resources: {e}")
    
    async def _cleanup_all_resources(self):
        """Clean up all resources"""
        try:
            # Browser cleanup
            await self.browser.cleanup()
            
            # Process cleanup
            for proc in psutil.process_iter():
                try:
                    if proc.username() == os.getlogin():
                        # Only kill user processes
                        if any(x in proc.name().lower() for x in ['chrome', 'python']):
                            proc.terminate()
                except:
                    pass
            
            # File cleanup
            temp_dirs = [
                os.path.join(self.cache_dir, 'browser'),
                os.path.join(self.cache_dir, 'tools')
            ]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for entry in os.listdir(temp_dir):
                        path = os.path.join(temp_dir, entry)
                        try:
                            if os.path.isfile(path):
                                os.remove(path)
                            elif os.path.isdir(path):
                                os.rmdir(path)
                        except:
                            pass
                            
        except Exception as e:
            self.logger.error(f"Error cleaning up all resources: {e}")
    
    async def _clear_cache(self):
        """Clear all cache"""
        try:
            if os.path.exists(self.cache_dir):
                for entry in os.listdir(self.cache_dir):
                    path = os.path.join(self.cache_dir, entry)
                    try:
                        if os.path.isfile(path):
                            os.remove(path)
                        elif os.path.isdir(path):
                            os.rmdir(path)
                    except:
                        pass
                        
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
