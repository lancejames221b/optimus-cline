import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from .search_engine import SearchManager, SearchModel, SearchResult

class SearchManagerGUI(ttk.Frame):
    """GUI for managing intelligent search"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize search manager
        self.search_manager = SearchManager()
        self.current_project = None
        
        # Create event loop for async operations
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Create main layout
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the GUI elements"""
        # Create main layout
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Search
        search_frame = ttk.LabelFrame(main_frame, text="Intelligent Search")
        search_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Search input
        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(input_frame, text="Search Query:").pack(side='left')
        self.search_entry = ttk.Entry(input_frame)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Model selection
        model_frame = ttk.Frame(search_frame)
        model_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(model_frame, text="Model:").pack(side='left')
        self.model_var = tk.StringVar(value='auto')
        model_select = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=['auto', 'small', 'large', 'huge'],
            state='readonly'
        )
        model_select.pack(side='left', padx=5)
        
        # Context input
        context_frame = ttk.Frame(search_frame)
        context_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(context_frame, text="Context:").pack(anchor='w')
        self.context_text = tk.Text(context_frame, height=4)
        self.context_text.pack(fill='x', pady=2)
        
        # Search button
        ttk.Button(
            search_frame,
            text="Search",
            command=self._perform_search
        ).pack(pady=5)
        
        # Search result
        result_frame = ttk.LabelFrame(search_frame, text="Result")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.result_text = tk.Text(
            result_frame,
            wrap='word',
            height=10,
            state='disabled'
        )
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Right side - History
        history_frame = ttk.LabelFrame(main_frame, text="Search History")
        history_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Cost overview
        cost_frame = ttk.Frame(history_frame)
        cost_frame.pack(fill='x', padx=5, pady=5)
        
        self.cost_label = ttk.Label(
            cost_frame,
            text="Total Cost: $0.00"
        )
        self.cost_label.pack(side='left')
        
        ttk.Button(
            cost_frame,
            text="Clear History",
            command=self._clear_history
        ).pack(side='right')
        
        # History list
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=('Time', 'Query', 'Model', 'Cost'),
            show='headings'
        )
        self.history_tree.heading('Time', text='Time')
        self.history_tree.heading('Query', text='Query')
        self.history_tree.heading('Model', text='Model')
        self.history_tree.heading('Cost', text='Cost')
        self.history_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            history_frame,
            orient='vertical',
            command=self.history_tree.yview
        )
        scrollbar.pack(side='right', fill='y')
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind history selection
        self.history_tree.bind('<<TreeviewSelect>>', self._show_history_result)
    
    def _get_model(self) -> Optional[SearchModel]:
        """Get selected model or None for auto"""
        model_map = {
            'small': SearchModel.SMALL,
            'large': SearchModel.LARGE,
            'huge': SearchModel.HUGE
        }
        selection = self.model_var.get()
        return model_map.get(selection)
    
    def _perform_search(self):
        """Perform search query"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        context = self.context_text.get('1.0', 'end').strip()
        if not context:
            context = None
        
        # Run async search in background
        async def do_search():
            try:
                result = await self.search_manager.search(
                    query,
                    context=context,
                    force_model=self._get_model()
                )
                
                # Update result display
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', 'end')
                self.result_text.insert('1.0', result.response)
                self.result_text.config(state='disabled')
                
                # Update history
                self.history_tree.insert(
                    '',
                    0,
                    values=(
                        datetime.fromisoformat(result.timestamp).strftime('%H:%M:%S'),
                        result.query[:50] + '...' if len(result.query) > 50 else result.query,
                        result.model.value.split('-')[0],
                        f"${result.cost:.4f}"
                    )
                )
                
                # Update cost
                self.cost_label.config(
                    text=f"Total Cost: ${self.search_manager.total_cost:.4f}"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Search failed: {e}")
        
        # Run async search
        self.loop.run_until_complete(do_search())
    
    def _show_history_result(self, event):
        """Show selected history result"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        # Get result from history
        index = self.history_tree.index(selection[0])
        result = self.search_manager.get_history()[-index-1]
        
        # Update display
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', 'end')
        self.result_text.insert('1.0', result.response)
        self.result_text.config(state='disabled')
    
    def _clear_history(self):
        """Clear search history"""
        if messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to clear the search history?"
        ):
            # Clear history
            self.search_manager.clear_history()
            
            # Clear displays
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            self.result_text.config(state='normal')
            self.result_text.delete('1.0', 'end')
            self.result_text.config(state='disabled')
            
            self.cost_label.config(text="Total Cost: $0.00")
    
    def set_project(self, project):
        """Set current project"""
        self.current_project = project
