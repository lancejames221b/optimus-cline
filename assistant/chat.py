import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from .agent import MacAssistant

class AssistantChat:
    """Terminal-based chat interface for Mac Assistant"""
    
    def __init__(self):
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize assistant
        self.assistant = MacAssistant()
        
        # Set up rich console
        self.console = Console()
        
        # Set up prompt session with history
        history_dir = os.path.expanduser('~/.mac-assistant/history')
        os.makedirs(history_dir, exist_ok=True)
        history_file = os.path.join(history_dir, 'chat_history')
        
        self.session = PromptSession(
            history=FileHistory(history_file),
            auto_suggest=AutoSuggestFromHistory()
        )
        
        # Command prefixes
        self.commands = {
            '/help': self.show_help,
            '/history': self.show_history,
            '/clear': self.clear_history,
            '/quit': self.quit
        }
    
    def show_welcome(self):
        """Show welcome message"""
        welcome = """# Mac Assistant

Your AI-powered automation assistant for macOS.

Available commands:
- /help: Show this help message
- /history: Show task history
- /clear: Clear task history
- /quit: Exit assistant

Type your task in natural language, for example:
- "Open Chrome and search for Python automation"
- "Check my Gmail for new messages"
- "Create a new document in VSCode"
"""
        self.console.print(Markdown(welcome))
    
    async def show_help(self, *args):
        """Show help message"""
        help_text = """# Available Commands

- /help: Show this help message
- /history: Show task history
- /clear: Clear task history
- /quit: Exit assistant

## Task Examples

1. Browser Tasks:
   - "Open Chrome and go to gmail.com"
   - "Search for Python automation tutorials"
   - "Check my calendar for today's events"

2. Application Tasks:
   - "Open VSCode and create a new file"
   - "Send a message in Slack"
   - "Check for new emails in Gmail"

3. System Tasks:
   - "Take a screenshot of the current window"
   - "Create a new folder on the desktop"
   - "Open Terminal and run updates"

The assistant will:
1. Analyze your task
2. Research how to accomplish it
3. Execute the necessary actions
4. Provide feedback on the results"""
        
        self.console.print(Markdown(help_text))
        return False  # Don't exit
    
    async def show_history(self, *args):
        """Show task history"""
        history = self.assistant.get_history()
        if not history:
            self.console.print("No task history available")
            return False
        
        self.console.print("\n[bold]Task History:[/bold]\n")
        for task in history:
            status = "[green]✓[/green]" if task.completed else "[red]✗[/red]"
            self.console.print(
                f"{status} {task.timestamp.split('T')[0]} - {task.description}"
            )
            if task.result:
                self.console.print(f"   Result: {task.result}\n")
        
        return False  # Don't exit
    
    async def clear_history(self, *args):
        """Clear task history"""
        self.assistant.clear_history()
        self.console.print("[green]Task history cleared[/green]")
        return False  # Don't exit
    
    async def quit(self, *args):
        """Exit the assistant"""
        self.console.print("[yellow]Goodbye![/yellow]")
        return True  # Exit
    
    async def handle_task(self, task: str) -> bool:
        """Handle user task"""
        try:
            # Check for commands
            if task.startswith('/'):
                command = task.split()[0]
                args = task.split()[1:]
                if command in self.commands:
                    return await self.commands[command](*args)
                else:
                    self.console.print(f"[red]Unknown command: {command}[/red]")
                    return False
            
            # Execute task
            self.console.print("\n[bold blue]Analyzing task...[/bold blue]")
            result = await self.assistant.execute_task(task)
            
            # Show result
            if result:
                self.console.print(Panel(
                    result,
                    title="Task Result",
                    border_style="green"
                ))
            
            return False  # Don't exit
            
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            self.console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    async def run(self):
        """Run the chat interface"""
        self.show_welcome()
        
        while True:
            try:
                # Get user input
                task = await self.session.prompt_async(
                    HTML("<ansiyellow>task></ansiyellow> ")
                )
                
                if not task.strip():
                    continue
                
                # Handle task
                should_exit = await self.handle_task(task.strip())
                if should_exit:
                    break
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.logger.error(f"Error: {e}")
                self.console.print(f"[red]Error: {str(e)}[/red]")

def main():
    """Run the assistant"""
    chat = AssistantChat()
    asyncio.run(chat.run())

if __name__ == '__main__':
    main()
