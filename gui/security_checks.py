import tkinter as tk
from tkinter import ttk, messagebox

class SecurityChecks(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Security Checks")
        
        # Default security checks
        self.DEFAULT_CHECKS = [
            "Production safeguards active",
            "Backup systems verified", 
            "Staging environment tested",
            "Access controls verified",
            "Cost limits configured",
            "Monitoring systems active",
            "Rollback plan tested",
            "Documentation updated"
        ]
        
        # State
        self.check_vars = {}
        self.custom_checks = []
        
        # Create scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.checks_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas
        canvas.create_window((0, 0), window=self.checks_frame, anchor="nw")
        
        # Add default checks
        for check in self.DEFAULT_CHECKS:
            self.add_check(check)
        
        # Add custom check input
        custom_frame = ttk.Frame(self.checks_frame)
        custom_frame.pack(fill='x', padx=5, pady=2)
        
        self.custom_entry = ttk.Entry(custom_frame)
        self.custom_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        ttk.Button(
            custom_frame,
            text="Add Check",
            command=self.add_custom_check
        ).pack(side='right', padx=5)
        
        # Update scroll region when frame changes
        self.checks_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def add_check(self, check_text):
        """Add a security check"""
        var = tk.BooleanVar()
        self.check_vars[check_text] = var
        
        frame = ttk.Frame(self.checks_frame)
        frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Checkbutton(
            frame,
            text=check_text,
            variable=var
        ).pack(side='left')
        
        if check_text not in self.DEFAULT_CHECKS:
            ttk.Button(
                frame,
                text="Remove",
                command=lambda: self.remove_check(check_text, frame)
            ).pack(side='right')
    
    def add_custom_check(self):
        """Add custom security check"""
        check_text = self.custom_entry.get().strip()
        if not check_text:
            return
            
        if check_text in self.check_vars:
            messagebox.showwarning("Warning", "This check already exists")
            return
        
        self.add_check(check_text)
        self.custom_checks.append(check_text)
        self.custom_entry.delete(0, tk.END)
    
    def remove_check(self, check_text, frame):
        """Remove a custom check"""
        if check_text in self.check_vars:
            del self.check_vars[check_text]
        if check_text in self.custom_checks:
            self.custom_checks.remove(check_text)
        frame.destroy()
    
    def verify_checks(self):
        """Verify security checks"""
        unchecked = [
            check for check, var in self.check_vars.items()
            if not var.get()
        ]
        
        if unchecked:
            return messagebox.askyesno(
                "Security Checks",
                f"The following security checks are not complete:\n" +
                "\n".join(f"- {check}" for check in unchecked) +
                "\n\nDo you want to proceed anyway?"
            )
        
        return True
    
    def get_active_checks(self):
        """Get list of active security checks"""
        return [
            check for check, var in self.check_vars.items()
            if var.get()
        ]
    
    def get_all_checks(self):
        """Get all security checks"""
        return list(self.check_vars.keys())
