import tkinter as tk
from tkinter import ttk, messagebox
import logging
import uuid
from typing import Optional, Dict, Any
from .computer_use import ComputerUse, ComputerTask, ResourceType, PermissionLevel, ResourcePermission

class ComputerUseManager(ttk.Frame):
    """GUI manager for computer use capabilities"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize computer use engine
        self.computer = ComputerUse()
        
        # State
        self.pending_tasks: Dict[str, ComputerTask] = {}
        self.current_project = None
        
        # Create main layout
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the GUI elements"""
        # Create main layout
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Controls
        controls_frame = ttk.LabelFrame(main_frame, text="Computer Use Controls")
        controls_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Permissions
        perm_frame = ttk.LabelFrame(controls_frame, text="Permissions")
        perm_frame.pack(fill='x', padx=5, pady=5)
        
        # Resource type
        type_frame = ttk.Frame(perm_frame)
        type_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(type_frame, text="Resource Type:").pack(side='left')
        self.resource_type = ttk.Combobox(
            type_frame,
            values=[rt.value for rt in ResourceType],
            state='readonly'
        )
        self.resource_type.pack(side='left', padx=5)
        
        # Resource path
        path_frame = ttk.Frame(perm_frame)
        path_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(path_frame, text="Resource Path:").pack(side='left')
        self.resource_path = ttk.Entry(path_frame)
        self.resource_path.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(
            path_frame,
            text="Browse",
            command=self._browse_resource
        ).pack(side='right')
        
        # Permission level
        level_frame = ttk.Frame(perm_frame)
        level_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(level_frame, text="Permission Level:").pack(side='left')
        self.permission_level = ttk.Combobox(
            level_frame,
            values=[pl.value for pl in PermissionLevel],
            state='readonly'
        )
        self.permission_level.pack(side='left', padx=5)
        
        # Approval required
        self.approval_required = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            perm_frame,
            text="Requires Approval",
            variable=self.approval_required
        ).pack(padx=5, pady=2)
        
        # Add permission button
        ttk.Button(
            perm_frame,
            text="Add Permission",
            command=self._add_permission
        ).pack(padx=5, pady=5)
        
        # Task approval
        approval_frame = ttk.LabelFrame(controls_frame, text="Task Approval")
        approval_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Pending tasks
        self.task_list = ttk.Treeview(
            approval_frame,
            columns=('ID', 'Type', 'Resource', 'Action'),
            show='headings'
        )
        self.task_list.heading('ID', text='ID')
        self.task_list.heading('Type', text='Type')
        self.task_list.heading('Resource', text='Resource')
        self.task_list.heading('Action', text='Action')
        self.task_list.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Approval buttons
        btn_frame = ttk.Frame(approval_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Approve",
            command=self._approve_task
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Deny",
            command=self._deny_task
        ).pack(side='left', padx=5)
        
        # Right side - Activity
        activity_frame = ttk.LabelFrame(main_frame, text="Activity Log")
        activity_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Activity list
        self.activity_list = ttk.Treeview(
            activity_frame,
            columns=('Time', 'Task', 'Status'),
            show='headings'
        )
        self.activity_list.heading('Time', text='Time')
        self.activity_list.heading('Task', text='Task')
        self.activity_list.heading('Status', text='Status')
        self.activity_list.pack(fill='both', expand=True, padx=5, pady=5)
    
    def _browse_resource(self):
        """Browse for a resource path"""
        resource_type = self.resource_type.get()
        
        if resource_type == ResourceType.FILE.value:
            path = filedialog.askopenfilename(title="Select Resource")
            if path:
                self.resource_path.delete(0, tk.END)
                self.resource_path.insert(0, path)
        elif resource_type == ResourceType.APPLICATION.value:
            path = filedialog.askopenfilename(
                title="Select Application",
                filetypes=[("Applications", "*.app"), ("All files", "*.*")]
            )
            if path:
                self.resource_path.delete(0, tk.END)
                self.resource_path.insert(0, path)
    
    def _add_permission(self):
        """Add a new permission"""
        try:
            # Validate inputs
            if not self.resource_type.get():
                messagebox.showwarning("Warning", "Please select a resource type")
                return
                
            if not self.resource_path.get().strip():
                messagebox.showwarning("Warning", "Please enter a resource path")
                return
                
            if not self.permission_level.get():
                messagebox.showwarning("Warning", "Please select a permission level")
                return
            
            # Create permission
            permission = ResourcePermission(
                resource_type=ResourceType(self.resource_type.get()),
                resource_path=self.resource_path.get().strip(),
                permission_level=PermissionLevel(self.permission_level.get()),
                requires_approval=self.approval_required.get()
            )
            
            # Add to computer use engine
            self.computer.security.add_permission(permission)
            
            # Clear inputs
            self.resource_path.delete(0, tk.END)
            self.resource_type.set('')
            self.permission_level.set('')
            
            messagebox.showinfo("Success", "Permission added successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add permission: {e}")
    
    def _approve_task(self):
        """Approve selected task"""
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to approve")
            return
        
        task_id = self.task_list.item(selection[0])['values'][0]
        if task_id not in self.pending_tasks:
            messagebox.showerror("Error", "Task not found")
            return
        
        task = self.pending_tasks[task_id]
        result = self.computer.execute_task(task)
        
        # Update activity log
        self.activity_list.insert(
            '',
            0,
            values=(
                "now",  # TODO: Add proper timestamp
                f"{task.resource_type.value} - {task.action}",
                "Success" if result else "Failed"
            )
        )
        
        # Remove from pending
        del self.pending_tasks[task_id]
        self.task_list.delete(selection[0])
    
    def _deny_task(self):
        """Deny selected task"""
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to deny")
            return
        
        task_id = self.task_list.item(selection[0])['values'][0]
        if task_id not in self.pending_tasks:
            messagebox.showerror("Error", "Task not found")
            return
        
        # Update activity log
        task = self.pending_tasks[task_id]
        self.activity_list.insert(
            '',
            0,
            values=(
                "now",  # TODO: Add proper timestamp
                f"{task.resource_type.value} - {task.action}",
                "Denied"
            )
        )
        
        # Remove from pending
        del self.pending_tasks[task_id]
        self.task_list.delete(selection[0])
    
    def submit_task(self, task_type: str, resource_type: ResourceType,
                   resource_path: str, action: str,
                   parameters: Dict[str, Any]) -> Optional[Any]:
        """Submit a task for execution"""
        # Create task
        task_id = str(uuid.uuid4())
        task = ComputerTask(
            task_id=task_id,
            task_type=task_type,
            resource_type=resource_type,
            resource_path=resource_path,
            action=action,
            parameters=parameters
        )
        
        # Check if approval required
        resource_key = f"{resource_type.value}:{resource_path}"
        if resource_key in self.computer.security.permissions:
            permission = self.computer.security.permissions[resource_key]
            if not permission.requires_approval:
                # Execute immediately
                result = self.computer.execute_task(task)
                
                # Update activity log
                self.activity_list.insert(
                    '',
                    0,
                    values=(
                        "now",  # TODO: Add proper timestamp
                        f"{task.resource_type.value} - {task.action}",
                        "Success" if result else "Failed"
                    )
                )
                
                return result
        
        # Add to pending tasks
        self.pending_tasks[task_id] = task
        
        # Add to task list
        self.task_list.insert(
            '',
            0,
            values=(
                task_id,
                task_type,
                resource_path,
                action
            )
        )
        
        return None
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
