import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
from datetime import datetime

class CommandHistory(ttk.LabelFrame):
    def __init__(self, parent, credential_manager):
        super().__init__(parent, text="Command History")
        self.credential_manager = credential_manager
        
        # State
        self.current_project = None
        
        # Command history
        history_frame = ttk.Frame(self)
        history_frame.pack(fill='x', pady=5)
        
        self.cmd_tree = ttk.Treeview(
            history_frame,
            columns=('Time', 'Status', 'Duration'),
            show='headings',
            height=6
        )
        self.cmd_tree.heading('Time', text='Time')
        self.cmd_tree.heading('Status', text='Status')
        self.cmd_tree.heading('Duration', text='Duration')
        self.cmd_tree.pack(fill='x', pady=5)
        
        # Command input
        input_frame = ttk.LabelFrame(self, text="Command")
        input_frame.pack(fill='x', padx=5, pady=5)
        
        self.cmd_entry = ttk.Entry(input_frame)
        self.cmd_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        ttk.Button(input_frame, text="Execute", command=self.execute_command).pack(side='right', padx=5, pady=5)
        
        # Command output
        output_frame = ttk.LabelFrame(self, text="Output")
        output_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD)
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
        self.load_history()
    
    def execute_command(self):
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        
        # Inject credentials if needed
        if self.credential_manager:
            task_path = os.path.join(
                self.current_project['path'],
                '.cline',
                'current_task.md'
            )
            if os.path.exists(task_path):
                cmd = self.credential_manager.inject_credentials(cmd, task_path)
        
        self.cmd_entry.delete(0, tk.END)
        self.add_to_history(cmd, datetime.now(), 'Running', '0:00')
        
        # Add command to output
        self.output_text.insert(tk.END, f"\n$ {cmd}\n")
        self.output_text.see(tk.END)
    
    def add_to_history(self, cmd, start_time, status, duration):
        self.cmd_tree.insert(
            '',
            0,
            values=(
                start_time.strftime('%H:%M:%S'),
                status,
                str(duration)
            )
        )
        
        if not self.current_project:
            return
        
        # Save to history file
        history_file = os.path.join(
            self.current_project['path'],
            '.cline',
            'command_history.json'
        )
        try:
            if os.path.exists(history_file):
                with open(history_file) as f:
                    history = json.load(f)
            else:
                history = []
            
            history.insert(0, {
                'command': cmd,
                'timestamp': start_time.isoformat(),
                'status': status,
                'duration': str(duration)
            })
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving command history: {e}")
    
    def load_history(self):
        """Load command history for current project"""
        # Clear current history
        for item in self.cmd_tree.get_children():
            self.cmd_tree.delete(item)
        
        if not self.current_project:
            return
        
        # Load history from file
        history_file = os.path.join(
            self.current_project['path'],
            '.cline',
            'command_history.json'
        )
        if os.path.exists(history_file):
            try:
                with open(history_file) as f:
                    history = json.load(f)
                
                for cmd in history:
                    timestamp = datetime.fromisoformat(cmd['timestamp'])
                    self.cmd_tree.insert(
                        '',
                        'end',
                        values=(
                            timestamp.strftime('%H:%M:%S'),
                            cmd['status'],
                            cmd['duration']
                        )
                    )
            except Exception as e:
                print(f"Error loading command history: {e}")
    
    def add_output(self, output):
        """Add output to the output text area"""
        self.output_text.insert(tk.END, output)
        self.output_text.see(tk.END)
