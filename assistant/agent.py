import os
import json
import logging
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from .search import ResearchManager, SearchResult
from .computer import ComputerController, ScreenAnalyzer, UIElement

@dataclass
class Task:
    """Represents a task to be performed"""
    description: str
    context: Optional[str]
    timestamp: str
    completed: bool = False
    result: Optional[str] = None

class MacAssistant:
    """AI-powered Mac OS assistant"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.research = ResearchManager()
        self.computer = ComputerController()
        self.screen = ScreenAnalyzer()
        
        # Task history
        self.history: List[Task] = []
        
        # Cache directory
        self.cache_dir = os.path.expanduser('~/.mac-assistant/cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load task history
        self._load_history()
    
    def _load_history(self):
        """Load task history from cache"""
        history_path = os.path.join(self.cache_dir, 'task_history.json')
        if os.path.exists(history_path):
            try:
                with open(history_path) as f:
                    data = json.load(f)
                    self.history = [Task(**task) for task in data]
            except Exception as e:
                self.logger.error(f"Error loading history: {e}")
    
    def _save_history(self):
        """Save task history to cache"""
        history_path = os.path.join(self.cache_dir, 'task_history.json')
        try:
            with open(history_path, 'w') as f:
                json.dump([task.__dict__ for task in self.history], f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    async def analyze_task(self, description: str) -> Dict[str, Any]:
        """Analyze task to determine required actions"""
        # Research how to accomplish task
        result = await self.research.research(
            f"How to automate on Mac OS: {description}",
            context="Need to perform task using Python, pyautogui, and system control"
        )
        
        # Extract key information
        analysis = {
            'description': description,
            'requires_browser': any(word in description.lower() 
                                  for word in ['chrome', 'safari', 'web', 'browser']),
            'requires_keyboard': any(word in description.lower() 
                                   for word in ['type', 'enter', 'input']),
            'requires_mouse': any(word in description.lower() 
                                for word in ['click', 'select', 'choose']),
            'target_app': self._detect_target_app(description),
            'research_result': result.response
        }
        
        return analysis
    
    def _detect_target_app(self, description: str) -> Optional[str]:
        """Detect target application from description"""
        apps = {
            'chrome': ['chrome', 'google', 'browser'],
            'safari': ['safari', 'browser'],
            'vscode': ['vscode', 'code', 'editor'],
            'terminal': ['terminal', 'command', 'shell'],
            'slack': ['slack', 'chat'],
            'gmail': ['gmail', 'email', 'mail']
        }
        
        description = description.lower()
        for app, keywords in apps.items():
            if any(word in description for word in keywords):
                return app
        
        return None
    
    async def execute_task(self, description: str, context: Optional[str] = None) -> str:
        """Execute a task based on description"""
        # Create task record
        task = Task(
            description=description,
            context=context,
            timestamp=datetime.now().isoformat()
        )
        
        try:
            # Analyze task
            analysis = await self.analyze_task(description)
            
            # Perform task based on analysis
            if analysis['requires_browser']:
                result = await self._handle_browser_task(analysis)
            elif analysis['target_app']:
                result = await self._handle_app_task(analysis)
            else:
                result = await self._handle_system_task(analysis)
            
            # Update task record
            task.completed = True
            task.result = result
            
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            task.result = f"Error: {str(e)}"
        
        # Save to history
        self.history.append(task)
        self._save_history()
        
        return task.result if task.result else "Task failed"
    
    async def _handle_browser_task(self, analysis: Dict[str, Any]) -> str:
        """Handle browser-based task"""
        # Find browser window
        browser = self.screen.find_element_by_text(
            analysis['target_app'] or 'chrome',
            partial=True
        )
        
        if browser:
            # Click browser window
            self.computer.click_element(browser)
            
            # Perform browser actions based on analysis
            if analysis['requires_keyboard']:
                self.computer.type_text(analysis['description'])
            
            return "Browser task completed"
        else:
            return "Browser window not found"
    
    async def _handle_app_task(self, analysis: Dict[str, Any]) -> str:
        """Handle application-specific task"""
        # Research app-specific automation
        result = await self.research.research(
            f"How to automate {analysis['target_app']} on Mac: {analysis['description']}",
            context=f"Need to control {analysis['target_app']} application"
        )
        
        # Find and activate app window
        app = self.screen.find_element_by_text(analysis['target_app'], partial=True)
        if app:
            self.computer.click_element(app)
            
            # Perform app-specific actions
            if analysis['requires_keyboard']:
                self.computer.type_text(analysis['description'])
            
            return f"{analysis['target_app']} task completed"
        else:
            return f"{analysis['target_app']} window not found"
    
    async def _handle_system_task(self, analysis: Dict[str, Any]) -> str:
        """Handle system-level task"""
        # Research system automation
        result = await self.research.research(
            f"How to automate system task on Mac: {analysis['description']}",
            context="Need to perform system-level automation"
        )
        
        # Perform system actions based on analysis
        if analysis['requires_keyboard']:
            self.computer.type_text(analysis['description'])
        
        return "System task completed"
    
    def get_history(self, limit: Optional[int] = None) -> List[Task]:
        """Get task history"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """Clear task history"""
        self.history.clear()
        self._save_history()

# Example usage:
"""
async def main():
    assistant = MacAssistant()
    
    # Execute a task
    result = await assistant.execute_task(
        "Open Chrome and search for Python automation",
        context="Need to research automation techniques"
    )
    print(result)
    
    # Check history
    history = assistant.get_history(limit=5)
    for task in history:
        print(f"{task.timestamp}: {task.description} - {'Success' if task.completed else 'Failed'}")

if __name__ == '__main__':
    asyncio.run(main())
"""
