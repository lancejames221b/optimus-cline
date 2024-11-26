import tkinter as tk
from tkinter import ttk
import pyautogui
import time

class TestDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Dialog")
        
        # Create buttons frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(padx=20, pady=20)
        
        # Create proceed button (red)
        self.proceed_btn = ttk.Button(
            buttons_frame,
            text="Proceed",
            style='Proceed.TButton'
        )
        self.proceed_btn.pack(side='left', padx=10)
        
        # Create cancel button (grey)
        self.cancel_btn = ttk.Button(
            buttons_frame,
            text="Cancel",
            style='Cancel.TButton'
        )
        self.cancel_btn.pack(side='left', padx=10)
        
        # Create styles
        style = ttk.Style()
        
        # Proceed button style (red)
        style.configure(
            'Proceed.TButton',
            background='red',
            foreground='white'
        )
        
        # Cancel button style (grey)
        style.configure(
            'Cancel.TButton',
            background='grey',
            foreground='black'
        )
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # Start button cycle
        self.cycle_buttons()
    
    def cycle_buttons(self):
        """Cycle between proceed and cancel buttons"""
        while True:
            # Show proceed button
            self.proceed_btn.state(['!disabled'])
            self.cancel_btn.state(['disabled'])
            self.root.update()
            time.sleep(2)
            
            # Show cancel button
            self.proceed_btn.state(['disabled'])
            self.cancel_btn.state(['!disabled'])
            self.root.update()
            time.sleep(2)
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    dialog = TestDialog()
    dialog.run()
