import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from datetime import datetime

class TaskManagement(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Task Management")
        
        # State
        self.current_project = None
        
        # Create toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', pady=5)
        
        ttk.Button(toolbar, text="New Task", command=self.new_task_dialog).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Open", command=self.open_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Archive", command=self.archive_task).pack(side='left', padx=5)
        
        # Tasks list
        self.tasks_tree = ttk.Treeview(self, columns=('Status',), show='tree headings')
        self.tasks_tree.heading('Status', text='Status')
        self.tasks_tree.pack(expand=True, fill='both', pady=5)
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
        self.refresh_tasks()
    
    def new_task_dialog(self):
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("New Task")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Description
        desc_frame = ttk.LabelFrame(dialog, text="Description")
        desc_frame.pack(fill='x', padx=5, pady=5)
        desc_entry = ttk.Entry(desc_frame)
        desc_entry.pack(fill='x', padx=5, pady=5)
        
        # System Prompt
        prompt_frame = ttk.LabelFrame(dialog, text="System Prompt")
        prompt_frame.pack(fill='x', padx=5, pady=5)
        prompt_text = scrolledtext.ScrolledText(prompt_frame, height=5)
        prompt_text.pack(fill='x', padx=5, pady=5)
        
        # Required Credentials
        creds_frame = ttk.LabelFrame(dialog, text="Required Credentials")
        creds_frame.pack(fill='x', padx=5, pady=5)
        
        service_frame = ttk.Frame(creds_frame)
        service_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(service_frame, text="Service:").pack(side='left')
        service_entry = ttk.Entry(service_frame)
        service_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        keys_frame = ttk.Frame(creds_frame)
        keys_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(keys_frame, text="Keys:").pack(side='left')
        keys_entry = ttk.Entry(keys_frame)
        keys_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        def create_task():
            desc = desc_entry.get().strip()
            prompt = prompt_text.get("1.0", "end-1c").strip()
            service = service_entry.get().strip()
            keys = keys_entry.get().strip()
            
            if not desc:
                messagebox.showwarning("Warning", "Please enter a description")
                return
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            task_id = f"task_{timestamp}_{desc.lower().replace(' ', '_')}"
            task_dir = os.path.join(self.current_project['path'], '.cline', 'tasks', task_id)
            os.makedirs(task_dir)
            
            # Create task.json
            task_data = {
                'id': task_id,
                'title': desc,
                'systemPrompt': prompt,
                'service': service,
                'keys': keys.split(',') if keys else [],
                'status': 'active',
                'created': datetime.now().isoformat()
            }
            
            with open(os.path.join(task_dir, 'task.json'), 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Create task.md
            with open(os.path.join(task_dir, 'task.md'), 'w') as f:
                f.write(f"# Task: {desc}\n")
                f.write(f"Date: {timestamp}\n\n")
                
                f.write("## Required Credentials\n")
                if service and keys:
                    f.write(f"- Service: {service}\n")
                    f.write(f"- Keys: {keys}\n\n")
                else:
                    f.write("- No credentials required\n\n")
                
                f.write("## System Prompt\n")
                f.write(f"{prompt}\n\n")
                f.write("## Steps\n1. [Step details]\n\n")
                f.write("## Results\n- [ ] Task completed\n")
            
            dialog.destroy()
            self.refresh_tasks()
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Create", command=create_task).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='right')
    
    def open_task(self):
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        task_id = selected[0]
        task_path = os.path.join(
            self.current_project['path'],
            '.cline',
            'tasks',
            task_id,
            'task.md'
        )
        
        try:
            subprocess.run(['code', task_path])
        except FileNotFoundError:
            if os.name == 'posix':  # macOS/Linux
                subprocess.run(['open', task_path])
            else:  # Windows
                os.startfile(task_path)
    
    def archive_task(self):
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        task_id = selected[0]
        task_path = os.path.join(
            self.current_project['path'],
            '.cline',
            'tasks',
            task_id,
            'task.json'
        )
        
        with open(task_path) as f:
            task = json.load(f)
        
        task['status'] = 'archived'
        
        with open(task_path, 'w') as f:
            json.dump(task, f, indent=2)
        
        self.refresh_tasks()
    
    def refresh_tasks(self):
        # Clear current items
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        
        if not self.current_project:
            return
            
        # Load tasks
        tasks_dir = os.path.join(self.current_project['path'], '.cline', 'tasks')
        if not os.path.exists(tasks_dir):
            return
            
        for task_id in os.listdir(tasks_dir):
            task_path = os.path.join(tasks_dir, task_id, 'task.json')
            if os.path.exists(task_path):
                with open(task_path) as f:
                    task = json.load(f)
                    self.tasks_tree.insert('', 'end', task['id'], text=task['title'], values=(task['status'],))
