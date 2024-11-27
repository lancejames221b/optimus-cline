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
        logging.basicConfig(level=logging.INFO)
        
        # Initialize assistant
        try:
            self.assistant = MacAssistant()
        except Exception as e:
            self.logger.error(f"Failed to initialize assistant: {e}")
            raise
        
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

Your AI-powered assistant for macOS. I can help you with:

🚀 Application Control
 • Launch and manage applications
 • Open specific files or folders
 • Control system settings

🔍 Information & Search
 • Answer questions about any topic
 • Search the web for information
 • Explain concepts and provide examples

💻 System Operations
 • Execute system commands
 • Manage files and directories
 • Handle common tasks

Available commands:
 • /help: Show help message
 • /history: Show task history
 • /clear: Clear task history
 • /quit: Exit assistant

Just tell me what you need in natural language!
"""
        self.console.print(Markdown(welcome))
    
    async def show_help(self, *args):
        """Show help message"""
        help_text = """# Mac Assistant Help

I can help you with various tasks. Here are some examples:

## Application Control
 • "Open Chrome"
 • "Launch Visual Studio Code"
 • "Start Spotify"
 • "Open my downloads folder"

## Information & Search
 • "What's the weather like today?"
 • "Tell me about quantum computing"
 • "How do I create a Python virtual environment?"
 • "Search for coffee shops near me"

## System Operations
 • "Show my IP address"
 • "Create a new folder called Projects"
 • "What's using my disk space?"
 • "Check system memory usage"

## Available Commands
 • /help: Show this help message
 • /history: Show task history
 • /clear: Clear task history
 • /quit: Exit assistant

Just ask your question or describe your task in natural language. I'll understand what you need and help you accomplish it!"""
        
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
            self.console.print("\n[bold blue]Processing your request...[/bold blue]")
            result = await self.assistant.execute_task(task)
            
            # Show result
            if result:
                self.console.print(Panel(
                    result,
                    title="Response",
                    border_style="green"
                ))
            
            return False  # Don't exit
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Task cancelled[/yellow]")
            return False
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            self.console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    async def run(self):
        """Run the chat interface"""
        try:
            self.show_welcome()
            
            while True:
                try:
                    # Get user input
                    task = await self.session.prompt_async(
                        HTML("<ansiyellow>ask></ansiyellow> ")
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
        
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            self.console.print(f"[red]Fatal error: {str(e)}[/red]")
        finally:
            # Clean up
            self.console.print("\n[yellow]Shutting down...[/yellow]")

def main():
    """Run the assistant"""
    chat = AssistantChat()
    asyncio.run(chat.run())
