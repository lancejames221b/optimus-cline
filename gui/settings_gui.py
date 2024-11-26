import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from .settings_manager import settings

class SettingsGUI(ttk.Frame):
    """GUI for managing global settings"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create main layout
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the GUI elements"""
        # Create main layout
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # API Keys section
        keys_frame = ttk.LabelFrame(main_frame, text="API Keys")
        keys_frame.pack(fill='x', padx=5, pady=5)
        
        # OpenRouter key
        openrouter_frame = ttk.Frame(keys_frame)
        openrouter_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(openrouter_frame, text="OpenRouter API Key:").pack(side='left')
        self.openrouter_key = ttk.Entry(openrouter_frame, show="*")
        self.openrouter_key.pack(side='left', fill='x', expand=True, padx=5)
        
        if settings.get_api_key('OPENROUTER_API_KEY'):
            self.openrouter_key.insert(0, settings.get_api_key('OPENROUTER_API_KEY'))
        
        ttk.Button(
            openrouter_frame,
            text="Save",
            command=lambda: self._save_api_key('OPENROUTER_API_KEY', self.openrouter_key.get())
        ).pack(side='right')
        
        # Claude key
        claude_frame = ttk.Frame(keys_frame)
        claude_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(claude_frame, text="Claude API Key:").pack(side='left')
        self.claude_key = ttk.Entry(claude_frame, show="*")
        self.claude_key.pack(side='left', fill='x', expand=True, padx=5)
        
        if settings.get_api_key('CLAUDE_API_KEY'):
            self.claude_key.insert(0, settings.get_api_key('CLAUDE_API_KEY'))
        
        ttk.Button(
            claude_frame,
            text="Save",
            command=lambda: self._save_api_key('CLAUDE_API_KEY', self.claude_key.get())
        ).pack(side='right')
        
        # Perplexity key
        perplexity_frame = ttk.Frame(keys_frame)
        perplexity_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(perplexity_frame, text="Perplexity API Key:").pack(side='left')
        self.perplexity_key = ttk.Entry(perplexity_frame, show="*")
        self.perplexity_key.pack(side='left', fill='x', expand=True, padx=5)
        
        if settings.get_api_key('PERPLEXITY_API_KEY'):
            self.perplexity_key.insert(0, settings.get_api_key('PERPLEXITY_API_KEY'))
        
        ttk.Button(
            perplexity_frame,
            text="Save",
            command=lambda: self._save_api_key('PERPLEXITY_API_KEY', self.perplexity_key.get())
        ).pack(side='right')
        
        # General Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="General Settings")
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        # Default model
        model_frame = ttk.Frame(settings_frame)
        model_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(model_frame, text="Default Search Model:").pack(side='left')
        self.default_model = ttk.Combobox(
            model_frame,
            values=['small', 'large', 'huge'],
            state='readonly'
        )
        self.default_model.set(settings.get_setting('default_model', 'small'))
        self.default_model.pack(side='left', padx=5)
        
        ttk.Button(
            model_frame,
            text="Save",
            command=lambda: self._save_setting('default_model', self.default_model.get())
        ).pack(side='right')
        
        # Cache settings
        cache_frame = ttk.Frame(settings_frame)
        cache_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(cache_frame, text="Cache Duration (hours):").pack(side='left')
        self.cache_duration = ttk.Entry(cache_frame)
        self.cache_duration.insert(0, str(settings.get_setting('cache_duration', 24)))
        self.cache_duration.pack(side='left', padx=5)
        
        ttk.Button(
            cache_frame,
            text="Save",
            command=lambda: self._save_setting('cache_duration', int(self.cache_duration.get()))
        ).pack(side='right')
        
        # Budget settings
        budget_frame = ttk.Frame(settings_frame)
        budget_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(budget_frame, text="Monthly Budget ($):").pack(side='left')
        self.monthly_budget = ttk.Entry(budget_frame)
        self.monthly_budget.insert(0, str(settings.get_setting('monthly_budget', 10.0)))
        self.monthly_budget.pack(side='left', padx=5)
        
        ttk.Button(
            budget_frame,
            text="Save",
            command=lambda: self._save_setting('monthly_budget', float(self.monthly_budget.get()))
        ).pack(side='right')
    
    def _save_api_key(self, key: str, value: str):
        """Save API key"""
        if not value.strip():
            messagebox.showwarning("Warning", "Please enter an API key")
            return
        
        try:
            settings.set_api_key(key, value.strip())
            messagebox.showinfo("Success", f"{key} saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save {key}: {e}")
    
    def _save_setting(self, key: str, value: Any):
        """Save setting"""
        try:
            settings.set_setting(key, value)
            messagebox.showinfo("Success", f"Setting '{key}' saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save setting: {e}")
    
    def refresh(self):
        """Refresh displayed values"""
        # Update API keys
        self.openrouter_key.delete(0, tk.END)
        self.claude_key.delete(0, tk.END)
        self.perplexity_key.delete(0, tk.END)
        
        if settings.get_api_key('OPENROUTER_API_KEY'):
            self.openrouter_key.insert(0, settings.get_api_key('OPENROUTER_API_KEY'))
        if settings.get_api_key('CLAUDE_API_KEY'):
            self.claude_key.insert(0, settings.get_api_key('CLAUDE_API_KEY'))
        if settings.get_api_key('PERPLEXITY_API_KEY'):
            self.perplexity_key.insert(0, settings.get_api_key('PERPLEXITY_API_KEY'))
        
        # Update settings
        self.default_model.set(settings.get_setting('default_model', 'small'))
        
        self.cache_duration.delete(0, tk.END)
        self.cache_duration.insert(0, str(settings.get_setting('cache_duration', 24)))
        
        self.monthly_budget.delete(0, tk.END)
        self.monthly_budget.insert(0, str(settings.get_setting('monthly_budget', 10.0)))
