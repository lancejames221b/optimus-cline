#!/usr/bin/env python3
"""
Cline Chat Runner
----------------

Run the Cline chat interface with all components.
"""

import os
import asyncio
import logging
from chat_interface import ChatInterface
from key_manager import KeyManager

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cline_chat.log')
        ]
    )

def print_welcome():
    """Print welcome message"""
    print("""
╔══════════════════════════════════════╗
║           Cline Assistant            ║
╚══════════════════════════════════════╝

Commands:
  !command - Execute system command
  ?query   - Search for information
  'action' - Perform computer task
  quit     - Exit chat

Examples:
  !ls                     - List files
  ?python error handling  - Search for info
  open Chrome            - Launch browser
  create file test.txt   - Create new file

Type your message below:
""")

def check_keys():
    """Check API keys and print status"""
    key_manager = KeyManager()
    
    print("\nChecking API keys...")
    
    # Check OpenRouter
    if key_manager.has_key('OPENROUTER_API_KEY'):
        print("✓ OpenRouter API key found")
    else:
        print("✗ OpenRouter API key not found")
        print("  Add to .env file or keys.txt:")
        print("  OPENROUTER_API_KEY=your_key_here")
    
    # Check Perplexity
    if key_manager.has_key('PERPLEXITY_API_KEY'):
        print("✓ Perplexity API key found")
    else:
        print("✗ Perplexity API key not found")
        print("  Add to .env file or keys.txt:")
        print("  PERPLEXITY_API_KEY=your_key_here")
    
    # List key sources
    print("\nKey sources checked:")
    print("- Environment variables")
    print("- .env file")
    print("- ./keys.txt")
    print("- /Volumes/SeXternal/keys.txt")
    print("- ~/keys.txt")
    print("- @keys.txt")
    
    # Return if we have minimum required keys
    return (
        key_manager.has_key('OPENROUTER_API_KEY') or
        key_manager.has_key('PERPLEXITY_API_KEY')
    )

async def main():
    """Run chat interface"""
    try:
        # Set up
        setup_logging()
        
        # Check keys
        if not check_keys():
            print("\nNo API keys found. Some features will be limited.")
            response = input("Continue anyway? [y/N] ")
            if response.lower() != 'y':
                return
        
        # Print welcome
        print_welcome()
        
        # Create interface
        chat = ChatInterface()
        
        # Chat loop
        while True:
            try:
                # Get input
                message = input("\n> ")
                
                # Check for quit
                if message.lower() in ['quit', 'exit']:
                    break
                
                # Handle message
                response = await chat.handle_message(message)
                print(f"\n{response}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nError: {e}")
        
        print("\nGoodbye!")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
        raise

if __name__ == '__main__':
    # Run chat
    asyncio.run(main())
