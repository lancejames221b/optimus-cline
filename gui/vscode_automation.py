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
        
        # Create main layout
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True)
        
        # Left side - Actions
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Common actions
        actions_frame = ttk.LabelFrame(left_frame, text="Common Actions")
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
        custom_frame = ttk.LabelFrame(left_frame, text="Custom Command")
        custom_frame.pack(fill='x', padx=5, pady=5)
        
        self.vscode_cmd_entry = ttk.Entry(custom_frame)
        self.vscode_cmd_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        ttk.Button(
            custom_frame,
            text="Execute",
            command=self.execute_custom_vscode
        ).pack(side='right', padx=5, pady=5)
        
        # Automation setup
        setup_frame = ttk.LabelFrame(left_frame, text="Automation Setup")
        setup_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            setup_frame,
            text="Capture Approval Button",
            command=self.capture_button_location
        ).pack(side='left', padx=5, pady=5)
        
        self.location_label = ttk.Label(setup_frame, text="Button location: Not set")
        self.location_label.pack(side='left', padx=5, pady=5)
        
        # Right side - History
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Command history
        history_frame = ttk.LabelFrame(right_frame, text="Command History")
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
    
    def capture_button_location(self):
        """Capture VS Code approval button location"""
        try:
            # Prompt user to position mouse
            if messagebox.askyesno(
                "Capture Approval Button",
                "Position your mouse over the VS Code approval button (Run Command, Save, etc.) and click OK.\n" +
                "This location will be saved for future automation.\nProceed?"
            ):
                # Wait for user to position mouse
                time.sleep(1)
                
                # Get mouse position
                self.button_location = pyautogui.position()
                
                # Save location
                self.save_button_location()
                
                # Update label
                self.location_label.config(text=f"Button location: {self.button_location.x}, {self.button_location.y}")
                
                messagebox.showinfo(
                    "Success",
                    "Approval button location captured.\nThe GUI will now click this location automatically."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture button location: {e}")
    
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
                    if 'button_location' in config:
                        x, y = config['button_location']
                        self.button_location = pyautogui.Point(x, y)
                        self.location_label.config(text=f"Button location: {x}, {y}")
            except:
                self.button_location = None
                self.location_label.config(text="Button location: Not set")
    
    def save_button_location(self):
        """Save button location for current project"""
        if not self.current_project or not self.button_location:
            return
            
        config_dir = os.path.join(self.current_project['path'], '.cline')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'vscode_config.json')
        config = {'button_location': [self.button_location.x, self.button_location.y]}
        
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
                # First time - ask user to capture button location
                if messagebox.askyesno(
                    "VS Code Automation",
                    "Approval button location not set.\nWould you like to capture it now?"
                ):
                    self.capture_button_location()
                return False
            
            # Click saved location
            pyautogui.click(self.button_location.x, self.button_location.y)
            logging.info(f"Clicked approval button at {self.button_location.x}, {self.button_location.y}")
            return True
                
        except Exception as e:
            logging.error(f"Error automating VS Code approval: {e}")
            return False
