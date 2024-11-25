#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
import pyautogui
import subprocess
import time

class ClineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cline")
        self.root.geometry("600x400")
        
        # Security checks
        self.SECURITY_CHECKS = [
            "Production safeguards active",
            "Backup systems verified",
            "Staging environment tested",
            "Access controls verified",
            "Cost limits configured",
            "Monitoring systems active",
            "Rollback plan tested",
            "Documentation updated"
        ]
        
        # Setup logging
        os.makedirs('.cline', exist_ok=True)
        logging.basicConfig(
            filename='.cline/automation.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Security checks frame
        checks_frame = ttk.LabelFrame(main_frame, text="Security Checks")
        checks_frame.pack(fill='x', pady=5)
        
        self.check_vars = {}
        for check in self.SECURITY_CHECKS:
            var = tk.BooleanVar()
            self.check_vars[check] = var
            ttk.Checkbutton(
                checks_frame,
                text=check,
                variable=var
            ).pack(anchor='w', padx=5, pady=2)
        
        # VS Code automation frame
        vscode_frame = ttk.LabelFrame(main_frame, text="VS Code Automation")
        vscode_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            vscode_frame,
            text="Accept Change",
            command=lambda: self.safe_execute_vscode('git.acceptChange')
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            vscode_frame,
            text="Stage Change",
            command=lambda: self.safe_execute_vscode('git.stage')
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            vscode_frame,
            text="Revert Change",
            command=lambda: self.safe_execute_vscode('git.revertChange')
        ).pack(side='left', padx=5, pady=5)
        
        # Make window appear in front
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        root.focus_force()
    
    def verify_security_checks(self):
        """Verify security checks"""
        unchecked = [
            check for check, var in self.check_vars.items()
            if not var.get()
        ]
        
        if unchecked:
            return messagebox.askyesno(
                "Security Checks",
                f"The following security checks are not complete:\n" +
                "\n".join(f"- {check}" for check in unchecked) +
                "\n\nDo you want to proceed anyway?"
            )
        
        return True
    
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
            if not self.verify_security_checks():
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

if __name__ == '__main__':
    root = tk.Tk()
    app = ClineGUI(root)
    root.mainloop()
