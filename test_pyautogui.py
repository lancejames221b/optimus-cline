import tkinter as tk
import pyautogui
import time
import threading

class TestDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Dialog")
        self.root.configure(bg='#1e1e1e')  # VS Code dark theme background
        
        # Create buttons frame
        buttons_frame = tk.Frame(self.root, bg='#1e1e1e')
        buttons_frame.pack(padx=20, pady=20)
        
        # Create proceed button (red)
        self.proceed_btn = tk.Button(
            buttons_frame,
            text="Proceed",
            bg='#ff0000',  # Red
            fg='white',
            relief='flat',
            padx=10,
            pady=5
        )
        self.proceed_btn.pack(side='left', padx=10)
        
        # Create cancel button (grey)
        self.cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            bg='#808080',  # Grey
            fg='white',
            relief='flat',
            padx=10,
            pady=5
        )
        self.cancel_btn.pack(side='left', padx=10)
        
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
