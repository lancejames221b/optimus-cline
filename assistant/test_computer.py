import asyncio
import logging
from computer import ComputerController, ScreenAnalyzer

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_computer_control():
    """Test computer control functionality"""
    controller = ComputerController()
    screen = ScreenAnalyzer()
    
    print("\nTesting Computer Control...\n")
    
    # Test 1: Basic Screen Analysis
    print("=== Test 1: Screen Analysis ===")
    try:
        elements = screen.find_ui_elements()
        print(f"Found {len(elements)} UI elements")
        for elem in elements[:5]:  # Show first 5 elements
            print(f"- {elem.type}: {elem.text or elem.accessibility_description}")
    except Exception as e:
        print(f"Screen analysis failed: {e}")
    
    # Test 2: Chrome Automation
    print("\n=== Test 2: Chrome Automation ===")
    try:
        # Activate Chrome
        controller.activate_app("Google Chrome")
        print("Activated Chrome")
        await asyncio.sleep(1)  # Wait for activation
        
        # Create new tab with URL
        controller.chrome_command('open location "https://www.python.org"')
        print("Navigated to Python.org")
        
        # Wait for page load
        await asyncio.sleep(2)
        
        # Try to find and click "Downloads"
        if controller.click_text("Downloads", partial=True):
            print("Clicked Downloads link")
        else:
            print("Downloads link not found")
    except Exception as e:
        print(f"Chrome automation failed: {e}")
    
    # Test 3: VSCode Automation
    print("\n=== Test 3: VSCode Automation ===")
    try:
        # Activate VSCode
        controller.activate_app("Visual Studio Code")
        print("Activated VSCode")
        await asyncio.sleep(1)  # Wait for activation
        
        # Create new file
        controller.hotkey('cmd', 'n')
        print("Created new file")
        await asyncio.sleep(1)  # Wait for window
        
        # Move mouse to center before typing
        screen_size = controller.get_screen_size()
        controller.move_to(screen_size[0]//2, screen_size[1]//2)
        await asyncio.sleep(0.5)
        
        # Type some Python code
        code = '''print("Hello from Mac Assistant!")'''
        controller.type_text(code)
        print("Typed code")
        
        # Save file
        controller.hotkey('cmd', 's')
        print("Triggered save dialog")
    except Exception as e:
        print(f"VSCode automation failed: {e}")
    
    # Test 4: System Operations
    print("\n=== Test 4: System Operations ===")
    try:
        # Take screenshot
        screenshot = screen.capture_screen()
        screenshot.save('test_screenshot.png')
        print("Saved screenshot")
        
        # Get running applications
        apps = controller.get_running_apps()
        print("Running applications:", apps)
    except Exception as e:
        print(f"System operations failed: {e}")

def main():
    """Run computer control tests"""
    setup_logging()
    asyncio.run(test_computer_control())

if __name__ == '__main__':
    main()
