#!/usr/bin/env python3
import os
import sys
import logging
from .chat import main as chat_main

def setup_logging():
    """Set up logging configuration"""
    log_dir = os.path.expanduser('~/.mac-assistant/logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                os.path.join(log_dir, 'assistant.log')
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main entry point"""
    # Set up logging
    setup_logging()
    
    # Run chat interface
    chat_main()

if __name__ == '__main__':
    main()
