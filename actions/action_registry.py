"""
Action Registry for EDITH.
Defines ActionDefinition metadata, validation callbacks, permission tiers,
and provides a centralized decorator-based registry.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from security.permissions import PermissionLevel


@dataclass
class ActionParameter:
    name: str
    type_name: str
    required: bool = True
    default: Any = None
    description: str = ""


@dataclass
class ActionDefinition:
    name: str
    description: str
    permission_level: PermissionLevel
    parameters: List[ActionParameter] = field(default_factory=list)
    handler: Optional[Callable[..., Dict[str, Any]]] = None
    validator: Optional[Callable[[Dict[str, Any]], Tuple[bool, str]]] = None
    default_success_response: str = "Action completed successfully."
    default_failure_response: str = "Action failed to execute."
    timeout_seconds: float = 10.0


class ActionRegistry:
    """Central registry holding all executable Windows action definitions."""

    def __init__(self) -> None:
        self._actions: Dict[str, ActionDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        permission_level: PermissionLevel = PermissionLevel.NORMAL,
        parameters: Optional[List[ActionParameter]] = None,
        validator: Optional[Callable[[Dict[str, Any]], Tuple[bool, str]]] = None,
        default_success_response: str = "Completed successfully.",
        default_failure_response: str = "Failed to complete.",
        timeout_seconds: float = 10.0,
    ) -> Callable[[Callable[..., Dict[str, Any]]], Callable[..., Dict[str, Any]]]:
        """Decorator to register an action handler function."""

        def decorator(func: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
            action_name = name.upper()
            action_def = ActionDefinition(
                name=action_name,
                description=description,
                permission_level=permission_level,
                parameters=parameters or [],
                handler=func,
                validator=validator,
                default_success_response=default_success_response,
                default_failure_response=default_failure_response,
                timeout_seconds=timeout_seconds,
            )
            self._actions[action_name] = action_def
            return func

        return decorator

    def get_action(self, name: str) -> Optional[ActionDefinition]:
        return self._actions.get(name.upper())

    def list_actions(self) -> List[ActionDefinition]:
        return list(self._actions.values())

    def has_action(self, name: str) -> bool:
        return name.upper() in self._actions


action_registry = ActionRegistry()
