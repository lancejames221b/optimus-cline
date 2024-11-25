import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import logging

class CredentialManagement(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Credential Management")
        
        # State
        self.keys_file = None
        
        # Keys file frame
        keys_frame = ttk.Frame(self)
        keys_frame.pack(fill='x', pady=5)
        
        ttk.Label(keys_frame, text="Keys file:").pack(side='left')
        self.keys_label = ttk.Label(keys_frame, text="No file selected")
        self.keys_label.pack(side='left', padx=5)
        ttk.Button(keys_frame, text="Select File", command=self.select_keys_file).pack(side='left', padx=5)
        
        # Add credential frame
        cred_frame = ttk.LabelFrame(self, text="Add Credential")
        cred_frame.pack(fill='x', padx=5, pady=5)
        
        # Service row
        service_frame = ttk.Frame(cred_frame)
        service_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(service_frame, text="Service:", width=10).pack(side='left')
        self.service_entry = ttk.Entry(service_frame)
        self.service_entry.pack(side='left', fill='x', expand=True)
        
        # Key row
        key_frame = ttk.Frame(cred_frame)
        key_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(key_frame, text="Key:", width=10).pack(side='left')
        self.key_entry = ttk.Entry(key_frame)
        self.key_entry.pack(side='left', fill='x', expand=True)
        
        # Value row
        value_frame = ttk.Frame(cred_frame)
        value_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(value_frame, text="Value:", width=10).pack(side='left')
        self.value_entry = ttk.Entry(value_frame)
        self.value_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(cred_frame, text="Add", command=self.add_credential).pack(pady=5)
        
        # Credentials list
        self.creds_tree = ttk.Treeview(self, columns=('Value',), show='tree headings')
        self.creds_tree.heading('Value', text='Value')
        self.creds_tree.pack(expand=True, fill='both', pady=5)
    
    def select_keys_file(self):
        file_path = filedialog.askopenfilename(
            title="Select keys.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            self.keys_file = file_path
            self.keys_label.config(text=os.path.basename(file_path))
            self.refresh_credentials()
    
    def add_credential(self):
        if not self.keys_file:
            messagebox.showwarning("Warning", "Please select a keys.txt file first")
            return
        
        service = self.service_entry.get().strip()
        key = self.key_entry.get().strip()
        value = self.value_entry.get().strip()
        
        if not all([service, key, value]):
            messagebox.showwarning("Warning", "Please fill in all fields")
            return
        
        # Read current content
        try:
            with open(self.keys_file) as f:
                content = f.read()
        except:
            content = ""
        
        # Find or create service section
        if f"[{service}]" not in content:
            if content and not content.endswith('\n\n'):
                content += '\n\n'
            content += f"[{service}]\n"
        
        # Add key-value pair
        lines = content.split('\n')
        service_section = False
        key_added = False
        
        new_lines = []
        for line in lines:
            if line.strip() == f"[{service}]":
                service_section = True
                new_lines.append(line)
                new_lines.append(f"{key}={value}")
                key_added = True
            elif line.strip().startswith('['):
                service_section = False
                if not key_added and service_section:
                    new_lines.append(f"{key}={value}")
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Write back to file
        with open(self.keys_file, 'w') as f:
            f.write('\n'.join(new_lines))
        
        # Clear entries
        self.service_entry.delete(0, 'end')
        self.key_entry.delete(0, 'end')
        self.value_entry.delete(0, 'end')
        
        self.refresh_credentials()
    
    def refresh_credentials(self):
        if not self.keys_file:
            return
        
        # Clear current items
        for item in self.creds_tree.get_children():
            self.creds_tree.delete(item)
        
        # Read and parse keys file
        current_section = None
        section_id = None
        
        with open(self.keys_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    section_id = self.creds_tree.insert('', 'end', text=current_section)
                elif '=' in line and current_section:
                    key, value = line.split('=', 1)
                    self.creds_tree.insert(section_id, 'end', text=key.strip(), values=('••••••',))
    
    def parse_task_credentials(self, task_path):
        """Parse credentials from task.md"""
        try:
            with open(task_path) as f:
                content = f.read()
            
            # Find credentials section
            creds_match = re.search(
                r'## Required Credentials\n(.*?)\n\n',
                content,
                re.DOTALL
            )
            if not creds_match:
                return None, []
            
            creds_section = creds_match.group(1)
            
            # Parse service and keys
            service_match = re.search(r'- Service: (.*)', creds_section)
            keys_match = re.search(r'- Keys: (.*)', creds_section)
            
            service = service_match.group(1) if service_match else None
            keys = keys_match.group(1).split(',') if keys_match else []
            
            return service, [k.strip() for k in keys]
            
        except Exception as e:
            logging.error(f"Error parsing task credentials: {e}")
            return None, []
    
    def inject_credentials(self, command, task_path):
        """Inject credentials into command"""
        if not self.keys_file:
            return command
        
        try:
            # Get credentials from task
            service, keys = self.parse_task_credentials(task_path)
            
            if not service or not keys:
                return command
            
            # Read keys file
            with open(self.keys_file) as f:
                content = f.read()
            
            # Find service section
            section_match = re.search(
                rf'\[{service}\](.*?)(?=\[|$)',
                content,
                re.DOTALL
            )
            if not section_match:
                return command
            
            section = section_match.group(1)
            
            # Replace keys in command
            modified_cmd = command
            for key in keys:
                key = key.strip()
                key_match = re.search(rf'{key}=(.*)', section)
                if key_match:
                    value = key_match.group(1).strip()
                    modified_cmd = modified_cmd.replace(f'${key}', value)
            
            return modified_cmd
            
        except Exception as e:
            logging.error(f"Error injecting credentials: {e}")
            return command
