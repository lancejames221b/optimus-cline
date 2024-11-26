import os
import json
import asyncio
import logging
from tool_executor import ToolExecutor, ToolRequest, ToolResult

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_command_execution():
    """Test execute_command tool"""
    print("\n=== Test 1: Command Execution ===")
    
    executor = ToolExecutor()
    
    # Test safe command
    request = ToolRequest(
        tool='execute_command',
        params={'command': 'echo "Hello World"'},
        timestamp='now'
    )
    
    result = await executor.execute(request)
    print("\nSafe command test:")
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    print(f"Error: {result.error}")
    print(f"Duration: {result.duration}s")
    
    # Test invalid command
    request = ToolRequest(
        tool='execute_command',
        params={'command': 'invalid_command'},
        timestamp='now'
    )
    
    result = await executor.execute(request)
    print("\nInvalid command test:")
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    print(f"Error: {result.error}")
    print(f"Duration: {result.duration}s")

async def test_file_operations():
    """Test file operation tools"""
    print("\n=== Test 2: File Operations ===")
    
    executor = ToolExecutor()
    test_dir = 'test_files'
    test_file = os.path.join(test_dir, 'test.txt')
    
    try:
        # Create test directory
        os.makedirs(test_dir, exist_ok=True)
        
        # Test write
        write_request = ToolRequest(
            tool='write_to_file',
            params={
                'path': test_file,
                'content': 'Hello from test!'
            },
            timestamp='now'
        )
        
        result = await executor.execute(write_request)
        print("\nWrite file test:")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}")
        print(f"Error: {result.error}")
        print(f"Duration: {result.duration}s")
        
        # Test read
        read_request = ToolRequest(
            tool='read_file',
            params={'path': test_file},
            timestamp='now'
        )
        
        result = await executor.execute(read_request)
        print("\nRead file test:")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}")
        print(f"Error: {result.error}")
        print(f"Duration: {result.duration}s")
        
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(test_dir):
            os.rmdir(test_dir)

async def test_file_listing():
    """Test list_files tool"""
    print("\n=== Test 3: File Listing ===")
    
    executor = ToolExecutor()
    
    # Test non-recursive
    request = ToolRequest(
        tool='list_files',
        params={
            'path': '.',
            'recursive': False
        },
        timestamp='now'
    )
    
    result = await executor.execute(request)
    print("\nNon-recursive list test:")
    print(f"Success: {result.success}")
    if result.success:
        files = json.loads(result.output)
        print(f"Found {len(files)} files")
        for file in files[:5]:  # Show first 5
            print(f"- {file}")
    print(f"Error: {result.error}")
    print(f"Duration: {result.duration}s")
    
    # Test recursive
    request = ToolRequest(
        tool='list_files',
        params={
            'path': '.',
            'recursive': True
        },
        timestamp='now'
    )
    
    result = await executor.execute(request)
    print("\nRecursive list test:")
    print(f"Success: {result.success}")
    if result.success:
        files = json.loads(result.output)
        print(f"Found {len(files)} files")
        for file in files[:5]:  # Show first 5
            print(f"- {file}")
    print(f"Error: {result.error}")
    print(f"Duration: {result.duration}s")

async def test_browser_actions():
    """Test browser_action tool"""
    print("\n=== Test 4: Browser Actions ===")
    
    executor = ToolExecutor()
    
    try:
        # Test launch
        request = ToolRequest(
            tool='browser_action',
            params={
                'action': 'launch',
                'url': 'https://example.com'
            },
            timestamp='now'
        )
        
        result = await executor.execute(request)
        print("\nLaunch test:")
        print(f"Success: {result.success}")
        if result.success:
            output = json.loads(result.output)
            print(f"Screenshot: {output['screenshot']}")
            print(f"Logs: {output['logs']}")
        print(f"Error: {result.error}")
        print(f"Duration: {result.duration}s")
        
        # Test click
        request = ToolRequest(
            tool='browser_action',
            params={
                'action': 'click',
                'coordinate': '450,300'
            },
            timestamp='now'
        )
        
        result = await executor.execute(request)
        print("\nClick test:")
        print(f"Success: {result.success}")
        if result.success:
            output = json.loads(result.output)
            print(f"Screenshot: {output['screenshot']}")
            print(f"Logs: {output['logs']}")
        print(f"Error: {result.error}")
        print(f"Duration: {result.duration}s")
        
        # Test scroll
        request = ToolRequest(
            tool='browser_action',
            params={
                'action': 'scroll_down',
            },
            timestamp='now'
        )
        
        result = await executor.execute(request)
        print("\nScroll test:")
        print(f"Success: {result.success}")
        if result.success:
            output = json.loads(result.output)
            print(f"Screenshot: {output['screenshot']}")
            print(f"Logs: {output['logs']}")
        print(f"Error: {result.error}")
        print(f"Duration: {result.duration}s")
        
        # Test close
        request = ToolRequest(
            tool='browser_action',
            params={
                'action': 'close',
            },
            timestamp='now'
        )
        
        result = await executor.execute(request)
        print("\nClose test:")
        print(f"Success: {result.success}")
        print(f"Error: {result.error}")
        print(f"Duration: {result.duration}s")
        
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run tool executor tests"""
    setup_logging()
    
    print("\nTesting Tool Executor...\n")
    
    await test_command_execution()
    await test_file_operations()
    await test_file_listing()
    await test_browser_actions()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTests stopped by user")
