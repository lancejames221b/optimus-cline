import asyncio
import logging
from cline_integration import ClineMonitor, ToolUse

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_tool_parsing():
    print("=== Test 1: Tool Use Parsing ===")
    
    # Create monitor without path check
    monitor = ClineMonitor(check_path=False)
    
    test_cmd = '<execute_command><command>ls -la</command></execute_command>'
    tool_use = monitor._parse_tool_use(test_cmd)
    if tool_use:
        print(f"Parsed tool: {tool_use.tool}")
        print(f"Parameters: {tool_use.params}")
        print(f"Safe: {monitor._analyze_safety(tool_use)}\n")

def test_safety_analysis():
    print("=== Test 2: Safety Analysis ===")
    
    # Create monitor without path check
    monitor = ClineMonitor(check_path=False)
    
    test_cases = [
        ToolUse(tool="execute_command", params={"command": "ls -la"}, timestamp="now"),
        ToolUse(tool="execute_command", params={"command": "rm -rf /"}, timestamp="now"),
        ToolUse(tool="write_to_file", params={"path": "test.txt", "content": "Hello"}, timestamp="now"),
        ToolUse(tool="write_to_file", params={"path": "../test.txt", "content": "Hello"}, timestamp="now")
    ]
    
    for case in test_cases:
        safe = monitor._analyze_safety(case)
        print(f"Tool: {case.tool}")
        print(f"Params: {case.params}")
        print(f"Safe: {safe}\n")

def test_history_management():
    print("=== Test 3: History Management ===")
    
    # Create monitor without path check
    monitor = ClineMonitor(check_path=False)
    
    test_case = ToolUse(tool="test", params={"param": "value"}, timestamp="now")
    monitor.history.append(test_case)
    monitor._save_history()
    print("Saved history")
    
    monitor.clear_history()
    print("Cleared history")
    
    monitor._load_history()
    print(f"Loaded {len(monitor.history)} entries")

async def main():
    setup_logging()
    
    print("\nTesting Cline Integration...\n")
    
    # Run offline tests
    test_tool_parsing()
    test_safety_analysis()
    test_history_management()
    
    print("\nNote: Live monitoring test skipped - Cline executable not found")

if __name__ == '__main__':
    asyncio.run(main())
