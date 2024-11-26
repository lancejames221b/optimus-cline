import os
import logging
from vscode_integration import VSCodeIntegration, ToolRequest

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_extension_detection():
    """Test finding Cline extension"""
    print("\n=== Test 1: Extension Detection ===")
    
    integration = VSCodeIntegration()
    extension_path = integration.find_cline_extension()
    
    if extension_path:
        print(f"Found Cline extension at: {extension_path}")
        
        # Check extension files
        package_json = os.path.join(extension_path, 'package.json')
        if os.path.exists(package_json):
            print("Found package.json")
        
        dist_dir = os.path.join(extension_path, 'dist')
        if os.path.exists(dist_dir):
            print("Found dist directory")
    else:
        print("Cline extension not found")

def test_tool_handling():
    """Test tool request handling"""
    print("\n=== Test 2: Tool Request Handling ===")
    
    integration = VSCodeIntegration()
    
    # Test safe command
    safe_command = {
        'tool': 'execute_command',
        'params': {'command': 'ls -la'}
    }
    
    result = integration.handle_tool_request(**safe_command)
    print("\nSafe command test:")
    print(f"Tool: {result.tool}")
    print(f"Params: {result.params}")
    print(f"Approved: {result.approved}")
    
    # Test unsafe command
    unsafe_command = {
        'tool': 'execute_command',
        'params': {'command': 'rm -rf /'}
    }
    
    result = integration.handle_tool_request(**unsafe_command)
    print("\nUnsafe command test:")
    print(f"Tool: {result.tool}")
    print(f"Params: {result.params}")
    print(f"Approved: {result.approved}")
    
    # Test safe file operation
    safe_file = {
        'tool': 'write_to_file',
        'params': {'path': 'test.txt', 'content': 'Hello'}
    }
    
    result = integration.handle_tool_request(**safe_file)
    print("\nSafe file operation test:")
    print(f"Tool: {result.tool}")
    print(f"Params: {result.params}")
    print(f"Approved: {result.approved}")
    
    # Test unsafe file operation
    unsafe_file = {
        'tool': 'write_to_file',
        'params': {'path': '../test.txt', 'content': 'Hello'}
    }
    
    result = integration.handle_tool_request(**unsafe_file)
    print("\nUnsafe file operation test:")
    print(f"Tool: {result.tool}")
    print(f"Params: {result.params}")
    print(f"Approved: {result.approved}")

def test_history():
    """Test history management"""
    print("\n=== Test 3: History Management ===")
    
    integration = VSCodeIntegration()
    
    # Clear history
    integration.clear_history()
    print("Cleared history")
    
    # Add some test entries
    test_tools = [
        ('execute_command', {'command': 'ls'}),
        ('write_to_file', {'path': 'test.txt', 'content': 'Hello'}),
        ('read_file', {'path': 'config.json'})
    ]
    
    for tool, params in test_tools:
        integration.handle_tool_request(tool, params)
    
    print(f"\nAdded {len(test_tools)} test entries")
    
    # Get recent history
    recent = integration.get_history(limit=2)
    print(f"\nRecent history ({len(recent)} entries):")
    for entry in recent:
        print(f"- {entry.tool}: {entry.params}")

def main():
    """Run VSCode integration tests"""
    setup_logging()
    
    print("\nTesting VSCode Integration...\n")
    
    test_extension_detection()
    test_tool_handling()
    test_history()

if __name__ == '__main__':
    main()
