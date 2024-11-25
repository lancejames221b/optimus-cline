import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import logging
import pyautogui
import time

class VSCodeAutomation(ttk.LabelFrame):
    def __init__(self, parent, security_checks):
        super().__init__(parent, text="VS Code Automation")
        self.security_checks = security_checks
        
        # VS Code commands
        self.VSCODE_COMMANDS = {
            'accept_change': 'git.acceptChange',
            'stage_change': 'git.stage',
            'revert_change': 'git.revertChange'
        }
        
        # Create buttons for common actions
        for name, command in self.VSCODE_COMMANDS.items():
            btn_text = name.replace('_', ' ').title()
            ttk.Button(
                self,
                text=btn_text,
                command=lambda cmd=command: self.safe_execute_vscode(cmd)
            ).pack(side='left', padx=5, pady=5)
    
    def safe_execute_vscode(self, command):
        """Execute VS Code command with safety checks"""
        # Log attempt
        logging.info(f"Attempting VS Code command: {command}")
        
        # Check if command needs confirmation
        if command == 'git.revertChange':
            if not messagebox.askyesno(
                "Confirm Action",
                "Are you sure you want to revert this change?"
            ):
                logging.info(f"VS Code command cancelled: {command}")
                return
        
        try:
            # Execute command
            result = subprocess.run(
                ['code', '--command', command],
                capture_output=True,
                text=True
            )
            
            # Log result
            status = 'Success' if result.returncode == 0 else 'Failed'
            logging.info(f"VS Code command completed: {command} ({status})")
            
            # Try to automate approval if needed
            if status == 'Success':
                time.sleep(0.5)  # Wait for VS Code to show approval button
                self.automate_vscode_approval()
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"VS Code command failed: {command} - {error_msg}")
            messagebox.showerror("Error", f"Failed to execute command: {error_msg}")
    
    def automate_vscode_approval(self):
        """Automate VS Code command approval"""
        try:
            # Verify security checks first
            if not self.security_checks.verify_checks():
                return False
            
            # Take screenshot of the screen
            screen = pyautogui.screenshot()
            
            # Look for red pixels that could be the button
            width, height = screen.size
            for x in range(0, width, 5):  # Step by 5 pixels for performance
                for y in range(0, height, 5):
                    pixel = screen.getpixel((x, y))
                    # Check if pixel is reddish (high red, low green/blue)
                    if pixel[0] > 200 and pixel[1] < 100 and pixel[2] < 100:
                        # Found potential red button, click it
                        pyautogui.click(x, y)
                        logging.info(f"Clicked red button at {x}, {y}")
                        return True
            
            logging.info("No red button found")
            return False
                
        except Exception as e:
            logging.error(f"Error automating VS Code approval: {e}")
            return False
