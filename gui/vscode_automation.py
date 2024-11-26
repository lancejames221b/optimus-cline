import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import logging
import pyautogui
import time
import os
import json
from datetime import datetime

class VSCodeAutomation(ttk.LabelFrame):
    def __init__(self, parent, security_checks):
        super().__init__(parent, text="VS Code Automation")
        self.security_checks = security_checks
        
        # State
        self.current_project = None
        self.button_location = None
        
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
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
        self.load_button_location()
    
    def load_button_location(self):
        """Load saved button location for current project"""
        if not self.current_project:
            return
            
        config_path = os.path.join(self.current_project['path'], '.cline', 'vscode_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    self.button_location = config.get('button_location')
            except:
                self.button_location = None
    
    def save_button_location(self):
        """Save button location for current project"""
        if not self.current_project or not self.button_location:
            return
            
        config_dir = os.path.join(self.current_project['path'], '.cline')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'vscode_config.json')
        config = {'button_location': self.button_location}
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
    
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
            
            # Try to automate approval if needed
            if status == 'Success':
                time.sleep(0.5)  # Wait for VS Code to show button
                self.automate_vscode_approval()
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"VS Code command failed: {command} - {error_msg}")
            messagebox.showerror("Error", f"Failed to execute command: {error_msg}")
    
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
            
            if not self.button_location:
                # First time - ask user to click button
                if messagebox.askyesno(
                    "VS Code Button",
                    "Click OK, then click the VS Code button within 3 seconds.\n" +
                    "This location will be saved for future automation."
                ):
                    time.sleep(3)
                    # Capture click location
                    self.button_location = pyautogui.position()
                    self.save_button_location()
                    logging.info(f"Saved button location: {self.button_location}")
                    return True
            else:
                # Use saved location
                x, y = self.button_location
                pyautogui.click(x, y)
                logging.info(f"Clicked saved location: {x}, {y}")
                return True
            
            return False
                
        except Exception as e:
            logging.error(f"Error automating VS Code approval: {e}")
            return False
