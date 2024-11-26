import os
import json
import asyncio
import logging
from browser_control import BrowserControl, BrowserAction, BrowserResult

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_browser_launch():
    """Test browser launch and navigation"""
    print("\n=== Test 1: Browser Launch ===")
    
    browser = BrowserControl()
    
    try:
        # Test launch
        action = BrowserAction(
            action='launch',
            params={'url': 'https://example.com'},
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nLaunch test:")
        print(f"Success: {result.success}")
        print(f"Screenshot: {result.screenshot}")
        print(f"Logs: {result.logs}")
        print(f"Error: {result.error}")
        
        # Test close
        action = BrowserAction(
            action='close',
            params={},
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nClose test:")
        print(f"Success: {result.success}")
        print(f"Error: {result.error}")
        
    finally:
        await browser.cleanup()

async def test_browser_interaction():
    """Test browser interaction"""
    print("\n=== Test 2: Browser Interaction ===")
    
    browser = BrowserControl()
    
    try:
        # Launch browser
        action = BrowserAction(
            action='launch',
            params={'url': 'https://example.com'},
            timestamp='now'
        )
        
        await browser.execute(action)
        
        # Test click
        action = BrowserAction(
            action='click',
            params={'coordinate': '450,300'},  # Center of page
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nClick test:")
        print(f"Success: {result.success}")
        print(f"Screenshot: {result.screenshot}")
        print(f"Logs: {result.logs}")
        print(f"Error: {result.error}")
        
        # Test type
        action = BrowserAction(
            action='type',
            params={'text': 'Hello World'},
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nType test:")
        print(f"Success: {result.success}")
        print(f"Screenshot: {result.screenshot}")
        print(f"Logs: {result.logs}")
        print(f"Error: {result.error}")
        
        # Close browser
        action = BrowserAction(
            action='close',
            params={},
            timestamp='now'
        )
        
        await browser.execute(action)
        
    finally:
        await browser.cleanup()

async def test_browser_scrolling():
    """Test browser scrolling"""
    print("\n=== Test 3: Browser Scrolling ===")
    
    browser = BrowserControl()
    
    try:
        # Launch browser
        action = BrowserAction(
            action='launch',
            params={'url': 'https://example.com'},
            timestamp='now'
        )
        
        await browser.execute(action)
        
        # Test scroll down
        action = BrowserAction(
            action='scroll_down',
            params={},
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nScroll down test:")
        print(f"Success: {result.success}")
        print(f"Screenshot: {result.screenshot}")
        print(f"Logs: {result.logs}")
        print(f"Error: {result.error}")
        
        # Test scroll up
        action = BrowserAction(
            action='scroll_up',
            params={},
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nScroll up test:")
        print(f"Success: {result.success}")
        print(f"Screenshot: {result.screenshot}")
        print(f"Logs: {result.logs}")
        print(f"Error: {result.error}")
        
        # Close browser
        action = BrowserAction(
            action='close',
            params={},
            timestamp='now'
        )
        
        await browser.execute(action)
        
    finally:
        await browser.cleanup()

async def test_error_handling():
    """Test error handling"""
    print("\n=== Test 4: Error Handling ===")
    
    browser = BrowserControl()
    
    try:
        # Test invalid action
        action = BrowserAction(
            action='invalid',
            params={},
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nInvalid action test:")
        print(f"Success: {result.success}")
        print(f"Error: {result.error}")
        
        # Test invalid URL
        action = BrowserAction(
            action='launch',
            params={'url': 'invalid://url'},
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nInvalid URL test:")
        print(f"Success: {result.success}")
        print(f"Error: {result.error}")
        
        # Test invalid coordinates
        action = BrowserAction(
            action='click',
            params={'coordinate': 'invalid'},
            timestamp='now'
        )
        
        result = await browser.execute(action)
        print("\nInvalid coordinates test:")
        print(f"Success: {result.success}")
        print(f"Error: {result.error}")
        
    finally:
        await browser.cleanup()

async def main():
    """Run browser control tests"""
    setup_logging()
    
    print("\nTesting Browser Control...\n")
    
    await test_browser_launch()
    await test_browser_interaction()
    await test_browser_scrolling()
    await test_error_handling()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTests stopped by user")
