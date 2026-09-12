"""
Security subsystem for EDITH.
Developed by G.Vijay Raj (vijay smart).
"""

from security.dangerous_actions import DangerousActionManager, dangerous_action_manager
from security.permissions import DANGEROUS_ACTIONS, PermissionLevel
from security.validator import SecurityValidator, ValidationResult

__all__ = [
    "PermissionLevel",
    "DANGEROUS_ACTIONS",
    "SecurityValidator",
    "ValidationResult",
    "DangerousActionManager",
    "dangerous_action_manager",
]
