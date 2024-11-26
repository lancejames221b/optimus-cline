"""
Mac Assistant - AI-powered workflow automation for macOS
"""

from .search import ResearchManager, SearchResult
from .computer import (
    ComputerController,
    ScreenAnalyzer,
    UIElement,
    ElementType
)
from .agent import MacAssistant, Task
from .chat import AssistantChat

__version__ = '0.1.0'
__author__ = 'Lance James'

__all__ = [
    'ResearchManager',
    'SearchResult',
    'ComputerController',
    'ScreenAnalyzer',
    'UIElement',
    'ElementType',
    'MacAssistant',
    'Task',
    'AssistantChat'
]
