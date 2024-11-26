import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page

@dataclass
class BrowserAction:
    """Represents a browser action"""
    action: str
    params: Dict[str, Any]
    timestamp: str

@dataclass
class BrowserResult:
    """Represents a browser action result"""
    success: bool
    screenshot: Optional[str] = None
    logs: Optional[List[str]] = None
    error: Optional[str] = None

class BrowserControl:
    """Controls browser actions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Browser instance
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # Window size
        self.width = 900
        self.height = 600
        
        # Screenshot directory
        self.screenshot_dir = os.path.join(
            os.getcwd(),
            'screenshots'
        )
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Console logs
        self.logs: List[str] = []
        
        # Event loop
        self.loop = asyncio.get_event_loop()
    
    async def _setup_browser(self):
        """Set up browser if not running"""
        if not self.browser:
            try:
                self.browser = await launch(
                    headless=True,
                    handleSIGINT=False,
                    handleSIGTERM=False,
                    handleSIGHUP=False,
                    args=[
                        f'--window-size={self.width},{self.height}',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process'
                    ]
                )
                self.page = await self.browser.newPage()
                await self.page.setViewport({
                    'width': self.width,
                    'height': self.height
                })
                
                # Set user agent
                await self.page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                
                # Capture console logs
                self.logs = []
                self.page.on('console', lambda msg: self.logs.append(str(msg)))
                
                # Handle page errors
                self.page.on('error', lambda err: self.logs.append(f"Page error: {err}"))
                self.page.on('pageerror', lambda err: self.logs.append(f"Page error: {err}"))
                
            except Exception as e:
                self.logger.error(f"Error setting up browser: {e}")
                await self.cleanup()
                raise
    
    async def _take_screenshot(self) -> Optional[str]:
        """Take screenshot of current page"""
        try:
            if not self.page:
                return None
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'screenshot_{timestamp}.png'
            path = os.path.join(self.screenshot_dir, filename)
            
            # Take screenshot
            await self.page.screenshot({'path': path})
            
            return path
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return None
    
    async def execute(self, action: BrowserAction) -> BrowserResult:
        """Execute a browser action"""
        try:
            # Get handler
            handler = getattr(self, f'_handle_{action.action}', None)
            if not handler:
                return BrowserResult(
                    success=False,
                    error=f"Unknown action: {action.action}"
                )
            
            # Execute action
            await handler(action.params)
            
            # Get results
            screenshot = await self._take_screenshot()
            
            return BrowserResult(
                success=True,
                screenshot=screenshot,
                logs=self.logs.copy()
            )
            
        except Exception as e:
            self.logger.error(f"Error executing browser action: {e}")
            return BrowserResult(
                success=False,
                error=str(e)
            )
        finally:
            if action.action == 'close':
                await self.cleanup()
    
    async def _handle_launch(self, params: Dict[str, Any]):
        """Handle launch action"""
        url = params.get('url')
        if not url:
            raise ValueError("No URL provided")
        
        # Set up browser
        await self._setup_browser()
        
        try:
            # Navigate to URL with timeout and wait options
            response = await self.page.goto(
                url,
                {
                    'waitUntil': ['load', 'domcontentloaded', 'networkidle0'],
                    'timeout': 60000
                }
            )
            
            if not response.ok:
                raise Exception(f"Navigation failed: {response.status} {response.statusText}")
            
            # Wait for page to be ready
            await self.page.waitForFunction(
                'document.readyState === "complete"',
                {'timeout': 10000}
            )
            
        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {e}")
            await self.cleanup()
            raise
    
    async def _handle_click(self, params: Dict[str, Any]):
        """Handle click action"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        coords = params.get('coordinate')
        if not coords:
            raise ValueError("No coordinates provided")
        
        # Parse coordinates
        try:
            x, y = map(int, coords.split(','))
        except ValueError:
            raise ValueError("Invalid coordinates format")
        
        # Validate coordinates
        if not (0 <= x <= self.width and 0 <= y <= self.height):
            raise ValueError("Coordinates out of bounds")
        
        # Click at coordinates
        await self.page.mouse.click(x, y)
        
        # Wait for any resulting navigation
        try:
            await self.page.waitForNavigation({
                'waitUntil': 'networkidle0',
                'timeout': 10000
            })
        except:
            pass  # Ignore timeout if no navigation occurs
    
    async def _handle_type(self, params: Dict[str, Any]):
        """Handle type action"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        text = params.get('text')
        if not text:
            raise ValueError("No text provided")
        
        # Type text
        await self.page.keyboard.type(text)
    
    async def _handle_scroll_down(self, params: Dict[str, Any]):
        """Handle scroll down action"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        # Scroll down one page
        await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
        await asyncio.sleep(0.5)  # Wait for scroll to complete
    
    async def _handle_scroll_up(self, params: Dict[str, Any]):
        """Handle scroll up action"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        # Scroll up one page
        await self.page.evaluate('window.scrollBy(0, -window.innerHeight)')
        await asyncio.sleep(0.5)  # Wait for scroll to complete
    
    async def _handle_close(self, params: Dict[str, Any]):
        """Handle close action"""
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.browser:
                pages = await self.browser.pages()
                for page in pages:
                    await page.close()
                await self.browser.close()
        except Exception as e:
            self.logger.error(f"Error cleaning up browser: {e}")
        finally:
            self.browser = None
            self.page = None
