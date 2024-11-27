#!/usr/bin/env python3
"""
Test Computer Use Capabilities
--------------------------

Test UI automation with PyAutoGUI and safety measures.
"""

import os
import sys
import platform
import pyautogui
import psutil
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.5  # Reduce pause between actions

class ComputerUseTest:
    """Test computer use capabilities"""
    
    def __init__(self):
        self.test_dir = os.path.abspath("test_outputs")
        self.screenshots_dir = os.path.abspath(os.path.join("assistant", "screenshots"))
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),  # Log to console
                logging.FileHandler(os.path.join(self.test_dir, 'test.log'))  # Log to file
            ]
        )
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logging.info(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
        
        # Store platform-specific keys and window titles
        self.is_mac = sys.platform == 'darwin'
        self.modifier_key = 'command' if self.is_mac else 'ctrl'
        self.editor_title = 'TextEdit' if self.is_mac else 'Notepad'
        self.vscode_title = 'Visual Studio Code'
        
        # Maximum attempts for operations
        self.max_attempts = 3
        
        logging.info(f"Platform: {'macOS' if self.is_mac else 'Windows'}")
        logging.info(f"Editor: {self.editor_title}")
    
    def test_file_operations(self):
        """Test file creation and manipulation with safety checks"""
        print("\nTesting file operations...")
        logging.info("Starting file operations test")
        
        try:
            # Get current timestamp and system info
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_info = {
                "OS": platform.system(),
                "Version": platform.version(),
                "Machine": platform.machine(),
                "Python": platform.python_version()
            }
            
            # Create test file path in safe directory
            test_file = os.path.join(self.test_dir, "test_file.txt")
            logging.info(f"Writing to test file: {test_file}")
            
            # Write data to file
            data = {
                "system_info": system_info,
                "timestamp": timestamp
            }
            with open(test_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Read back and verify
            logging.info("Verifying file contents")
            with open(test_file, 'r') as f:
                read_data = json.load(f)
                assert read_data == data, "Data verification failed"
            
            print("File operations test passed")
            logging.info("File operations test completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error in file operations: {e}")
            return False
    
    def test_system_monitoring(self):
        """Test system monitoring capabilities"""
        print("\nTesting system monitoring...")
        logging.info("Starting system monitoring test")
        
        try:
            monitor_file = os.path.join(self.test_dir, 'system_monitor.txt')
            logging.info(f"Writing to monitor file: {monitor_file}")
            
            # Get CPU usage per core
            logging.info("Getting CPU usage")
            cpu_percents = psutil.cpu_percent(interval=1, percpu=True)
            if cpu_percents is None:
                cpu_percents = [0.0] * psutil.cpu_count()
            
            # Get memory details
            logging.info("Getting memory usage")
            memory = psutil.virtual_memory()
            memory_data = {
                "total": memory.total // (1024 * 1024),  # MB
                "available": memory.available // (1024 * 1024),  # MB
                "percent": memory.percent,
                "used": memory.used // (1024 * 1024)  # MB
            }
            
            # Get top processes
            logging.info("Getting process list")
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] is not None:
                        processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            top_processes = processes[:5]
            
            # Write report
            logging.info("Writing system monitor report")
            with open(monitor_file, 'w') as f:
                f.write(f"System Monitor Report - {datetime.now()}\n\n")
                
                f.write("CPU Usage Per Core:\n")
                for i, percent in enumerate(cpu_percents):
                    f.write(f"Core {i}: {percent}%\n")
                
                f.write("\nMemory Usage:\n")
                for key, value in memory_data.items():
                    if key == "percent":
                        f.write(f"{key}: {value}%\n")
                    else:
                        f.write(f"{key}: {value} MB\n")
                
                f.write("\nTop Processes by CPU Usage:\n")
                for proc in top_processes:
                    f.write(f"PID: {proc['pid']} Name: {proc['name']} CPU: {proc['cpu_percent']}%\n")
            
            print("System monitoring test passed")
            logging.info("System monitoring test completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error in system monitoring: {e}")
            return False
    
    def is_vscode_window(self, window_title: str) -> bool:
        """Check if a window title belongs to VSCode"""
        vscode_titles = [
            'Visual Studio Code',
            'Code',
            'VSCode',
            '.py - Visual Studio Code',
            '.js - Visual Studio Code',
            '.md - Visual Studio Code'
        ]
        return any(title.lower() in window_title.lower() for title in vscode_titles)
    
    def close_editor_safely(self):
        """Close text editor without affecting VSCode"""
        logging.info("Attempting to close editor safely")
        try:
            # Get all window titles
            windows = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if self.editor_title.lower() in proc.name().lower():
                        windows.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Close only text editor windows
            for window in windows:
                try:
                    if not self.is_vscode_window(window.name()):
                        logging.info(f"Closing window: {window.name()}")
                        window.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            time.sleep(0.5)  # Wait for windows to close
            
        except Exception as e:
            logging.warning(f"Error closing editor: {e}")
    
    def wait_for_editor(self, timeout: int = 10) -> bool:
        """Wait for text editor to appear in process list"""
        logging.info(f"Waiting for {self.editor_title} to open (timeout: {timeout}s)")
        start_time = time.time()
        while time.time() - start_time < timeout:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if self.editor_title.lower() in proc.name().lower():
                        logging.info(f"Found {self.editor_title} process")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            time.sleep(0.5)
        logging.warning(f"Timeout waiting for {self.editor_title}")
        return False
    
    def test_ui_automation(self):
        """Test UI automation with safety measures"""
        print("\nTesting UI automation...")
        logging.info("Starting UI automation test")
        
        try:
            # Take screenshot before starting
            screenshot_path = os.path.join(
                self.screenshots_dir,
                f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            pyautogui.screenshot(screenshot_path)
            logging.info(f"Saved initial screenshot to {screenshot_path}")
            
            # Create test file directly first
            test_file = os.path.join(self.test_dir, 'ui_test.txt')
            test_message = "This is a UI automation test message."
            
            with open(test_file, 'w') as f:
                f.write(test_message)
            logging.info(f"Created test file at {test_file}")
            
            # Open text editor
            editor_opened = False
            for attempt in range(self.max_attempts):
                try:
                    logging.info(f"Attempting to open {self.editor_title} (attempt {attempt + 1}/{self.max_attempts})")
                    if self.is_mac:
                        # Open TextEdit on macOS
                        logging.info("Opening Spotlight")
                        pyautogui.hotkey(self.modifier_key, 'space')
                        time.sleep(1)
                        
                        logging.info("Typing 'textedit'")
                        pyautogui.write('textedit')
                        time.sleep(1)
                        
                        logging.info("Pressing return")
                        pyautogui.press('return')
                        
                        # Wait for TextEdit to open
                        if self.wait_for_editor():
                            editor_opened = True
                            break
                    else:
                        # Open Notepad on Windows
                        logging.info("Opening Start menu")
                        pyautogui.press('win')
                        time.sleep(1)
                        
                        logging.info("Typing 'notepad'")
                        pyautogui.write('notepad')
                        time.sleep(1)
                        
                        logging.info("Pressing return")
                        pyautogui.press('return')
                        
                        # Wait for Notepad to open
                        if self.wait_for_editor():
                            editor_opened = True
                            break
                    
                except Exception as e:
                    logging.warning(f"Failed to open editor (attempt {attempt + 1}/{self.max_attempts}): {e}")
                    time.sleep(1)
            
            if not editor_opened:
                raise Exception("Failed to open text editor")
            
            # Wait for editor to be ready
            logging.info("Waiting for editor to be ready")
            time.sleep(2)
            
            # Type test message directly
            logging.info("Typing test message")
            pyautogui.write(test_message)
            time.sleep(1)
            
            # Add some text
            logging.info("Adding additional text")
            pyautogui.write("\nAdditional text added by UI automation test.")
            time.sleep(1)
            
            # Save file
            logging.info("Saving file")
            pyautogui.hotkey(self.modifier_key, 's')
            time.sleep(1)
            
            logging.info(f"Typing file path: {test_file}")
            pyautogui.write(str(Path(test_file).absolute()))
            time.sleep(1)
            
            logging.info("Pressing return to save")
            pyautogui.press('return')
            time.sleep(1)
            
            # Handle potential replace dialog
            if os.path.exists(test_file):
                logging.info("Handling replace dialog")
                pyautogui.press('return')
                time.sleep(1)
            
            # Close editor safely
            self.close_editor_safely()
            
            # Verify file was modified
            logging.info("Verifying file modifications")
            with open(test_file, 'r') as f:
                content = f.read()
                if "Additional text" not in content:
                    raise Exception("File was not modified correctly")
            
            # Take screenshot after completion
            screenshot_path = os.path.join(
                self.screenshots_dir,
                f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            pyautogui.screenshot(screenshot_path)
            logging.info(f"Saved final screenshot to {screenshot_path}")
            
            print("UI automation test passed")
            logging.info("UI automation test completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error in UI automation: {e}")
            # Take error screenshot
            try:
                screenshot_path = os.path.join(
                    self.screenshots_dir,
                    f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                pyautogui.screenshot(screenshot_path)
                logging.info(f"Saved error screenshot to {screenshot_path}")
            except:
                pass
            return False
        
        finally:
            # Always try to close editor safely
            self.close_editor_safely()

def main():
    """Run tests"""
    tester = ComputerUseTest()
    
    # Test file operations
    tester.test_file_operations()
    
    # Test system monitoring
    tester.test_system_monitoring()
    
    # Test UI automation
    tester.test_ui_automation()

if __name__ == '__main__':
    main()
