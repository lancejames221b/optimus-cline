import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import logging
from datetime import datetime

class ProjectManagement(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Project Management")
        
        # State
        self.current_project = None
        
        # Project selection
        select_frame = ttk.Frame(self)
        select_frame.pack(fill='x', padx=5, pady=5)
        
        self.project_label = ttk.Label(select_frame, text="No project selected")
        self.project_label.pack(side='left', padx=5)
        
        ttk.Button(select_frame, text="Select Project", command=self.select_project).pack(side='left', padx=5)
        ttk.Button(select_frame, text="New Project", command=self.new_project_dialog).pack(side='left', padx=5)
        
        # Project info
        info_frame = ttk.LabelFrame(self, text="Project Information")
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.info_text = ttk.Label(info_frame, text="Select a project to view details")
        self.info_text.pack(padx=5, pady=5)
        
        # Project settings
        settings_frame = ttk.LabelFrame(self, text="Project Settings")
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        # Keys file
        keys_frame = ttk.Frame(settings_frame)
        keys_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(keys_frame, text="Keys file:").pack(side='left')
        self.keys_label = ttk.Label(keys_frame, text="Not configured")
        self.keys_label.pack(side='left', padx=5)
        ttk.Button(keys_frame, text="Configure", command=self.configure_keys).pack(side='left', padx=5)
    
    def select_project(self):
        """Select an existing project directory"""
        dir_path = filedialog.askdirectory(title="Select Project Directory")
        if not dir_path:
            return
            
        self.set_project(dir_path)
    
    def new_project_dialog(self):
        """Create a new project"""
        dialog = tk.Toplevel(self)
        dialog.title("New Project")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Project name
        name_frame = ttk.LabelFrame(dialog, text="Project Name")
        name_frame.pack(fill='x', padx=5, pady=5)
        name_entry = ttk.Entry(name_frame)
        name_entry.pack(fill='x', padx=5, pady=5)
        
        # Project location
        loc_frame = ttk.LabelFrame(dialog, text="Location")
        loc_frame.pack(fill='x', padx=5, pady=5)
        loc_entry = ttk.Entry(loc_frame)
        loc_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        ttk.Button(
            loc_frame,
            text="Browse",
            command=lambda: loc_entry.insert(0, filedialog.askdirectory())
        ).pack(side='right', padx=5, pady=5)
        
        def create_project():
            name = name_entry.get().strip()
            location = loc_entry.get().strip()
            
            if not name or not location:
                messagebox.showwarning("Warning", "Please fill in all fields")
                return
            
            # Create project directory
            project_dir = os.path.join(location, name)
            try:
                os.makedirs(project_dir)
                os.makedirs(os.path.join(project_dir, '.cline'))
                os.makedirs(os.path.join(project_dir, '.cline', 'tasks'))
                
                # Create project config
                config = {
                    'name': name,
                    'created': datetime.now().isoformat(),
                    'settings': {
                        'keys_file': None
                    }
                }
                
                with open(os.path.join(project_dir, '.cline', 'project.json'), 'w') as f:
                    json.dump(config, f, indent=2)
                
                dialog.destroy()
                self.set_project(project_dir)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create project: {e}")
    
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Create", command=create_project).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='right')
    
    def set_project(self, project_dir):
        """Set the current project"""
        try:
            # Verify .cline directory exists
            cline_dir = os.path.join(project_dir, '.cline')
            if not os.path.exists(cline_dir):
                os.makedirs(cline_dir)
                os.makedirs(os.path.join(cline_dir, 'tasks'))
            
            # Load or create project config
            config_path = os.path.join(cline_dir, 'project.json')
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
            else:
                config = {
                    'name': os.path.basename(project_dir),
                    'created': datetime.now().isoformat(),
                    'settings': {
                        'keys_file': None
                    }
                }
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            
            # Update state
            self.current_project = {
                'path': project_dir,
                'config': config
            }
            
            # Update UI
            self.project_label.config(text=config['name'])
            self.info_text.config(
                text=f"Location: {project_dir}\n" +
                     f"Created: {config['created']}\n" +
                     f"Tasks: {len(os.listdir(os.path.join(cline_dir, 'tasks')))}"
            )
            
            if config['settings']['keys_file']:
                self.keys_label.config(text=os.path.basename(config['settings']['keys_file']))
            
            # Notify listeners
            self.event_generate('<<ProjectChanged>>')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")
            self.current_project = None
            self.project_label.config(text="No project selected")
            self.info_text.config(text="Select a project to view details")
            self.keys_label.config(text="Not configured")
    
    def configure_keys(self):
        """Configure the keys.txt file for the project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select keys.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return
        
        # Update config
        self.current_project['config']['settings']['keys_file'] = file_path
        
        # Save config
        config_path = os.path.join(self.current_project['path'], '.cline', 'project.json')
        with open(config_path, 'w') as f:
            json.dump(self.current_project['config'], f, indent=2)
        
        # Update UI
        self.keys_label.config(text=os.path.basename(file_path))
        
        # Notify listeners
        self.event_generate('<<KeysFileChanged>>')
