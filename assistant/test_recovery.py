import os
import json
import asyncio
import logging
from datetime import datetime
from error_recovery import ErrorRecovery, RecoveryAction, RecoveryResult

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_browser_recovery():
    """Test browser error recovery"""
    print("\n=== Test 1: Browser Recovery ===")
    
    recovery = ErrorRecovery()
    
    try:
        # Test timeout error
        result = await recovery.recover(
            'browser_error',
            'Navigation Timeout Exceeded',
            {
                'error': 'Navigation Timeout Exceeded: 30000ms exceeded',
                'url': 'https://example.com'
            }
        )
        
        print("\nTimeout error recovery:")
        print(f"Success: {result.success}")
        print(f"Action: {result.action}")
        print(f"Error: {result.error}")
        
        # Test navigation error
        result = await recovery.recover(
            'browser_error',
            'Navigation Failed',
            {
                'error': 'Navigation failed: net::ERR_CONNECTION_REFUSED',
                'url': 'https://example.com'
            }
        )
        
        print("\nNavigation error recovery:")
        print(f"Success: {result.success}")
        print(f"Action: {result.action}")
        print(f"Error: {result.error}")
        
    except Exception as e:
        print(f"Error: {e}")

async def test_tool_recovery():
    """Test tool error recovery"""
    print("\n=== Test 2: Tool Recovery ===")
    
    recovery = ErrorRecovery()
    
    try:
        # Test permission error
        result = await recovery.recover(
            'tool_error',
            'Permission Denied',
            {
                'error': 'Permission denied: /path/to/file',
                'tool': 'write_to_file',
                'path': '/path/to/file'
            }
        )
        
        print("\nPermission error recovery:")
        print(f"Success: {result.success}")
        print(f"Action: {result.action}")
        print(f"Error: {result.error}")
        
        # Test generic error
        result = await recovery.recover(
            'tool_error',
            'Tool Failed',
            {
                'error': 'Command failed with exit code 1',
                'tool': 'execute_command',
                'command': 'invalid_command'
            }
        )
        
        print("\nGeneric error recovery:")
        print(f"Success: {result.success}")
        print(f"Action: {result.action}")
        print(f"Error: {result.error}")
        
    except Exception as e:
        print(f"Error: {e}")

async def test_extension_recovery():
    """Test extension error recovery"""
    print("\n=== Test 3: Extension Recovery ===")
    
    recovery = ErrorRecovery()
    
    try:
        # Test extension error
        result = await recovery.recover(
            'extension_error',
            'Extension Failed',
            {
                'error': 'Extension process died',
                'pid': 12345
            }
        )
        
        print("\nExtension error recovery:")
        print(f"Success: {result.success}")
        print(f"Action: {result.action}")
        print(f"Error: {result.error}")
        
    except Exception as e:
        print(f"Error: {e}")

async def test_system_recovery():
    """Test system error recovery"""
    print("\n=== Test 4: System Recovery ===")
    
    recovery = ErrorRecovery()
    
    try:
        # Test system error
        result = await recovery.recover(
            'system_error',
            'System Error',
            {
                'error': 'System resources exhausted',
                'memory': '95%',
                'cpu': '100%'
            }
        )
        
        print("\nSystem error recovery:")
        print(f"Success: {result.success}")
        print(f"Action: {result.action}")
        print(f"Error: {result.error}")
        
    except Exception as e:
        print(f"Error: {e}")

async def test_retry_behavior():
    """Test retry behavior"""
    print("\n=== Test 5: Retry Behavior ===")
    
    recovery = ErrorRecovery()
    
    try:
        # Test with retries
        start = datetime.now()
        
        result = await recovery.recover(
            'browser_error',
            'Intermittent Error',
            {
                'error': 'Random failure',
                'attempt': 1
            }
        )
        
        duration = (datetime.now() - start).total_seconds()
        
        print("\nRetry behavior test:")
        print(f"Success: {result.success}")
        print(f"Action: {result.action}")
        print(f"Error: {result.error}")
        print(f"Duration: {duration}s")
        
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run error recovery tests"""
    setup_logging()
    
    print("\nTesting Error Recovery...\n")
    
    try:
        await test_browser_recovery()
        await test_tool_recovery()
        await test_extension_recovery()
        await test_system_recovery()
        await test_retry_behavior()
        
    except KeyboardInterrupt:
        print("\nTests stopped by user")
    except Exception as e:
        print(f"\nError running tests: {e}")

if __name__ == '__main__':
    asyncio.run(main())
