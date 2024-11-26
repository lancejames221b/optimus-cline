import os
import json
import asyncio
import logging
from system_integration import SystemIntegration, SystemEvent
from vscode_integration import ToolRequest

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_tool_flow():
    """Test complete tool flow"""
    print("\n=== Test 1: Tool Flow ===")
    
    system = SystemIntegration()
    
    # Track events
    events = []
    
    def on_tool_request(event: SystemEvent):
        print("\nTool Request:")
        print(f"Tool: {event.data['request']['tool']}")
        print(f"Params: {event.data['request']['params']}")
        events.append(('request', event))
    
    def on_tool_response(event: SystemEvent):
        print("\nTool Response:")
        if 'request' in event.data:
            print(f"Tool: {event.data['request']['tool']}")
        if 'result' in event.data:
            print(f"Success: {event.data['result']['success']}")
            print(f"Output: {event.data['result']['output']}")
            print(f"Error: {event.data['result']['error']}")
        events.append(('response', event))
    
    def on_error(event: SystemEvent):
        print(f"\nError: {event.data['error']}")
        events.append(('error', event))
    
    # Register handlers
    system.on('tool_request', on_tool_request)
    system.on('tool_response', on_tool_response)
    system.on('error', on_error)
    
    try:
        # Start system
        system_task = asyncio.create_task(system.start())
        
        # Wait for system to start
        await asyncio.sleep(1)
        
        # Simulate tool request
        await system._handle_tool_request({
            'request': {
                'tool': 'execute_command',
                'params': {'command': 'echo "Hello World"'},
                'timestamp': 'now'
            }
        })
        
        # Wait for events
        await asyncio.sleep(1)
        
        # Print event summary
        print("\nEvent Summary:")
        for event_type, event in events:
            print(f"- {event_type}: {event.type}")
        
    finally:
        # Cancel system task
        system_task.cancel()
        try:
            await system_task
        except asyncio.CancelledError:
            pass

async def test_error_handling():
    """Test error handling"""
    print("\n=== Test 2: Error Handling ===")
    
    system = SystemIntegration()
    
    # Track events
    events = []
    
    def on_error(event: SystemEvent):
        print(f"\nError: {event.data['error']}")
        events.append(('error', event))
    
    # Register handler
    system.on('error', on_error)
    
    try:
        # Start system
        system_task = asyncio.create_task(system.start())
        
        # Wait for system to start
        await asyncio.sleep(1)
        
        # Simulate invalid request
        await system._handle_tool_request({
            'request': {
                'tool': 'invalid_tool',
                'params': {},
                'timestamp': 'now'
            }
        })
        
        # Wait for events
        await asyncio.sleep(1)
        
        # Print event summary
        print("\nEvent Summary:")
        for event_type, event in events:
            print(f"- {event_type}: {event.type}")
        
    finally:
        # Cancel system task
        system_task.cancel()
        try:
            await system_task
        except asyncio.CancelledError:
            pass

async def test_browser_flow():
    """Test browser tool flow"""
    print("\n=== Test 3: Browser Flow ===")
    
    system = SystemIntegration()
    
    # Track events
    events = []
    
    def on_tool_request(event: SystemEvent):
        print("\nTool Request:")
        print(f"Tool: {event.data['request']['tool']}")
        print(f"Params: {event.data['request']['params']}")
        events.append(('request', event))
    
    def on_tool_response(event: SystemEvent):
        print("\nTool Response:")
        if 'request' in event.data:
            print(f"Tool: {event.data['request']['tool']}")
        if 'result' in event.data:
            print(f"Success: {event.data['result']['success']}")
            if event.data['result']['output']:
                output = json.loads(event.data['result']['output'])
                print(f"Screenshot: {output.get('screenshot')}")
                print(f"Logs: {output.get('logs')}")
            print(f"Error: {event.data['result']['error']}")
        events.append(('response', event))
    
    def on_error(event: SystemEvent):
        print(f"\nError: {event.data['error']}")
        events.append(('error', event))
    
    # Register handlers
    system.on('tool_request', on_tool_request)
    system.on('tool_response', on_tool_response)
    system.on('error', on_error)
    
    try:
        # Start system
        system_task = asyncio.create_task(system.start())
        
        # Wait for system to start
        await asyncio.sleep(1)
        
        # Simulate browser actions
        actions = [
            {
                'tool': 'browser_action',
                'params': {
                    'action': 'launch',
                    'url': 'https://example.com'
                },
                'timestamp': 'now'
            },
            {
                'tool': 'browser_action',
                'params': {
                    'action': 'click',
                    'coordinate': '450,300'
                },
                'timestamp': 'now'
            },
            {
                'tool': 'browser_action',
                'params': {
                    'action': 'close'
                },
                'timestamp': 'now'
            }
        ]
        
        for action in actions:
            await system._handle_tool_request({'request': action})
            await asyncio.sleep(2)  # Wait for action to complete
        
        # Print event summary
        print("\nEvent Summary:")
        for event_type, event in events:
            print(f"- {event_type}: {event.type}")
        
    finally:
        # Cancel system task
        system_task.cancel()
        try:
            await system_task
        except asyncio.CancelledError:
            pass

async def main():
    """Run system integration tests"""
    setup_logging()
    
    print("\nTesting System Integration...\n")
    
    await test_tool_flow()
    await test_error_handling()
    await test_browser_flow()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTests stopped by user")
