#!/usr/bin/env python3
"""
Optimus Cline Quick Start Example
--------------------------------

This script demonstrates basic usage of the Optimus Cline assistant.
"""

import os
import asyncio
from tool_executor import ToolExecutor, ToolRequest
from browser_control import BrowserControl
from error_recovery import ErrorRecovery
from performance_optimization import PerformanceOptimizer

async def main():
    """Run quick start examples"""
    print("Optimus Cline Quick Start\n")
    
    # Initialize components
    executor = ToolExecutor()
    recovery = ErrorRecovery()
    optimizer = PerformanceOptimizer()
    
    try:
        # 1. Execute a command
        print("\n1. Execute Command Example:")
        result = await executor.execute(ToolRequest(
            tool='execute_command',
            params={'command': 'echo "Hello from Optimus Cline!"'},
            timestamp='now'
        ))
        if result.success:
            print(f"Command output: {result.output}")
        else:
            print(f"Command failed: {result.error}")
        
        # 2. Write a file
        print("\n2. File Operation Example:")
        result = await executor.execute(ToolRequest(
            tool='write_to_file',
            params={
                'path': 'example.txt',
                'content': 'This is a test file created by Optimus Cline.'
            },
            timestamp='now'
        ))
        if result.success:
            print("File created successfully")
            
            # Read the file back
            result = await executor.execute(ToolRequest(
                tool='read_file',
                params={'path': 'example.txt'},
                timestamp='now'
            ))
            if result.success:
                print(f"File contents: {result.output}")
        else:
            print(f"File operation failed: {result.error}")
        
        # 3. List files
        print("\n3. File Listing Example:")
        result = await executor.execute(ToolRequest(
            tool='list_files',
            params={
                'path': '.',
                'recursive': False
            },
            timestamp='now'
        ))
        if result.success:
            print("Files in current directory:")
            for file in result.output:
                print(f"- {file}")
        else:
            print(f"File listing failed: {result.error}")
        
        # 4. Search files
        print("\n4. File Search Example:")
        result = await executor.execute(ToolRequest(
            tool='search_files',
            params={
                'path': '.',
                'regex': r'def\s+\w+',
                'file_pattern': '*.py'
            },
            timestamp='now'
        ))
        if result.success:
            print(f"Found {len(result.output)} function definitions")
            for match in result.output[:3]:  # Show first 3 matches
                print(f"- {match}")
        else:
            print(f"File search failed: {result.error}")
        
        # 5. Batch operations
        print("\n5. Performance Optimization Example:")
        start_time = asyncio.get_event_loop().time()
        
        for i in range(10):
            await optimizer.batch_operation('file_write', {
                'path': f'batch_test_{i}.txt',
                'content': f'Test content {i}'
            })
        
        duration = asyncio.get_event_loop().time() - start_time
        print(f"Batch operations completed in {duration:.2f}s")
        
        # List batch files
        files = [f for f in os.listdir('.') if f.startswith('batch_test_')]
        print(f"Created {len(files)} batch files")
        
        # Clean up batch files
        for file in files:
            os.remove(file)
        print("Cleaned up batch files")
        
    except Exception as e:
        print(f"\nError: {e}")
        
        # Demonstrate error recovery
        print("\nAttempting recovery...")
        result = await recovery.recover(
            'tool_error',
            str(e),
            {'tool': 'execute_command'}
        )
        print(f"Recovery {'succeeded' if result.success else 'failed'}")
        
    finally:
        # Clean up
        if os.path.exists('example.txt'):
            os.remove('example.txt')
        print("\nQuick start completed!")

if __name__ == '__main__':
    # Run examples
    asyncio.run(main())
