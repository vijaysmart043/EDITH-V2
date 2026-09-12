"""
Action subsystem package for EDITH.
Ensures all action modules load and register their handlers.
Developed by G.Vijay Raj (vijay smart).
"""

from actions.action_executor import ActionExecutionResult, ActionExecutor, action_executor
from actions.action_registry import ActionDefinition, ActionParameter, ActionRegistry, action_registry

# Import action modules to trigger decorator registrations
import actions.application_actions
import actions.browser_actions
import actions.file_actions
import actions.media_actions
import actions.network_actions
import actions.system_actions

__all__ = [
    "action_registry",
    "action_executor",
    "ActionRegistry",
    "ActionExecutor",
    "ActionDefinition",
    "ActionParameter",
    "ActionExecutionResult",
]
