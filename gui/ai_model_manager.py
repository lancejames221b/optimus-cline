import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from typing import Optional, Dict, Any
from .ai_models import AIModelManager, ModelCapability, TaskRequirement, BudgetError

class AIModelManagerGUI(ttk.Frame):
    """GUI for managing AI models and usage"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize AI manager
        self.ai_manager = None
        self.current_project = None
        
        # Create main layout
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the GUI elements"""
        # Create main layout
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Configuration
        config_frame = ttk.LabelFrame(main_frame, text="AI Configuration")
        config_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # API Key
        key_frame = ttk.Frame(config_frame)
        key_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(key_frame, text="OpenRouter API Key:").pack(side='left')
        self.api_key = ttk.Entry(key_frame, show="*")
        self.api_key.pack(side='left', fill='x', expand=True, padx=5)
        
        ttk.Button(
            key_frame,
            text="Save",
            command=self._save_api_key
        ).pack(side='right')
        
        # Budget
        budget_frame = ttk.LabelFrame(config_frame, text="Budget Management")
        budget_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(budget_frame, text="Monthly Budget ($):").pack(side='left')
        self.budget_var = tk.StringVar(value="0.00")
        self.budget_entry = ttk.Entry(
            budget_frame,
            textvariable=self.budget_var
        )
        self.budget_entry.pack(side='left', padx=5)
        
        ttk.Button(
            budget_frame,
            text="Set Budget",
            command=self._set_budget
        ).pack(side='right', padx=5)
        
        # Model Selection
        model_frame = ttk.LabelFrame(config_frame, text="Model Selection")
        model_frame.pack(fill='x', padx=5, pady=5)
        
        # Default model
        default_frame = ttk.Frame(model_frame)
        default_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(default_frame, text="Default Model:").pack(side='left')
        self.default_model = ttk.Combobox(
            default_frame,
            values=['claude-3-sonnet', 'gpt-4', 'gemini-pro-1.5'],
            state='readonly'
        )
        self.default_model.set('claude-3-sonnet')
        self.default_model.pack(side='left', padx=5)
        
        # Cost threshold
        threshold_frame = ttk.Frame(model_frame)
        threshold_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(threshold_frame, text="Cost Alert Threshold ($):").pack(side='left')
        self.threshold_var = tk.StringVar(value="1.00")
        self.threshold_entry = ttk.Entry(
            threshold_frame,
            textvariable=self.threshold_var
        )
        self.threshold_entry.pack(side='left', padx=5)
        
        # Right side - Usage Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Usage Statistics")
        stats_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Usage overview
        overview_frame = ttk.Frame(stats_frame)
        overview_frame.pack(fill='x', padx=5, pady=5)
        
        self.usage_label = ttk.Label(
            overview_frame,
            text="Current Usage: $0.00 / $0.00"
        )
        self.usage_label.pack(side='left')
        
        ttk.Button(
            overview_frame,
            text="Refresh",
            command=self._refresh_stats
        ).pack(side='right')
        
        # Usage history
        self.usage_tree = ttk.Treeview(
            stats_frame,
            columns=('Time', 'Model', 'Tokens', 'Cost'),
            show='headings'
        )
        self.usage_tree.heading('Time', text='Time')
        self.usage_tree.heading('Model', text='Model')
        self.usage_tree.heading('Tokens', text='Tokens')
        self.usage_tree.heading('Cost', text='Cost')
        self.usage_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            stats_frame,
            orient='vertical',
            command=self.usage_tree.yview
        )
        scrollbar.pack(side='right', fill='y')
        self.usage_tree.configure(yscrollcommand=scrollbar.set)
    
    def _save_api_key(self):
        """Save OpenRouter API key"""
        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showwarning("Warning", "Please enter an API key")
            return
        
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        try:
            # Save to project config
            config_dir = os.path.join(self.current_project['path'], '.cline')
            os.makedirs(config_dir, exist_ok=True)
            
            config_path = os.path.join(config_dir, 'ai_config.json')
            
            # Load existing config or create new
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update config
            config['openrouter_key'] = api_key
            
            # Save config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Initialize AI manager
            self.ai_manager = AIModelManager(api_key)
            
            messagebox.showinfo("Success", "API key saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {e}")
    
    def _set_budget(self):
        """Set monthly budget"""
        try:
            budget = float(self.budget_var.get())
            if budget <= 0:
                raise ValueError("Budget must be positive")
            
            if not self.ai_manager:
                messagebox.showwarning(
                    "Warning",
                    "Please configure API key first"
                )
                return
            
            if not self.current_project:
                messagebox.showwarning(
                    "Warning",
                    "Please select a project first"
                )
                return
            
            # Set budget
            self.ai_manager.cost_tracker.set_project_budget(
                self.current_project['path'],
                budget
            )
            
            # Save to config
            config_dir = os.path.join(self.current_project['path'], '.cline')
            config_path = os.path.join(config_dir, 'ai_config.json')
            
            with open(config_path) as f:
                config = json.load(f)
            
            config['monthly_budget'] = budget
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self._refresh_stats()
            messagebox.showinfo("Success", "Budget set successfully")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid budget: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set budget: {e}")
    
    def _refresh_stats(self):
        """Refresh usage statistics"""
        if not self.ai_manager or not self.current_project:
            return
        
        # Clear tree
        for item in self.usage_tree.get_children():
            self.usage_tree.delete(item)
        
        # Get usage history
        history = self.ai_manager.cost_tracker.usage_history
        project_history = [
            entry for entry in history
            if entry['project_id'] == self.current_project['path']
        ]
        
        # Update tree
        for entry in project_history:
            self.usage_tree.insert(
                '',
                'end',
                values=(
                    entry['timestamp'],
                    entry['model'],
                    entry['tokens'],
                    f"${entry['cost']:.4f}"
                )
            )
        
        # Update usage label
        usage = self.ai_manager.cost_tracker.get_usage(
            self.current_project['path']
        )
        budget = self.ai_manager.cost_tracker.project_budgets.get(
            self.current_project['path'],
            0
        )
        self.usage_label.config(
            text=f"Current Usage: ${usage:.2f} / ${budget:.2f}"
        )
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
        
        if project:
            # Load config
            config_path = os.path.join(
                project['path'],
                '.cline',
                'ai_config.json'
            )
            
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
                
                # Set API key
                if 'openrouter_key' in config:
                    self.api_key.delete(0, tk.END)
                    self.api_key.insert(0, config['openrouter_key'])
                    self.ai_manager = AIModelManager(config['openrouter_key'])
                
                # Set budget
                if 'monthly_budget' in config:
                    self.budget_var.set(str(config['monthly_budget']))
                    if self.ai_manager:
                        self.ai_manager.cost_tracker.set_project_budget(
                            project['path'],
                            config['monthly_budget']
                        )
            
            self._refresh_stats()
