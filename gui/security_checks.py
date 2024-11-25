import tkinter as tk
from tkinter import ttk, messagebox

class SecurityChecks(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Security Checks")
        
        # Security checks
        self.SECURITY_CHECKS = [
            "Production safeguards active",
            "Backup systems verified", 
            "Staging environment tested",
            "Access controls verified",
            "Cost limits configured",
            "Monitoring systems active",
            "Rollback plan tested",
            "Documentation updated"
        ]
        
        self.check_vars = {}
        for check in self.SECURITY_CHECKS:
            var = tk.BooleanVar()
            self.check_vars[check] = var
            ttk.Checkbutton(
                self,
                text=check,
                variable=var
            ).pack(anchor='w', padx=5, pady=2)
    
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
