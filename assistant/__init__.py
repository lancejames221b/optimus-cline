"""
Mac Assistant Package
------------------

AI-powered automation assistant for macOS.
"""

from .chat import AssistantChat
from .agent import MacAssistant
from .browser_control import BrowserControl
from .computer import ComputerController
from .search import ResearchManager

__version__ = '1.0.0'
__author__ = 'Lance James'
__email__ = 'lance@221b.sh'

__all__ = [
    'AssistantChat',
    'MacAssistant',
    'BrowserControl',
    'ComputerController',
    'ResearchManager'
]
