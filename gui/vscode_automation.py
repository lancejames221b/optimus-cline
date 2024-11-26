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
        self.button_locations = {
            'save': None,
            'run': None,
            'approve': None
        }
        self.automation_enabled = {
            'save': tk.BooleanVar(value=False),
            'run': tk.BooleanVar(value=False),
            'approve': tk.BooleanVar(value=False)
        }
        
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
        setup_frame = ttk.LabelFrame(left_frame, text="Button Setup")
        setup_frame.pack(fill='x', padx=5, pady=5)
        
        # Save button setup
        save_frame = ttk.Frame(setup_frame)
        save_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Checkbutton(
            save_frame,
            text="Auto Save",
            variable=self.automation_enabled['save'],
            command=lambda: self.save_automation_settings()
        ).pack(side='left')
        
        ttk.Button(
            save_frame,
            text="Set Location",
            command=lambda: self.capture_button_location('save')
        ).pack(side='left', padx=5)
        
        self.save_label = ttk.Label(save_frame, text="Not set")
        self.save_label.pack(side='left', padx=5)
        
        # Run button setup
        run_frame = ttk.Frame(setup_frame)
        run_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Checkbutton(
            run_frame,
            text="Auto Run",
            variable=self.automation_enabled['run'],
            command=lambda: self.save_automation_settings()
        ).pack(side='left')
        
        ttk.Button(
            run_frame,
            text="Set Location",
            command=lambda: self.capture_button_location('run')
        ).pack(side='left', padx=5)
        
        self.run_label = ttk.Label(run_frame, text="Not set")
        self.run_label.pack(side='left', padx=5)
        
        # Approve button setup
        approve_frame = ttk.Frame(setup_frame)
        approve_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Checkbutton(
            approve_frame,
            text="Auto Approve",
            variable=self.automation_enabled['approve'],
            command=lambda: self.save_automation_settings()
        ).pack(side='left')
        
        ttk.Button(
            approve_frame,
            text="Set Location",
            command=lambda: self.capture_button_location('approve')
        ).pack(side='left', padx=5)
        
        self.approve_label = ttk.Label(approve_frame, text="Not set")
        self.approve_label.pack(side='left', padx=5)
        
        # Instructions
        instructions = ttk.Label(
            setup_frame,
            text="Click 'Set Location' when each dialog appears.\n" +
                 "Enable checkboxes for buttons you want to automate.\n" +
                 "Settings are saved per project.",
            justify='left'
        )
        instructions.pack(fill='x', padx=5, pady=5)
        
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
    
    def capture_button_location(self, button_type):
        """Capture VS Code button location"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        if messagebox.askyesno(
            f"Set {button_type.title()} Button Location",
            f"Click OK, then click the {button_type} button in VS Code.\n" +
            "This location will be saved for future automation."
        ):
            # Wait for user to click button
            time.sleep(0.5)
            
            # Start mouse position check
            start_time = time.time()
            last_pos = None
            
            # Wait for mouse to stop moving (user clicking button)
            while time.time() - start_time < 5:  # 5 second timeout
                current_pos = pyautogui.position()
                if last_pos == current_pos:  # Mouse stopped
                    self.button_locations[button_type] = current_pos
                    self.save_button_locations()
                    
                    # Update label
                    label = getattr(self, f"{button_type}_label")
                    label.config(text=f"Set: {current_pos.x}, {current_pos.y}")
                    
                    logging.info(f"Captured {button_type} button location: {current_pos.x}, {current_pos.y}")
                    return True
                last_pos = current_pos
                time.sleep(0.1)
            
            messagebox.showwarning("Timeout", f"Failed to capture {button_type} button location")
            return False
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
        self.load_settings()
    
    def load_settings(self):
        """Load saved settings for current project"""
        if not self.current_project:
            return
            
        config_path = os.path.join(self.current_project['path'], '.cline', 'vscode_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    
                    # Load button locations
                    if 'button_locations' in config:
                        self.button_locations = {
                            k: pyautogui.Point(x=v[0], y=v[1])
                            for k, v in config['button_locations'].items()
                        }
                        
                        # Update labels
                        for button_type in ['save', 'run', 'approve']:
                            if button_type in self.button_locations:
                                pos = self.button_locations[button_type]
                                label = getattr(self, f"{button_type}_label")
                                label.config(text=f"Set: {pos.x}, {pos.y}")
                    
                    # Load automation settings
                    if 'automation_enabled' in config:
                        for button_type, enabled in config['automation_enabled'].items():
                            self.automation_enabled[button_type].set(enabled)
            except:
                self.button_locations = {'save': None, 'run': None, 'approve': None}
                for button_type in ['save', 'run', 'approve']:
                    label = getattr(self, f"{button_type}_label")
                    label.config(text="Not set")
                    self.automation_enabled[button_type].set(False)
    
    def save_settings(self):
        """Save settings for current project"""
        if not self.current_project:
            return
            
        config_dir = os.path.join(self.current_project['path'], '.cline')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'vscode_config.json')
        
        # Load existing config or create new
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
        else:
            config = {}
        
        # Save button locations
        config['button_locations'] = {
            k: [v.x, v.y] for k, v in self.button_locations.items() if v is not None
        }
        
        # Save automation settings
        config['automation_enabled'] = {
            k: v.get() for k, v in self.automation_enabled.items()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
    
    def save_button_locations(self):
        """Save button locations (convenience method)"""
        self.save_settings()
    
    def save_automation_settings(self):
        """Save automation settings (convenience method)"""
        self.save_settings()
    
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
                time.sleep(0.5)  # Wait for VS Code to show dialog
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
            
            # Take screenshot to check for dialogs
            screenshot = pyautogui.screenshot()
            
            # Check each button type
            for button_type in ['save', 'run', 'approve']:
                # Skip if automation not enabled
                if not self.automation_enabled[button_type].get():
                    continue
                    
                # Skip if location not set
                if not self.button_locations[button_type]:
                    continue
                
                # Get button position
                pos = self.button_locations[button_type]
                
                # Check if button is present
                color = screenshot.getpixel((pos.x, pos.y))
                if self.is_button_color(color):
                    pyautogui.click(pos.x, pos.y)
                    logging.info(f"Clicked {button_type} button at {pos.x}, {pos.y}")
                    return True
            
            logging.info("No enabled dialogs detected")
            return False
                
        except Exception as e:
            logging.error(f"Error automating VS Code approval: {e}")
            return False
    
    def is_button_color(self, color):
        """Check if color matches a button"""
        # Convert color to HSV for better matching
        r, g, b = color
        
        # Check if color is close to button colors
        # This needs tuning based on your VS Code theme
        return (
            # Light theme buttons
            (r > 200 and g > 200 and b > 200) or
            # Dark theme buttons
            (r < 100 and g < 100 and b < 100)
        )
