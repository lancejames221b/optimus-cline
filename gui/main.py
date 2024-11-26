#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from .security_checks import SecurityChecks
from .vscode_automation import VSCodeAutomation
from .task_management import TaskManagement
from .credential_management import CredentialManagement
from .command_history import CommandHistory
from .project_management import ProjectManagement
from .computer_use_manager import ComputerUseManager
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
        
        # Create project management at top
        self.project_management = ProjectManagement(main_frame)
        self.project_management.pack(fill='x', pady=5)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both')
        
        # Create security checks first since other components need it
        self.security_checks = SecurityChecks(notebook)
        
        # Create components
        self.credential_manager = CredentialManagement(notebook)
        self.task_management = TaskManagement(notebook, self.security_checks)
        self.command_history = CommandHistory(notebook, self.credential_manager)
        self.vscode_automation = VSCodeAutomation(notebook, self.security_checks)
        self.computer_use = ComputerUseManager(notebook)
        
        # Add tabs
        notebook.add(self.task_management, text='Tasks')
        notebook.add(self.credential_manager, text='Credentials')
        notebook.add(self.command_history, text='Commands')
        notebook.add(self.vscode_automation, text='VS Code')
        notebook.add(self.computer_use, text='Computer Use')
        notebook.add(self.security_checks, text='Security')
        
        # Bind project events
        self.project_management.bind('<<ProjectChanged>>', self.on_project_changed)
        self.project_management.bind('<<KeysFileChanged>>', self.on_keys_changed)
        
        # Make window appear in front and bind events
        make_window_front(root)
        bind_window_events(root)
    
    def on_project_changed(self, event):
        """Handle project change event"""
        project = self.project_management.current_project
        if project:
            # Update components with new project
            self.task_management.set_project(project)
            self.command_history.set_project(project)
            self.vscode_automation.set_project(project)
            self.computer_use.set_project(project)
    
    def on_keys_changed(self, event):
        """Handle keys file change event"""
        project = self.project_management.current_project
        if project and project['config']['settings']['keys_file']:
            # Update credential manager with new keys file
            self.credential_manager.set_keys_file(
                project['config']['settings']['keys_file']
            )

def main():
    root = tk.Tk()
    app = ClineApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
