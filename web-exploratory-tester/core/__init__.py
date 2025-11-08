"""Core modules for the web exploratory testing framework."""

from .browser_manager import BrowserManager
from .action_handler import ActionHandler, ActionResult
from .state_tracker import StateTracker, InteractionRecord
from .popup_handler import PopupHandler
from .utils import *

__all__ = [
    'BrowserManager',
    'ActionHandler',
    'ActionResult',
    'StateTracker',
    'InteractionRecord',
    'PopupHandler',
]
