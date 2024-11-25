import tkinter as tk
import pyautogui
import time
import threading
import json
import os
from queue import Queue

class TestDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Dialog")
        self.root.configure(bg='#1e1e1e')  # VS Code dark theme background
        
        # State
        self.running = True
        self.testing = False
        self.update_queue = Queue()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(padx=20, pady=20)
        
        # Create buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#1e1e1e')
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        # Create proceed button (VS Code primary button)
        self.proceed_btn = tk.Button(
            buttons_frame,
            text="Proceed",
            bg='#0e7ad3',  # VS Code primary button blue
            fg='white',
            relief='flat',
            font=('Arial', 14),
            width=15,
            height=2,
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
            font=('Arial', 14),
            width=15,
            height=2,
            command=self.capture_cancel_color
        )
        self.cancel_btn.pack(side='left', padx=10)
        
        # Create info frame
        info_frame = tk.Frame(main_frame, bg='#1e1e1e')
        info_frame.pack(fill='x')
        
        # Create info label
        self.info_label = tk.Label(
            info_frame,
            text="Click a button to capture its color",
            fg='white',
            bg='#1e1e1e',
            font=('Arial', 12)
        )
        self.info_label.pack(pady=(0, 10))
        
        # Create coordinates label
        self.coord_label = tk.Label(
            info_frame,
            text="Mouse: (0, 0)",
            fg='#666666',  # Dimmed text
            bg='#1e1e1e',
            font=('Arial', 10)
        )
        self.coord_label.pack(pady=(0, 10))
        
        # Create test frame
        test_frame = tk.Frame(main_frame, bg='#1e1e1e')
        test_frame.pack(fill='x')
        
        # Create test toggle
        self.test_var = tk.BooleanVar(value=False)
        self.test_toggle = tk.Checkbutton(
            test_frame,
            text="Enable Color Detection",
            variable=self.test_var,
            command=self.toggle_testing,
            fg='white',
            bg='#1e1e1e',
            selectcolor='#0e7ad3',
            font=('Arial', 12)
        )
        self.test_toggle.pack(pady=10)
        
        # Create test result label
        self.test_label = tk.Label(
            test_frame,
            text="",
            fg='white',
            bg='#1e1e1e',
            font=('Arial', 12)
        )
        self.test_label.pack()
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # Start threads
        self.threads = []
        self.start_threads()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Start coordinate updates
        self.update_coordinates()
    
    def start_threads(self):
        """Start worker threads"""
        # Button cycle thread
        cycle_thread = threading.Thread(target=self.cycle_buttons, daemon=True)
        cycle_thread.start()
        self.threads.append(cycle_thread)
        
        # Test thread
        test_thread = threading.Thread(target=self.test_color_detection, daemon=True)
        test_thread.start()
        self.threads.append(test_thread)
        
        # Update thread
        update_thread = threading.Thread(target=self.process_updates, daemon=True)
        update_thread.start()
        self.threads.append(update_thread)
    
    def update_coordinates(self):
        """Update mouse coordinates display"""
        if not self.running:
            return
            
        try:
            pos = pyautogui.position()
            self.coord_label.config(text=f"Mouse: ({pos.x}, {pos.y})")
        except:
            pass
            
        # Schedule next update
        self.root.after(100, self.update_coordinates)
    
    def capture_proceed_color(self):
        """Capture proceed button color"""
        pos = pyautogui.position()
        color = pyautogui.screenshot().getpixel((pos.x, pos.y))
        self.save_color('proceed', color)
        self.update_queue.put(('info', f"Proceed color captured: RGB{color} at ({pos.x}, {pos.y})"))
    
    def capture_cancel_color(self):
        """Capture cancel button color"""
        pos = pyautogui.position()
        color = pyautogui.screenshot().getpixel((pos.x, pos.y))
        self.save_color('cancel', color)
        self.update_queue.put(('info', f"Cancel color captured: RGB{color} at ({pos.x}, {pos.y})"))
    
    def toggle_testing(self):
        """Toggle color detection testing"""
        self.testing = self.test_var.get()
        if not self.testing:
            self.update_queue.put(('test', ''))
    
    def test_color_detection(self):
        """Test color detection at current mouse position"""
        last_check = 0
        while self.running:
            if self.testing:
                current_time = time.time()
                if current_time - last_check >= 0.2:  # Check every 200ms
                    try:
                        pos = pyautogui.position()
                        color = pyautogui.screenshot().getpixel((pos.x, pos.y))
                        
                        # Load saved colors
                        config_path = os.path.join(os.getcwd(), '.cline', 'vscode_config.json')
                        if os.path.exists(config_path):
                            with open(config_path) as f:
                                config = json.load(f)
                                if 'button_colors' in config:
                                    proceed_color = tuple(config['button_colors']['proceed'])
                                    cancel_color = tuple(config['button_colors']['cancel'])
                                    
                                    # Check color matches
                                    if self.colors_match(color, proceed_color):
                                        self.update_queue.put((
                                            'test',
                                            ('proceed', f"Detected proceed button: RGB{color}")
                                        ))
                                    elif self.colors_match(color, cancel_color):
                                        self.update_queue.put((
                                            'test',
                                            ('cancel', f"Detected cancel button: RGB{color}")
                                        ))
                                    else:
                                        self.update_queue.put((
                                            'test',
                                            ('none', f"No button detected: RGB{color}")
                                        ))
                        else:
                            self.update_queue.put(('test', ('error', "No color config found")))
                    except:
                        pass
                    last_check = current_time
            time.sleep(0.05)
    
    def process_updates(self):
        """Process UI updates from queue"""
        while self.running:
            try:
                update_type, data = self.update_queue.get_nowait()
                if update_type == 'info':
                    self.info_label.config(text=data)
                elif update_type == 'test':
                    if not data:
                        self.test_label.config(text="")
                    else:
                        button_type, message = data
                        if button_type == 'proceed':
                            self.test_label.config(text=message, fg='#0e7ad3')
                        elif button_type == 'cancel':
                            self.test_label.config(text=message, fg='#3c3c3c')
                        elif button_type == 'none':
                            self.test_label.config(text=message, fg='white')
                        else:
                            self.test_label.config(text=message, fg='red')
            except:
                pass
            time.sleep(0.05)
    
    def colors_match(self, color1, color2, tolerance=20):
        """Check if colors match within tolerance"""
        return all(
            abs(c1 - c2) <= tolerance
            for c1, c2 in zip(color1, color2)
        )
    
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
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=1)
        
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    dialog = TestDialog()
    dialog.run()
