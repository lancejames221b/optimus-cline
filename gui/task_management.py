import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import subprocess
import pyautogui
import pyperclip
import time
from datetime import datetime

class TaskManagement(ttk.LabelFrame):
    def __init__(self, parent, security_checks):
        super().__init__(parent, text="Task Management")
        
        # State
        self.current_project = None
        self.security_checks = security_checks
        
        # Create main layout
        paned = ttk.PanedWindow(self, orient='horizontal')
        paned.pack(expand=True, fill='both')
        
        # Left side - Task list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame)
        
        # Toolbar
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill='x', pady=5)
        
        ttk.Button(toolbar, text="New Task", command=self.new_task_dialog).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Edit", command=self.edit_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Open", command=self.open_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Archive", command=self.archive_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Set Current", command=self.set_current_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Tell Cline", command=self.tell_cline).pack(side='left', padx=5)
        
        # Tasks list
        self.tasks_tree = ttk.Treeview(left_frame, columns=('Status',), show='tree headings')
        self.tasks_tree.heading('Status', text='Status')
        self.tasks_tree.pack(expand=True, fill='both', pady=5)
        
        # Right side - Task preview
        right_frame = ttk.Frame(paned)
        paned.add(right_frame)
        
        # Preview
        preview_frame = ttk.LabelFrame(right_frame, text="Task Preview")
        preview_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD)
        self.preview_text.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Bind selection
        self.tasks_tree.bind('<<TreeviewSelect>>', self.on_task_select)
    
    def tell_cline(self):
        """Tell Cline about the current task using keyboard shortcuts"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
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
            # Copy task path to clipboard
            pyperclip.copy(f"task {task_path}")
            
            # Prompt user
            if messagebox.askyesno(
                "Tell Cline",
                "Task command copied to clipboard.\nClick OK, then press Cmd+V (Mac) or Ctrl+V (Windows) to paste in Cline.\nProceed?"
            ):
                # Wait for user to switch to Cline
                time.sleep(1)
                
                # Paste and press enter
                pyautogui.hotkey('command' if os.name == 'posix' else 'ctrl', 'v')
                time.sleep(0.1)
                pyautogui.press('enter')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to tell Cline: {e}")
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
        self.refresh_tasks()
        
        # Open VS Code for project
        try:
            subprocess.run(['code', project['path']])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open VS Code: {e}")
    
    def set_current_task(self):
        """Set the selected task as the current task"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        task_id = selected[0]
        
        # Create current_task.md symlink
        current_task_path = os.path.join(
            self.current_project['path'],
            '.cline',
            'current_task.md'
        )
        
        task_path = os.path.join(
            self.current_project['path'],
            '.cline',
            'tasks',
            task_id,
            'task.md'
        )
        
        # Remove existing symlink if it exists
        if os.path.exists(current_task_path):
            os.remove(current_task_path)
        
        # Create symlink
        os.symlink(task_path, current_task_path)
        
        # Also write task ID to current_task.txt for Cline CLI
        with open(os.path.join(self.current_project['path'], '.cline', 'current_task.txt'), 'w') as f:
            f.write(task_id)
        
        # Copy task path to clipboard
        pyperclip.copy(task_path)
        
        messagebox.showinfo("Success", f"Set current task to: {task_id}\nTask path copied to clipboard")
    
    def on_task_select(self, event):
        """Handle task selection"""
        selected = self.tasks_tree.selection()
        if not selected:
            self.preview_text.delete('1.0', tk.END)
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
            with open(task_path) as f:
                content = f.read()
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', content)
        except Exception as e:
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', f"Error loading task: {e}")
    
    def get_system_prompt(self, user_prompt):
        """Get system prompt with environment details"""
        if not self.current_project:
            return user_prompt
            
        # Get keys file info
        keys_file = self.current_project['config']['settings'].get('keys_file', 'Not configured')
        
        # Get security checks
        active_checks = self.security_checks.get_active_checks()
        all_checks = self.security_checks.get_all_checks()
        
        # Build environment section
        env_info = [
            "# Environment",
            f"Keys File: {keys_file}",
            "",
            "# Security Checks",
            "Active:",
        ]
        
        for check in active_checks:
            env_info.append(f"- [x] {check}")
            
        env_info.append("")
        env_info.append("Inactive:")
        
        for check in all_checks:
            if check not in active_checks:
                env_info.append(f"- [ ] {check}")
        
        # Combine with user prompt
        return "\n".join([
            "\n".join(env_info),
            "",
            "# User Prompt",
            user_prompt
        ])
    
    def edit_task(self):
        """Edit selected task"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
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
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Task: {task['title']}")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Description
        desc_frame = ttk.LabelFrame(dialog, text="Description")
        desc_frame.pack(fill='x', padx=5, pady=5)
        desc_entry = ttk.Entry(desc_frame)
        desc_entry.insert(0, task['title'])
        desc_entry.pack(fill='x', padx=5, pady=5)
        
        # System Prompt
        prompt_frame = ttk.LabelFrame(dialog, text="System Prompt")
        prompt_frame.pack(fill='x', padx=5, pady=5)
        prompt_text = scrolledtext.ScrolledText(prompt_frame, height=5)
        prompt_text.insert('1.0', task.get('systemPrompt', ''))
        prompt_text.pack(fill='x', padx=5, pady=5)
        
        # Required Credentials
        creds_frame = ttk.LabelFrame(dialog, text="Required Credentials")
        creds_frame.pack(fill='x', padx=5, pady=5)
        
        service_frame = ttk.Frame(creds_frame)
        service_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(service_frame, text="Service:").pack(side='left')
        service_entry = ttk.Entry(service_frame)
        service_entry.insert(0, task.get('service', ''))
        service_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        keys_frame = ttk.Frame(creds_frame)
        keys_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(keys_frame, text="Keys:").pack(side='left')
        keys_entry = ttk.Entry(keys_frame)
        keys_entry.insert(0, ','.join(task.get('keys', [])))
        keys_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        def save_task():
            desc = desc_entry.get().strip()
            prompt = prompt_text.get("1.0", "end-1c").strip()
            service = service_entry.get().strip()
            keys = keys_entry.get().strip()
            
            if not desc:
                messagebox.showwarning("Warning", "Please enter a description")
                return
            
            # Update task.json
            task['title'] = desc
            task['systemPrompt'] = prompt
            task['service'] = service
            task['keys'] = keys.split(',') if keys else []
            
            with open(task_path, 'w') as f:
                json.dump(task, f, indent=2)
            
            # Update task.md
            md_path = os.path.join(
                self.current_project['path'],
                '.cline',
                'tasks',
                task_id,
                'task.md'
            )
            
            with open(md_path, 'w') as f:
                f.write(f"# Task: {desc}\n")
                f.write(f"Date: {task['created']}\n\n")
                
                f.write("## Required Credentials\n")
                if service and keys:
                    f.write(f"- Service: {service}\n")
                    f.write(f"- Keys: {keys}\n\n")
                else:
                    f.write("- No credentials required\n\n")
                
                f.write("## System Prompt\n")
                f.write(f"{self.get_system_prompt(prompt)}\n\n")
                f.write("## Steps\n1. [Step details]\n\n")
                f.write("## Results\n- [ ] Task completed\n")
            
            dialog.destroy()
            self.refresh_tasks()
            self.on_task_select(None)  # Refresh preview
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Save", command=save_task).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='right')
    
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
                f.write(f"{self.get_system_prompt(prompt)}\n\n")
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
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
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
            # Open VS Code for project and task
            subprocess.run(['code', self.current_project['path'], task_path])
        except FileNotFoundError:
            if os.name == 'posix':  # macOS/Linux
                subprocess.run(['open', task_path])
            else:  # Windows
                os.startfile(task_path)
    
    def archive_task(self):
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
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
        self.on_task_select(None)  # Refresh preview
    
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
