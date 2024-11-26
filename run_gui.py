#!/usr/bin/env python3
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the GUI
from gui import ClineApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = ClineApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
