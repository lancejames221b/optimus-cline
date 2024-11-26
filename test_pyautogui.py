import tkinter as tk
import pyautogui
import time
import threading
import json
import os

class TestDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Dialog")
        self.root.configure(bg='#1e1e1e')  # VS Code dark theme background
        
        # Create buttons frame
        buttons_frame = tk.Frame(self.root, bg='#1e1e1e')
        buttons_frame.pack(padx=20, pady=20)
        
        # Create proceed button (VS Code primary button)
        self.proceed_btn = tk.Button(
            buttons_frame,
            text="Proceed",
            bg='#0e7ad3',  # VS Code primary button blue
            fg='white',
            relief='flat',
            padx=10,
            pady=5,
            command=self.capture_proceed_color
        )
        self.proceed_btn.pack(side='left', padx=10)
        
        # Create cancel button (VS Code secondary button)
        self.cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            bg='#3c3c3c',  # VS Code secondary button grey
            fg='white',
            relief='flat',
            padx=10,
            pady=5,
            command=self.capture_cancel_color
        )
        self.cancel_btn.pack(side='left', padx=10)
        
        # Create info label
        self.info_label = tk.Label(
            self.root,
            text="Click a button to capture its color",
            fg='white',
            bg='#1e1e1e'
        )
        self.info_label.pack(pady=10)
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # Start button cycle in a separate thread
        self.running = True
        self.cycle_thread = threading.Thread(target=self.cycle_buttons, daemon=True)
        self.cycle_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def capture_proceed_color(self):
        """Capture proceed button color"""
        pos = pyautogui.position()
        color = pyautogui.screenshot().getpixel((pos.x, pos.y))
        self.save_color('proceed', color)
        self.info_label.config(text=f"Proceed color captured: RGB{color}")
    
    def capture_cancel_color(self):
        """Capture cancel button color"""
        pos = pyautogui.position()
        color = pyautogui.screenshot().getpixel((pos.x, pos.y))
        self.save_color('cancel', color)
        self.info_label.config(text=f"Cancel color captured: RGB{color}")
    
    def save_color(self, button_type, color):
        """Save button color to config"""
        config_dir = os.path.join(os.getcwd(), '.cline')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'vscode_config.json')
        
        # Load existing config or create new
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update button colors
        if 'button_colors' not in config:
            config['button_colors'] = {}
        config['button_colors'][button_type] = color
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def cycle_buttons(self):
        """Cycle between proceed and cancel buttons"""
        while self.running:
            # Show proceed button
            self.proceed_btn.configure(state='normal')
            self.cancel_btn.configure(state='disabled')
            time.sleep(2)
            
            if not self.running:
                break
            
            # Show cancel button
            self.proceed_btn.configure(state='disabled')
            self.cancel_btn.configure(state='normal')
            time.sleep(2)
    
    def on_close(self):
        """Handle window close"""
        self.running = False
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    dialog = TestDialog()
    dialog.run()
