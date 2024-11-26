import os
import asyncio
import logging
import subprocess
from cline_integration import ClineMonitor, ToolUse

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def find_mock_cline():
    """Find or create mock Cline executable"""
    mock_path = os.path.join(os.path.dirname(__file__), 'mock_cline.py')
    if os.path.exists(mock_path):
        # Make executable
        os.chmod(mock_path, 0o755)
        print(f"Using mock Cline at: {mock_path}")
        return mock_path
    else:
        print(f"Error: Mock Cline not found at {mock_path}")
        return None

async def test_live_monitoring():
    """Test live monitoring of Cline"""
    print("\nTesting Live Cline Monitoring...\n")
    
    # Try to find mock Cline
    print("Setting up mock Cline...")
    cline_path = find_mock_cline()
    
    if not cline_path:
        print("\nError: Could not find mock Cline")
        return
    
    # Create monitor with mock path
    monitor = ClineMonitor(check_path=False, custom_path=cline_path)
    print(f"\nUsing Cline at: {monitor.cline_path}")
    
    def on_tool_use(tool: ToolUse):
        """Handle tool use events"""
        print(f"\nTool detected: {tool.tool}")
        print(f"Parameters: {tool.params}")
        print(f"Auto-approved: {tool.approved}")
        
        if tool.approved:
            print("Tool is safe - auto-approving")
        else:
            print("Tool requires manual review")
    
    print("\nStarting Cline monitor...")
    print("Mock Cline will simulate tool use requests")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        await monitor.start_monitoring(callback=on_tool_use)
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    except Exception as e:
        print(f"\nError: {e}")

async def main():
    """Run live monitoring test"""
    setup_logging()
    await test_live_monitoring()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest stopped by user")
