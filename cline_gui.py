#!/usr/bin/env python3
[Previous content remains the same until automate_vscode_approval method...]

    def select_project(self):
        """Select project directory"""
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
            
            # Refresh UI
            self.refresh_tasks()
            self.load_command_history()
    
    def refresh_tasks(self):
        """Refresh tasks list"""
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
    
    def load_command_history(self):
        """Load command history"""
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
    
    def process_commands(self):
        """Process commands in queue"""
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
        """Process output in queue"""
        try:
            while True:
                output = self.output_queue.get_nowait()
                self.output_text.insert(tk.END, output)
                self.output_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_output)
    
    def add_to_history(self, cmd, start_time, status, duration):
        """Add command to history"""
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

if __name__ == '__main__':
    root = tk.Tk()
    app = ClineGUI(root)
    root.mainloop()
