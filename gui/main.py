#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from .security_checks import SecurityChecks
from .vscode_automation import VSCodeAutomation
from .task_management import TaskManagement
from .credential_management import CredentialManagement
from .command_history import CommandHistory
from .utils import setup_logging, make_window_front, bind_window_events

class ClineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cline")
        self.root.geometry("800x600")
        
        # Setup logging
        setup_logging()
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both')
        
        # Create components
        self.security_checks = SecurityChecks(notebook)
        self.credential_manager = CredentialManagement(notebook)
        self.task_management = TaskManagement(notebook)
        self.command_history = CommandHistory(notebook, self.credential_manager)
        self.vscode_automation = VSCodeAutomation(notebook, self.security_checks)
        
        # Add tabs
        notebook.add(self.task_management, text='Tasks')
        notebook.add(self.credential_manager, text='Credentials')
        notebook.add(self.command_history, text='Commands')
        notebook.add(self.vscode_automation, text='VS Code')
        notebook.add(self.security_checks, text='Security')
        
        # Make window appear in front and bind events
        make_window_front(root)
        bind_window_events(root)

def main():
    root = tk.Tk()
    app = ClineApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
