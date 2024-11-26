#!/usr/bin/env python3
"""
PyAutoGUI Test Script

This script helps verify PyAutoGUI installation and setup.
It performs basic tests and provides visual feedback.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import pyautogui
import sys
import os
from datetime import datetime

class TestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyAutoGUI Test")
        self.root.geometry("600x400")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(expand=True, fill='both')
        
        # System info
        info_frame = ttk.LabelFrame(main_frame, text="System Information")
        info_frame.pack(fill='x', pady=5)
        
        screen_size = pyautogui.size()
        ttk.Label(info_frame, text=f"Screen Size: {screen_size[0]}x{screen_size[1]}").pack(anchor='w', padx=5)
        ttk.Label(info_frame, text=f"OS: {sys.platform}").pack(anchor='w', padx=5)
        ttk.Label(info_frame, text=f"Python: {sys.version.split()[0]}").pack(anchor='w', padx=5)
        ttk.Label(info_frame, text=f"PyAutoGUI: {pyautogui.__version__}").pack(anchor='w', padx=5)
        
        # Test buttons
        test_frame = ttk.LabelFrame(main_frame, text="Tests")
        test_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            test_frame,
            text="Test Screenshot",
            command=self.test_screenshot
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            test_frame,
            text="Test Mouse Move",
            command=self.test_mouse
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            test_frame,
            text="Test Click",
            command=self.test_click
        ).pack(side='left', padx=5, pady=5)
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Output")
        output_frame.pack(fill='both', expand=True, pady=5)
        
        self.output = scrolledtext.ScrolledText(output_frame)
        self.output.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Log initial state
        self.log("PyAutoGUI Test Started")
        self.log(f"FAILSAFE: {pyautogui.FAILSAFE}")
        self.log(f"PAUSE: {pyautogui.PAUSE} seconds")
    
    def log(self, message):
        """Add message to output with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output.insert('end', f"[{timestamp}] {message}\n")
        self.output.see('end')
    
    def test_screenshot(self):
        """Test screenshot capability"""
        try:
            self.log("Taking screenshot...")
            screenshot = pyautogui.screenshot()
            
            # Save to .cline directory
            os.makedirs('.cline', exist_ok=True)
            filename = os.path.join('.cline', 'test_screenshot.png')
            screenshot.save(filename)
            
            self.log(f"Screenshot saved to {filename}")
            self.log("Screenshot test: PASSED")
            
        except Exception as e:
            self.log(f"Screenshot test FAILED: {e}")
            self.log("Check screen recording permissions")
    
    def test_mouse(self):
        """Test mouse movement"""
        try:
            self.log("Moving mouse in square pattern...")
            
            # Get current position
            start_x, start_y = pyautogui.position()
            
            # Move in square
            moves = [
                (start_x + 100, start_y),
                (start_x + 100, start_y + 100),
                (start_x, start_y + 100),
                (start_x, start_y)
            ]
            
            for x, y in moves:
                pyautogui.moveTo(x, y, duration=0.5)
            
            self.log("Mouse movement test: PASSED")
            
        except Exception as e:
            self.log(f"Mouse movement test FAILED: {e}")
    
    def test_click(self):
        """Test mouse click"""
        try:
            self.log("Testing click...")
            
            # Create test window
            test_win = tk.Toplevel(self.root)
            test_win.title("Click Test")
            test_win.geometry("200x100")
            
            # Add button to test window
            clicks = []
            
            def on_click():
                clicks.append(1)
                if len(clicks) >= 3:
                    test_win.destroy()
                    self.log("Click test: PASSED")
            
            test_button = ttk.Button(test_win, text="Click Me!", command=on_click)
            test_button.pack(expand=True)
            
            # Get button position
            self.root.update()
            test_win.update()
            
            # Wait for window to appear
            self.root.after(500, lambda: self.perform_test_clicks(test_button))
            
        except Exception as e:
            self.log(f"Click test FAILED: {e}")
    
    def perform_test_clicks(self, button):
        """Perform test clicks on button"""
        try:
            # Get button position
            x = button.winfo_rootx() + button.winfo_width() // 2
            y = button.winfo_rooty() + button.winfo_height() // 2
            
            # Perform clicks
            for _ in range(3):
                pyautogui.click(x, y)
                pyautogui.sleep(0.5)
            
        except Exception as e:
            self.log(f"Click test FAILED: {e}")

def main():
    # Configure PyAutoGUI
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 1.0
    
    # Create GUI
    root = tk.Tk()
    app = TestGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
