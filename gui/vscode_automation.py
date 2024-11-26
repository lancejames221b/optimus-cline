import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import logging
import pyautogui
import time
import os
import json
import threading
from datetime import datetime

class VSCodeAutomation(ttk.LabelFrame):
    def __init__(self, parent, security_checks):
        super().__init__(parent, text="VS Code Automation")
        self.security_checks = security_checks
        
        # State
        self.current_project = None
        self.button_location = None
        self.automation_enabled = tk.BooleanVar(value=False)
        self.monitoring = False
        self.monitor_thread = None
        self.last_click_time = 0
        self.CLICK_COOLDOWN = 2.0  # Seconds between clicks
        self.COLOR_TOLERANCE = 20  # Color matching tolerance
        
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
        
        # Button location
        location_frame = ttk.Frame(setup_frame)
        location_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Button(
            location_frame,
            text="Set Button Location",
            command=self.capture_button_location
        ).pack(side='left', padx=5)
        
        self.location_label = ttk.Label(location_frame, text="Not set")
        self.location_label.pack(side='left', padx=5)
        
        # Launch test dialog
        test_frame = ttk.Frame(setup_frame)
        test_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Button(
            test_frame,
            text="Launch Test Dialog",
            command=self.launch_test_dialog
        ).pack(side='left', padx=5)
        
        # Automation toggle
        toggle_frame = ttk.Frame(setup_frame)
        toggle_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Checkbutton(
            toggle_frame,
            text="Enable Auto-Click",
            variable=self.automation_enabled,
            command=self.toggle_automation
        ).pack(side='left')
        
        # Debug info
        self.debug_label = ttk.Label(toggle_frame, text="")
        self.debug_label.pack(side='left', padx=5)
        
        # Instructions
        instructions = ttk.Label(
            setup_frame,
            text="1. Launch Test Dialog to capture button colors\n" +
                 "2. Set button location in VS Code\n" +
                 "3. Enable Auto-Click to automatically click buttons",
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
    
    def launch_test_dialog(self):
        """Launch test dialog to capture button colors"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        # Import here to avoid circular dependency
        import test_pyautogui
        dialog = test_pyautogui.TestDialog()
        dialog.run()
    
    def capture_button_location(self):
        """Capture VS Code button location"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        if messagebox.askyesno(
            "Set Button Location",
            "Click OK, then click any VS Code dialog button.\n" +
            "This location will be used for all buttons."
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
                    self.button_location = current_pos
                    self.save_button_location()
                    self.location_label.config(text=f"Set: {current_pos.x}, {current_pos.y}")
                    logging.info(f"Captured button location: {current_pos.x}, {current_pos.y}")
                    return True
                last_pos = current_pos
                time.sleep(0.1)
            
            messagebox.showwarning("Timeout", "Failed to capture button location")
            return False
    
    def toggle_automation(self):
        """Toggle button automation"""
        if self.automation_enabled.get():
            if not self.button_location:
                messagebox.showwarning(
                    "Warning",
                    "Please set button location first"
                )
                self.automation_enabled.set(False)
                return
            
            # Check if colors are configured
            config_path = os.path.join(self.current_project['path'], '.cline', 'vscode_config.json')
            if not os.path.exists(config_path):
                messagebox.showwarning(
                    "Warning",
                    "Please capture button colors using Test Dialog first"
                )
                self.automation_enabled.set(False)
                return
            
            # Start monitoring if not already running
            if not self.monitoring:
                self.monitoring = True
                self.monitor_thread = threading.Thread(target=self.monitor_buttons, daemon=True)
                self.monitor_thread.start()
                logging.info("Started button monitoring")
        else:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1)
                self.monitor_thread = None
                logging.info("Stopped button monitoring")
    
    def monitor_buttons(self):
        """Monitor for button appearance"""
        while self.monitoring:
            try:
                if not self.button_location:
                    break
                
                # Take screenshot
                screenshot = pyautogui.screenshot()
                
                # Get current pixel color
                current_pixel = screenshot.getpixel((self.button_location.x, self.button_location.y))
                
                # Load saved colors
                config_path = os.path.join(self.current_project['path'], '.cline', 'vscode_config.json')
                if os.path.exists(config_path):
                    with open(config_path) as f:
                        config = json.load(f)
                        if 'button_colors' in config:
                            proceed_color = tuple(config['button_colors']['proceed'])
                            cancel_color = tuple(config['button_colors']['cancel'])
                            
                            # Check if it's a proceed button
                            if self.colors_match(current_pixel, proceed_color):
                                self.debug_label.config(text=f"Proceed button detected: RGB{current_pixel}")
                                
                                # Check cooldown
                                current_time = time.time()
                                if current_time - self.last_click_time >= self.CLICK_COOLDOWN:
                                    # Click button
                                    pyautogui.click(self.button_location.x, self.button_location.y)
                                    logging.info(f"Auto-clicked proceed button at {self.button_location.x}, {self.button_location.y}")
                                    
                                    # Update last click time
                                    self.last_click_time = current_time
                                    
                                    # Wait before checking again
                                    time.sleep(0.5)
                                else:
                                    self.debug_label.config(text="Waiting for cooldown")
                            
                            # Check if it's a cancel button
                            elif self.colors_match(current_pixel, cancel_color):
                                self.debug_label.config(text=f"Cancel button detected: RGB{current_pixel}")
                            else:
                                self.debug_label.config(text=f"No button detected: RGB{current_pixel}")
                
                time.sleep(0.1)  # Small delay between checks
                
            except Exception as e:
                logging.error(f"Error in button monitor: {e}")
                time.sleep(1)  # Longer delay after error
    
    def colors_match(self, color1, color2):
        """Check if colors match within tolerance"""
        return all(
            abs(c1 - c2) <= self.COLOR_TOLERANCE
            for c1, c2 in zip(color1, color2)
        )
    
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
                    
                    # Load button location
                    if 'button_location' in config:
                        x, y = config['button_location']
                        self.button_location = pyautogui.Point(x, y)
                        self.location_label.config(text=f"Set: {x}, {y}")
                    
                    # Load automation setting
                    if 'automation_enabled' in config:
                        self.automation_enabled.set(config['automation_enabled'])
                        if config['automation_enabled']:
                            self.toggle_automation()  # Start monitoring if enabled
                            
                    logging.info("Loaded VS Code automation settings")
            except Exception as e:
                logging.error(f"Error loading settings: {e}")
                self.button_location = None
                self.location_label.config(text="Not set")
                self.automation_enabled.set(False)
    
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
        
        # Save button location
        if self.button_location:
            config['button_location'] = [self.button_location.x, self.button_location.y]
        
        # Save automation setting
        config['automation_enabled'] = self.automation_enabled.get()
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
            
        logging.info("Saved VS Code automation settings")
    
    def save_button_location(self):
        """Save button location (convenience method)"""
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
