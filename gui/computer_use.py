import os
import logging
import subprocess
import pyautogui
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ResourceType(Enum):
    """Types of resources that can be accessed"""
    FILE = "file"
    APPLICATION = "application"
    BROWSER = "browser"
    NETWORK = "network"
    SYSTEM = "system"

class PermissionLevel(Enum):
    """Permission levels for resource access"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    FULL = "full"
    NONE = "none"

@dataclass
class ResourcePermission:
    """Permission configuration for a resource"""
    resource_type: ResourceType
    resource_path: str
    permission_level: PermissionLevel
    requires_approval: bool = True

@dataclass
class ComputerTask:
    """Represents a computer use task"""
    task_id: str
    task_type: str
    resource_type: ResourceType
    resource_path: str
    action: str
    parameters: Dict[str, Any]
    requires_approval: bool = True

class SecurityManager:
    """Manages security and permissions for computer use"""
    
    def __init__(self):
        self.permissions: Dict[str, ResourcePermission] = {}
        self.audit_log: List[Dict[str, Any]] = []
    
    def check_permission(self, task: ComputerTask) -> bool:
        """Check if task is allowed based on permissions"""
        resource_key = f"{task.resource_type.value}:{task.resource_path}"
        
        if resource_key not in self.permissions:
            logging.warning(f"No permission defined for {resource_key}")
            return False
        
        permission = self.permissions[resource_key]
        
        # Log attempt
        self.audit_log.append({
            "task_id": task.task_id,
            "resource": resource_key,
            "action": task.action,
            "timestamp": "now",  # TODO: Add proper timestamp
            "allowed": False  # Default to False, update if allowed
        })
        
        # Check permission level
        if permission.permission_level == PermissionLevel.NONE:
            return False
            
        if permission.permission_level == PermissionLevel.FULL:
            self.audit_log[-1]["allowed"] = True
            return True
            
        # Check specific permissions
        action_allowed = False
        if task.action == "read" and permission.permission_level in [PermissionLevel.READ, PermissionLevel.WRITE]:
            action_allowed = True
        elif task.action == "write" and permission.permission_level == PermissionLevel.WRITE:
            action_allowed = True
        elif task.action == "execute" and permission.permission_level == PermissionLevel.EXECUTE:
            action_allowed = True
            
        self.audit_log[-1]["allowed"] = action_allowed
        return action_allowed
    
    def add_permission(self, permission: ResourcePermission):
        """Add or update a permission"""
        resource_key = f"{permission.resource_type.value}:{permission.resource_path}"
        self.permissions[resource_key] = permission
        logging.info(f"Added permission for {resource_key}: {permission.permission_level.value}")

class FileSystemOperations:
    """Handles file system operations"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security = security_manager
    
    def read_file(self, path: str, task_id: str) -> Optional[str]:
        """Read contents of a file"""
        task = ComputerTask(
            task_id=task_id,
            task_type="file_read",
            resource_type=ResourceType.FILE,
            resource_path=path,
            action="read",
            parameters={"path": path}
        )
        
        if not self.security.check_permission(task):
            logging.warning(f"Permission denied to read file: {path}")
            return None
            
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading file {path}: {e}")
            return None
    
    def write_file(self, path: str, content: str, task_id: str) -> bool:
        """Write content to a file"""
        task = ComputerTask(
            task_id=task_id,
            task_type="file_write",
            resource_type=ResourceType.FILE,
            resource_path=path,
            action="write",
            parameters={"path": path, "content": content}
        )
        
        if not self.security.check_permission(task):
            logging.warning(f"Permission denied to write file: {path}")
            return False
            
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            logging.error(f"Error writing file {path}: {e}")
            return False
    
    def list_files(self, path: str, task_id: str) -> Optional[List[str]]:
        """List files in a directory"""
        task = ComputerTask(
            task_id=task_id,
            task_type="file_list",
            resource_type=ResourceType.FILE,
            resource_path=path,
            action="read",
            parameters={"path": path}
        )
        
        if not self.security.check_permission(task):
            logging.warning(f"Permission denied to list directory: {path}")
            return None
            
        try:
            return os.listdir(path)
        except Exception as e:
            logging.error(f"Error listing directory {path}: {e}")
            return None

class ApplicationControl:
    """Controls application interaction"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security = security_manager
    
    def launch_application(self, app_path: str, task_id: str) -> bool:
        """Launch an application"""
        task = ComputerTask(
            task_id=task_id,
            task_type="app_launch",
            resource_type=ResourceType.APPLICATION,
            resource_path=app_path,
            action="execute",
            parameters={"path": app_path}
        )
        
        if not self.security.check_permission(task):
            logging.warning(f"Permission denied to launch application: {app_path}")
            return False
            
        try:
            subprocess.Popen([app_path])
            return True
        except Exception as e:
            logging.error(f"Error launching application {app_path}: {e}")
            return False

class ComputerUse:
    """Main class for computer use capabilities"""
    
    def __init__(self):
        self.security = SecurityManager()
        self.file_system = FileSystemOperations(self.security)
        self.applications = ApplicationControl(self.security)
        
        # Set up initial permissions
        self._setup_default_permissions()
    
    def _setup_default_permissions(self):
        """Set up default permissions"""
        # Allow read access to current directory
        self.security.add_permission(ResourcePermission(
            resource_type=ResourceType.FILE,
            resource_path=os.getcwd(),
            permission_level=PermissionLevel.READ,
            requires_approval=True
        ))
    
    def execute_task(self, task: ComputerTask) -> Any:
        """Execute a computer use task"""
        try:
            if task.resource_type == ResourceType.FILE:
                if task.action == "read":
                    return self.file_system.read_file(task.resource_path, task.task_id)
                elif task.action == "write":
                    return self.file_system.write_file(
                        task.resource_path,
                        task.parameters["content"],
                        task.task_id
                    )
                elif task.action == "list":
                    return self.file_system.list_files(task.resource_path, task.task_id)
            
            elif task.resource_type == ResourceType.APPLICATION:
                if task.action == "launch":
                    return self.applications.launch_application(
                        task.resource_path,
                        task.task_id
                    )
            
            logging.warning(f"Unsupported task type: {task.resource_type} - {task.action}")
            return None
            
        except Exception as e:
            logging.error(f"Error executing task {task.task_id}: {e}")
            return None
