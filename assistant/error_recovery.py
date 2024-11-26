import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
from recovery_actions import RecoveryActions, RecoveryContext

@dataclass
class RecoveryAction:
    """Represents a recovery action"""
    action: str
    params: Dict[str, Any]
    timestamp: str

@dataclass
class RecoveryResult:
    """Represents a recovery result"""
    success: bool
    action: Optional[str] = None
    error: Optional[str] = None

class ErrorRecovery:
    """Handles error recovery strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Recovery actions
        self.actions = RecoveryActions()
        
        # Recovery strategies
        self.strategies: Dict[str, Callable[[Dict[str, Any]], RecoveryAction]] = {
            'browser_error': self._handle_browser_error,
            'tool_error': self._handle_tool_error,
            'extension_error': self._handle_extension_error,
            'system_error': self._handle_system_error
        }
        
        # Error history
        self.history: List[Dict[str, Any]] = []
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
    
    def _log_error(self, error_type: str, error: str, context: Dict[str, Any]):
        """Log error with context"""
        self.history.append({
            'type': error_type,
            'error': error,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
    
    async def recover(self, error_type: str, error: str, context: Dict[str, Any]) -> RecoveryResult:
        """Attempt to recover from error"""
        try:
            # Log error
            self._log_error(error_type, error, context)
            
            # Get recovery strategy
            strategy = self.strategies.get(error_type)
            if not strategy:
                return RecoveryResult(
                    success=False,
                    error=f"No recovery strategy for {error_type}"
                )
            
            # Try recovery with retries
            for attempt in range(self.max_retries):
                try:
                    # Get recovery action
                    action = strategy(context)
                    
                    # Create recovery context
                    recovery_context = RecoveryContext(
                        error_type=error_type,
                        error=error,
                        context=context,
                        attempt=attempt + 1
                    )
                    
                    # Execute recovery
                    success = await self._execute_recovery(action, recovery_context)
                    
                    if success:
                        return RecoveryResult(
                            success=True,
                            action=action.action
                        )
                    
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
            
            return RecoveryResult(
                success=False,
                error=f"Recovery failed after {self.max_retries} attempts"
            )
            
        except Exception as e:
            self.logger.error(f"Error recovery failed: {e}")
            return RecoveryResult(
                success=False,
                error=str(e)
            )
    
    async def _execute_recovery(self, action: RecoveryAction, context: RecoveryContext) -> bool:
        """Execute recovery action"""
        try:
            if action.action == 'restart_browser':
                return await self.actions.restart_browser(context)
            elif action.action == 'retry_tool':
                return await self.actions.retry_tool(context)
            elif action.action == 'restart_extension':
                return await self.actions.restart_extension(context)
            elif action.action == 'cleanup_system':
                return await self.actions.cleanup_system(context)
            else:
                raise ValueError(f"Unknown recovery action: {action.action}")
                
        except Exception as e:
            self.logger.error(f"Error executing recovery action: {e}")
            return False
    
    def _handle_browser_error(self, context: Dict[str, Any]) -> RecoveryAction:
        """Handle browser error"""
        error = context.get('error', '').lower()
        
        if 'timeout' in error:
            # For timeout errors, try restarting browser
            return RecoveryAction(
                action='restart_browser',
                params={'force': True},
                timestamp=datetime.now().isoformat()
            )
        elif 'navigation' in error:
            # For navigation errors, try with increased timeout
            return RecoveryAction(
                action='retry_tool',
                params={'timeout': 60000},
                timestamp=datetime.now().isoformat()
            )
        else:
            # Default to browser restart
            return RecoveryAction(
                action='restart_browser',
                params={},
                timestamp=datetime.now().isoformat()
            )
    
    def _handle_tool_error(self, context: Dict[str, Any]) -> RecoveryAction:
        """Handle tool error"""
        tool = context.get('tool', '')
        error = context.get('error', '').lower()
        
        if 'permission' in error:
            # For permission errors, try cleanup
            return RecoveryAction(
                action='cleanup_system',
                params={'tool': tool},
                timestamp=datetime.now().isoformat()
            )
        else:
            # Default to retry
            return RecoveryAction(
                action='retry_tool',
                params={'tool': tool},
                timestamp=datetime.now().isoformat()
            )
    
    def _handle_extension_error(self, context: Dict[str, Any]) -> RecoveryAction:
        """Handle extension error"""
        return RecoveryAction(
            action='restart_extension',
            params={},
            timestamp=datetime.now().isoformat()
        )
    
    def _handle_system_error(self, context: Dict[str, Any]) -> RecoveryAction:
        """Handle system error"""
        return RecoveryAction(
            action='cleanup_system',
            params={'full': True},
            timestamp=datetime.now().isoformat()
        )
