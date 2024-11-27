import os
import json
import logging
import asyncio
import subprocess
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from .search import ResearchManager, SearchResult

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
            f"Analyze this task: '{description}'. Respond with a JSON object containing: "
            "1. type: The type of task ('app_launch', 'web_search', 'system_command', or 'general_query') "
            "2. action: For app_launch: the terminal command (e.g. 'open -a \"Google Chrome\"'), "
            "          For web_search: the search URL, "
            "          For system_command: the command to run, "
            "          For general_query: leave empty "
            "3. response: A natural response to the query (required for general_query, optional for others) "
            "4. confidence: A number 0-1 indicating confidence in understanding the task "
            "Format the response as valid JSON with these exact fields.",
            context="Need to understand user intent and determine appropriate action"
        )
        
        try:
            # Extract JSON from response
            response_text = result.response
            # Find JSON block between ```json and ```
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            else:
                # Try to find a JSON block between any ``` markers
                if "```" in response_text:
                    json_text = response_text.split("```")[1].strip()
                else:
                    # Try to parse the whole response as JSON
                    json_text = response_text.strip()
            
            # Parse JSON
            task_info = json.loads(json_text)
            
            # Add original description
            task_info['description'] = description
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Failed to parse task info: {e}")
            # Get a general response instead
            result = await self.research.research(
                description,
                context="Provide a helpful response to the user's request"
            )
            return {
                'description': description,
                'type': 'general_query',
                'action': None,
                'response': result.response,
                'confidence': 0.8  # High confidence in providing a general response
            }
    
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
            
            if analysis.get('confidence', 0) > 0.7:
                task_type = analysis.get('type', 'general_query')
                
                if task_type == 'app_launch' and analysis.get('action'):
                    try:
                        subprocess.run(analysis['action'], shell=True, check=True)
                        result = f"Launched the application"
                    except subprocess.CalledProcessError as e:
                        self.logger.error(f"Command failed: {e}")
                        result = f"Failed to launch application: {e}"
                
                elif task_type == 'system_command' and analysis.get('action'):
                    try:
                        subprocess.run(analysis['action'], shell=True, check=True)
                        result = "Command executed successfully"
                    except subprocess.CalledProcessError as e:
                        self.logger.error(f"Command failed: {e}")
                        result = f"Command failed: {e}"
                
                elif task_type == 'web_search' and analysis.get('action'):
                    try:
                        subprocess.run(f'open "{analysis["action"]}"', shell=True, check=True)
                        result = "Opened search results in your browser"
                    except subprocess.CalledProcessError as e:
                        self.logger.error(f"Failed to open browser: {e}")
                        result = f"Failed to open browser: {e}"
                
                else:  # general_query or no action specified
                    result = analysis.get('response', "I understand your request but I'm not sure how to help. Could you be more specific?")
            
            else:
                result = analysis.get('response', "I'm not sure how to help with that. Could you rephrase your request?")
            
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
    
    def get_history(self, limit: Optional[int] = None) -> List[Task]:
        """Get task history"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """Clear task history"""
        self.history.clear()
        self._save_history()
