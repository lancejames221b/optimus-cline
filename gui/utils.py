import os
import logging

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('.cline', exist_ok=True)
    logging.basicConfig(
        filename='.cline/automation.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def make_window_front(root):
    """Make window appear in front"""
    root.lift()  # Lift window to top
    root.attributes('-topmost', True)  # Keep on top
    root.after_idle(root.attributes, '-topmost', False)  # Disable topmost after showing
    root.focus_force()  # Focus window

def bind_window_events(root):
    """Bind common window events"""
    root.bind('<Command-w>', lambda e: root.withdraw())  # Hide window
    root.bind('<Command-q>', lambda e: root.quit())  # Quit app
    root.bind('<FocusIn>', lambda e: root.lift())  # Bring to front when focused
    root.bind('<Map>', lambda e: root.focus_force())  # Focus when shown/restored
