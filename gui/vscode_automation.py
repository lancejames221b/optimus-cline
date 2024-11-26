import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import logging
import pyautogui
import time
import os
from datetime import datetime

class VSCodeAutomation(ttk.LabelFrame):
    def __init__(self, parent, security_checks):
        super().__init__(parent, text="VS Code Automation")
        self.security_checks = security_checks
        
        # State
        self.current_project = None
        
        # VS Code commands
        self.VSCODE_COMMANDS = {
            'accept_change': 'git.acceptChange',
            'stage_change': 'git.stage',
            'revert_change': 'git.revertChange'
        }
        
        # Common actions
        actions_frame = ttk.LabelFrame(self, text="Common Actions")
        actions_frame.pack(fill='x', padx=5, pady=5)
        
        # Create buttons for common actions
        for name, command in self.VSCODE_COMMANDS.items():
            btn_text = name.replace('_', ' ').title()
            ttk.Button(
                actions_frame,
                text=btn_text,
                command=lambda cmd=command: self.safe_execute_vscode(cmd)
            ).pack(side='left', padx=5, pady=5)
        
        # Custom command
        custom_frame = ttk.LabelFrame(self, text="Custom Command")
        custom_frame.pack(fill='x', padx=5, pady=5)
        
        self.vscode_cmd_entry = ttk.Entry(custom_frame)
        self.vscode_cmd_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        ttk.Button(
            custom_frame,
            text="Execute",
            command=self.execute_custom_vscode
        ).pack(side='right', padx=5, pady=5)
        
        # Command history
        history_frame = ttk.LabelFrame(self, text="Command History")
        history_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.vscode_history = ttk.Treeview(
            history_frame,
            columns=('Time', 'Command', 'Status'),
            show='headings'
        )
        self.vscode_history.heading('Time', text='Time')
        self.vscode_history.heading('Command', text='Command')
        self.vscode_history.heading('Status', text='Status')
        self.vscode_history.pack(fill='both', expand=True, pady=5)
        
        # Output area
        output_frame = ttk.LabelFrame(self, text="Output")
        output_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.vscode_output = scrolledtext.ScrolledText(output_frame, height=6)
        self.vscode_output.pack(fill='both', expand=True, padx=5, pady=5)
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
    
    def safe_execute_vscode(self, command):
        """Execute VS Code command with safety checks"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
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
                text=True,
                cwd=self.current_project['path']  # Execute in project directory
            )
            
            # Log result
            status = 'Success' if result.returncode == 0 else 'Failed'
            logging.info(f"VS Code command completed: {command} ({status})")
            
            # Add to history
            self.vscode_history.insert(
                '',
                0,
                values=(
                    datetime.now().strftime('%H:%M:%S'),
                    command,
                    status
                )
            )
            
            # Show output
            self.vscode_output.insert('end', f"\nCommand: {command}\n")
            if result.stdout:
                self.vscode_output.insert('end', result.stdout)
            if result.stderr:
                self.vscode_output.insert('end', f"Error: {result.stderr}\n")
            self.vscode_output.see('end')
            
            # Try to automate approval if needed
            if status == 'Success':
                time.sleep(0.5)  # Wait for VS Code to show approval button
                self.automate_vscode_approval()
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"VS Code command failed: {command} - {error_msg}")
            messagebox.showerror("Error", f"Failed to execute command: {error_msg}")
            self.vscode_output.insert('end', f"Error: {error_msg}\n")
            self.vscode_output.see('end')
    
    def execute_custom_vscode(self):
        """Execute custom VS Code command"""
        command = self.vscode_cmd_entry.get().strip()
        if not command:
            return
        
        self.vscode_cmd_entry.delete(0, tk.END)
        self.safe_execute_vscode(command)
    
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
