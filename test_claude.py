#!/usr/bin/env python3
"""
Test Claude Integration
---------------------

Test computer control capabilities using Claude.
"""

import os
import asyncio
import base64
from PIL import ImageGrab
from assistant.claude_manager import ClaudeManager

def take_screenshot() -> str:
    """Take screenshot and convert to base64"""
    screenshot = ImageGrab.grab()
    screenshot_path = "test_screenshot.png"
    screenshot.save(screenshot_path)
    
    with open(screenshot_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    os.remove(screenshot_path)
    return encoded_string

async def main():
    """Test Claude computer control"""
    claude = ClaudeManager()
    
    # Update safety settings
    claude.update_safety_settings({
        'max_cursor_speed': 50,  # pixels per second
        'restricted_areas': [
            # Dock area
            {'x1': 0, 'y1': 800, 'x2': 1440, 'y2': 900},
            # Menu bar
            {'x1': 0, 'y1': 0, 'x2': 1440, 'y2': 25}
        ],
        'allowed_apps': [
            'Google Chrome',
            'Visual Studio Code',
            'Terminal'
        ],
        'max_keystrokes': 50
    })
    
    # Test cases
    tasks = [
        # Basic cursor movement
        {
            'task': "Move the cursor to the center of the screen",
            'context': "Need to move cursor safely to screen center"
        },
        
        # Click operation
        {
            'task': "Click the Chrome icon in the dock",
            'context': "Need to launch Chrome browser"
        },
        
        # Text input
        {
            'task': "Type 'Hello, world!' in the active window",
            'context': "Need to input text in current window"
        },
        
        # Complex operation
        {
            'task': "Open Chrome and navigate to github.com",
            'context': "Need to launch Chrome and go to GitHub"
        }
    ]
    
    print("Testing Claude computer control...\n")
    
    for test in tasks:
        print(f"Task: {test['task']}")
        try:
            # Take screenshot for context
            screenshot = take_screenshot()
            
            # Execute task
            result = await claude.execute_task(
                test['task'],
                screenshot=screenshot,
                context=test['context']
            )
            
            print("Response:")
            print(f"Action: {result.action}")
            if result.cursor_pos:
                print(f"Cursor Position: {result.cursor_pos}")
            print("-" * 80 + "\n")
            
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Show performance metrics
    print("Performance Metrics:")
    metrics = claude.get_metrics()
    print(f"Success rate: {metrics['success_rate']:.2%}")
    print(f"Total calls: {metrics['total_calls']}")
    print(f"Average latency: {metrics['average_latency']:.2f}s")

if __name__ == '__main__':
    asyncio.run(main())
