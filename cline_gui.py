#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from datetime import datetime
import subprocess
import threading
import queue
import logging

class ClineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cline")
        self.root.geometry("800x600")
        
        # Make window appear in front
        root.lift()  # Lift window to top
        root.attributes('-topmost', True)  # Keep on top
        root.after_idle(root.attributes, '-topmost', False)  # Disable topmost after showing
        
        # Focus window
        root.focus_force()
        
        # Setup logging
        os.makedirs('.cline', exist_ok=True)
        logging.basicConfig(
            filename='.cline/automation.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # VS Code commands
        self.VSCODE_COMMANDS = {
            'accept_change': 'git.acceptChange',
            'stage_change': 'git.stage',
            'revert_change': 'git.revertChange',
            'commit': 'git.commit',
            'push': 'git.push'
        }
        
        # Dangerous commands requiring confirmation
        self.DANGEROUS_COMMANDS = {
            'git.revertChange': 'Are you sure you want to revert this change?',
            'git.clean': 'Are you sure you want to clean the working directory?',
            'git.reset': 'Are you sure you want to reset?'
        }
        
        # State
        self.current_project = None
        self.keys_file = None
        self.command_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
        # Main layout
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill='both')
        
        # Project selection frame at top
        project_frame = ttk.LabelFrame(self.main_frame, text="Project")
        project_frame.pack(fill='x', padx=10, pady=5)
        
        self.project_label = ttk.Label(project_frame, text="No project selected")
        self.project_label.pack(side='left', padx=5, pady=5)
        ttk.Button(project_frame, text="Select Project", command=self.select_project).pack(side='left', padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.tasks_frame = ttk.Frame(self.notebook)
        self.creds_frame = ttk.Frame(self.notebook)
        self.commands_frame = ttk.Frame(self.notebook)
        self.vscode_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_frame, text='Tasks')
        self.notebook.add(self.creds_frame, text='Credentials')
        self.notebook.add(self.commands_frame, text='Commands')
        self.notebook.add(self.vscode_frame, text='VS Code')
        
        # Setup UI
        self.setup_tasks_ui()
        self.setup_credentials_ui()
        self.setup_commands_ui()
        self.setup_vscode_ui()
        
        # Start command processing thread
        self.command_thread = threading.Thread(target=self.process_commands, daemon=True)
        self.command_thread.start()
        
        # Start output processing
        self.root.after(100, self.process_output)
        
        # Bind window activation
        root.bind('<FocusIn>', self.on_window_focus)
        root.bind('<Map>', self.on_window_map)  # Window shown/restored
        
        # Bind keyboard shortcuts
        root.bind('<Command-w>', lambda e: self.root.withdraw())  # Hide window
        root.bind('<Command-q>', lambda e: self.root.quit())  # Quit app
    
    def on_window_focus(self, event):
        """Handle window focus event"""
        self.root.lift()
    
    def on_window_map(self, event):
        """Handle window map event (shown/restored)"""
        self.root.lift()
        self.root.focus_force()
    
    def setup_vscode_ui(self):
        # Common actions
        actions_frame = ttk.LabelFrame(self.vscode_frame, text="Common Actions")
        actions_frame.pack(fill='x', padx=5, pady=5)
        
        # Create buttons for common actions
        for name, command in self.VSCODE_COMMANDS.items():
            btn_text = name.replace('_', ' ').title()
            ttk.Button(
                actions_frame,
                text=btn_text,
                command=lambda cmd=command: self.safe_execute_vscode(cmd)
            ).pack(side='left', padx=5, pady=5)
        
        # Custom command
        custom_frame = ttk.LabelFrame(self.vscode_frame, text="Custom Command")
        custom_frame.pack(fill='x', padx=5, pady=5)
        
        self.vscode_cmd_entry = ttk.Entry(custom_frame)
        self.vscode_cmd_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        ttk.Button(
            custom_frame,
            text="Execute",
            command=self.execute_custom_vscode
        ).pack(side='right', padx=5, pady=5)
        
        # Command history
        history_frame = ttk.LabelFrame(self.vscode_frame, text="Command History")
        history_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.vscode_history = ttk.Treeview(
            history_frame,
            columns=('Time', 'Command', 'Status'),
            show='headings'
        )
        self.vscode_history.heading('Time', text='Time')
        self.vscode_history.heading('Command', text='Command')
        self.vscode_history.heading('Status', text='Status')
        self.vscode_history.pack(fill='both', expand=True, pady=5)
        
        # Output area
        output_frame = ttk.LabelFrame(self.vscode_frame, text="Output")
        output_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.vscode_output = scrolledtext.ScrolledText(output_frame, height=6)
        self.vscode_output.pack(fill='both', expand=True, padx=5, pady=5)
    
    def safe_execute_vscode(self, command):
        """Execute VS Code command with safety checks"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        # Log attempt
        logging.info(f"Attempting VS Code command: {command}")
        
        # Check if command needs confirmation
        if command in self.DANGEROUS_COMMANDS:
            if not messagebox.askyesno(
                "Confirm Action",
                self.DANGEROUS_COMMANDS[command]
            ):
                logging.info(f"VS Code command cancelled: {command}")
                return
        
        try:
            # Execute command
            result = subprocess.run(
                ['code', '--command', command],
                capture_output=True,
                text=True
            )
            
            # Log result
            status = 'Success' if result.returncode == 0 else 'Failed'
            logging.info(f"VS Code command completed: {command} ({status})")
            
            # Add to history
            self.vscode_history.insert(
                '',
                0,
                values=(
                    datetime.now().strftime('%H:%M:%S'),
                    command,
                    status
                )
            )
            
            # Show output
            self.vscode_output.insert('end', f"\nCommand: {command}\n")
            if result.stdout:
                self.vscode_output.insert('end', result.stdout)
            if result.stderr:
                self.vscode_output.insert('end', f"Error: {result.stderr}\n")
            self.vscode_output.see('end')
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"VS Code command failed: {command} - {error_msg}")
            messagebox.showerror("Error", f"Failed to execute command: {error_msg}")
            self.vscode_output.insert('end', f"Error: {error_msg}\n")
            self.vscode_output.see('end')
    
    def execute_custom_vscode(self):
        """Execute custom VS Code command"""
        command = self.vscode_cmd_entry.get().strip()
        if not command:
            return
        
        self.vscode_cmd_entry.delete(0, tk.END)
        self.safe_execute_vscode(command)
    
    def setup_tasks_ui(self):
        # Tasks toolbar
        toolbar = ttk.Frame(self.tasks_frame)
        toolbar.pack(fill='x', pady=5)
        ttk.Button(toolbar, text="New Task", command=self.new_task_dialog).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Open", command=self.open_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Archive", command=self.archive_task).pack(side='left', padx=5)
        
        # Tasks list
        self.tasks_tree = ttk.Treeview(self.tasks_frame, columns=('Status',), show='tree headings')
        self.tasks_tree.heading('Status', text='Status')
        self.tasks_tree.pack(expand=True, fill='both', pady=5)
    
    def setup_credentials_ui(self):
        # Keys file frame
        keys_frame = ttk.Frame(self.creds_frame)
        keys_frame.pack(fill='x', pady=5)
        
        ttk.Label(keys_frame, text="Keys file:").pack(side='left')
        self.keys_label = ttk.Label(keys_frame, text="No file selected")
        self.keys_label.pack(side='left', padx=5)
        ttk.Button(keys_frame, text="Select File", command=self.select_keys_file).pack(side='left', padx=5)
        
        # Add credential frame
        cred_frame = ttk.LabelFrame(self.creds_frame, text="Add Credential")
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
        self.creds_tree = ttk.Treeview(self.creds_frame, columns=('Value',), show='tree headings')
        self.creds_tree.heading('Value', text='Value')
        self.creds_tree.pack(expand=True, fill='both', pady=5)
    
    def setup_commands_ui(self):
        # Command history
        history_frame = ttk.LabelFrame(self.commands_frame, text="Command History")
        history_frame.pack(fill='x', padx=5, pady=5)
        
        self.cmd_tree = ttk.Treeview(
            history_frame,
            columns=('Time', 'Status', 'Duration'),
            show='headings',
            height=6
        )
        self.cmd_tree.heading('Time', text='Time')
        self.cmd_tree.heading('Status', text='Status')
        self.cmd_tree.heading('Duration', text='Duration')
        self.cmd_tree.pack(fill='x', pady=5)
        
        # Command input
        input_frame = ttk.LabelFrame(self.commands_frame, text="Command")
        input_frame.pack(fill='x', padx=5, pady=5)
        
        self.cmd_entry = ttk.Entry(input_frame)
        self.cmd_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        ttk.Button(input_frame, text="Execute", command=self.execute_command).pack(side='right', padx=5, pady=5)
        
        # Command output
        output_frame = ttk.LabelFrame(self.commands_frame, text="Output")
        output_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD)
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def process_commands(self):
        while True:
            try:
                cmd = self.command_queue.get()
                if not cmd:
                    continue
                
                start_time = datetime.now()
                
                # Execute command
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Stream output
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.output_queue.put(output)
                
                # Get any remaining output
                stdout, stderr = process.communicate()
                if stdout:
                    self.output_queue.put(stdout)
                if stderr:
                    self.output_queue.put(f"Error: {stderr}")
                
                # Calculate duration
                duration = datetime.now() - start_time
                status = 'Success' if process.returncode == 0 else 'Failed'
                
                # Add to history
                self.root.after(0, self.add_to_history, cmd, start_time, status, duration)
                
            except Exception as e:
                self.output_queue.put(f"Error executing command: {str(e)}")
    
    def process_output(self):
        try:
            while True:
                output = self.output_queue.get_nowait()
                self.output_text.insert(tk.END, output)
                self.output_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_output)
    
    def execute_command(self):
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        
        self.cmd_entry.delete(0, tk.END)
        self.command_queue.put(cmd)
    
    def add_to_history(self, cmd, start_time, status, duration):
        self.cmd_tree.insert(
            '',
            0,
            values=(
                start_time.strftime('%H:%M:%S'),
                status,
                str(duration).split('.')[0]
            )
        )
        
        # Save to history file
        if self.current_project:
            history_file = os.path.join(self.current_project['config_dir'], 'command_history.json')
            try:
                if os.path.exists(history_file):
                    with open(history_file) as f:
                        history = json.load(f)
                else:
                    history = []
                
                history.insert(0, {
                    'command': cmd,
                    'timestamp': start_time.isoformat(),
                    'status': status,
                    'duration': str(duration)
                })
                
                with open(history_file, 'w') as f:
                    json.dump(history, f, indent=2)
            except Exception as e:
                print(f"Error saving command history: {e}")
    
    def select_project(self):
        dir_path = filedialog.askdirectory(title="Select Project Directory")
        if dir_path:
            self.current_project = {
                'path': dir_path,
                'name': os.path.basename(dir_path),
                'config_dir': os.path.join(dir_path, '.cline')
            }
            self.project_label.config(text=self.current_project['name'])
            
            # Create .cline directory if it doesn't exist
            os.makedirs(os.path.join(self.current_project['config_dir'], 'tasks'), exist_ok=True)
            
            self.refresh_tasks()
            self.load_command_history()
    
    def load_command_history(self):
        if not self.current_project:
            return
        
        # Clear current history
        for item in self.cmd_tree.get_children():
            self.cmd_tree.delete(item)
        
        # Load history from file
        history_file = os.path.join(self.current_project['config_dir'], 'command_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file) as f:
                    history = json.load(f)
                
                for cmd in history:
                    timestamp = datetime.fromisoformat(cmd['timestamp'])
                    self.cmd_tree.insert(
                        '',
                        'end',
                        values=(
                            timestamp.strftime('%H:%M:%S'),
                            cmd['status'],
                            cmd['duration']
                        )
                    )
            except Exception as e:
                print(f"Error loading command history: {e}")
    
    def new_task_dialog(self):
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("New Task")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Description
        desc_frame = ttk.LabelFrame(dialog, text="Description")
        desc_frame.pack(fill='x', padx=5, pady=5)
        desc_entry = ttk.Entry(desc_frame)
        desc_entry.pack(fill='x', padx=5, pady=5)
        
        # System Prompt
        prompt_frame = ttk.LabelFrame(dialog, text="System Prompt")
        prompt_frame.pack(fill='both', expand=True, padx=5, pady=5)
        prompt_text = scrolledtext.ScrolledText(prompt_frame, height=10)
        prompt_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        def create_task():
            desc = desc_entry.get().strip()
            prompt = prompt_text.get("1.0", "end-1c").strip()
            
            if not desc:
                messagebox.showwarning("Warning", "Please enter a description")
                return
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            task_id = f"task_{timestamp}_{desc.lower().replace(' ', '_')}"
            task_dir = os.path.join(self.current_project['config_dir'], 'tasks', task_id)
            os.makedirs(task_dir)
            
            # Create task.json
            task_data = {
                'id': task_id,
                'title': desc,
                'systemPrompt': prompt,
                'status': 'active',
                'created': datetime.now().isoformat()
            }
            with open(os.path.join(task_dir, 'task.json'), 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Create task.md
            with open(os.path.join(task_dir, 'task.md'), 'w') as f:
                f.write(f"# Task: {desc}\n")
                f.write(f"Date: {timestamp}\n\n")
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
    
    def refresh_tasks(self):
        if not self.current_project:
            return
        
        # Clear current items
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        
        # Load tasks
        tasks_dir = os.path.join(self.current_project['config_dir'], 'tasks')
        for task_id in os.listdir(tasks_dir):
            task_path = os.path.join(tasks_dir, task_id, 'task.json')
            if os.path.exists(task_path):
                with open(task_path) as f:
                    task = json.load(f)
                    self.tasks_tree.insert('', 'end', task['id'], text=task['title'], values=(task['status'],))
    
    def open_task(self):
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        task_id = selected[0]
        task_path = os.path.join(self.current_project['config_dir'], 'tasks', task_id, 'task.md')
        
        # Try to open with VS Code, fallback to default editor
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
        task_path = os.path.join(self.current_project['config_dir'], 'tasks', task_id, 'task.json')
        
        with open(task_path) as f:
            task = json.load(f)
        
        task['status'] = 'archived'
        
        with open(task_path, 'w') as f:
            json.dump(task, f, indent=2)
        
        self.refresh_tasks()
    
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

if __name__ == '__main__':
    root = tk.Tk()
    app = ClineGUI(root)
    root.mainloop()
