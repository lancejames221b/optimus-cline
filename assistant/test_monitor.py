import os
import json
import asyncio
import logging
from extension_monitor import ExtensionMonitor, ExtensionEvent

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def on_tool_request(event: ExtensionEvent):
    """Handle tool request events"""
    print("\nTool Request:")
    print(f"Tool: {event.data['request']['tool']}")
    print(f"Params: {event.data['request']['params']}")
    print(f"Approved: {event.data['request']['approved']}")

def on_tool_response(event: ExtensionEvent):
    """Handle tool response events"""
    print("\nTool Response:")
    print(f"Tool: {event.data['request']['tool']}")
    print(f"Approved: {event.data['approved']}")

def on_error(event: ExtensionEvent):
    """Handle error events"""
    print(f"\nError: {event.data['error']}")

async def test_extension_monitoring():
    """Test extension monitoring"""
    print("\nTesting Extension Monitoring...\n")
    
    try:
        # Create monitor
        monitor = ExtensionMonitor()
        print(f"Found Cline extension at: {monitor.extension_path}")
        
        # Register handlers
        monitor.on('tool_request', on_tool_request)
        monitor.on('tool_response', on_tool_response)
        monitor.on('error', on_error)
        
        print("\nStarting extension monitor...")
        print("Use Cline in VSCode to see events")
        print("Press Ctrl+C to stop\n")
        
        # Start monitoring
        await monitor.start()
        
    except RuntimeError as e:
        print(f"\nError: {e}")
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    except Exception as e:
        print(f"\nError: {e}")

async def test_log_simulation():
    """Test by simulating log entries"""
    print("\nTesting with simulated logs...\n")
    
    # Create test log file
    log_file = os.path.join(
        os.path.expanduser('~/.vscode/logs'),
        'cline.log'
    )
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Sample tool requests
    test_entries = [
        {
            'tool': 'execute_command',
            'params': {'command': 'ls -la'}
        },
        {
            'tool': 'write_to_file',
            'params': {'path': 'test.txt', 'content': 'Hello'}
        },
        {
            'tool': 'read_file',
            'params': {'path': 'config.json'}
        },
        {
            'error': 'Failed to execute command'
        }
    ]
    
    try:
        # Create monitor
        monitor = ExtensionMonitor()
        print(f"Found Cline extension at: {monitor.extension_path}")
        
        # Register handlers
        monitor.on('tool_request', on_tool_request)
        monitor.on('tool_response', on_tool_response)
        monitor.on('error', on_error)
        
        print("\nStarting extension monitor...")
        print("Writing test entries to log...\n")
        
        # Start monitoring
        monitor_task = asyncio.create_task(monitor.start())
        
        # Write test entries
        for entry in test_entries:
            with open(log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            await asyncio.sleep(1)
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Stop monitoring
        monitor_task.cancel()
        
    except RuntimeError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Clean up test log
        if os.path.exists(log_file):
            os.remove(log_file)

async def main():
    """Run extension monitor tests"""
    setup_logging()
    
    # Run simulation test first
    await test_log_simulation()
    
    print("\n" + "="*80 + "\n")
    
    # Then try live monitoring
    await test_extension_monitoring()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTests stopped by user")
