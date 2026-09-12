"""
Action Planner for EDITH.
Transforms structured intent objects into concrete, executable action payloads.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from actions.action_registry import action_registry
from ai.schemas import IntentResult
from app.logging_config import log_event


@dataclass
class PlannedAction:
    action_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    conversational_preface: Optional[str] = None
    is_executable: bool = True
    reason: str = ""


class ActionPlanner:
    """Plans parameter binding and execution order for structured intents."""

    def plan(self, intent: IntentResult) -> PlannedAction:
        action_name = intent.intent.upper()

        if action_name == "CONVERSATION":
            return PlannedAction(
                action_name="CONVERSATION",
                is_executable=False,
                conversational_preface=intent.conversational_response,
                reason="Pure conversation or clarification request.",
            )

        # Verify action exists in registry
        action_def = action_registry.get_action(action_name)
        if not action_def:
            log_event("PLANNER", f"No action registered matching intent: '{action_name}'")
            return PlannedAction(
                action_name=action_name,
                is_executable=False,
                conversational_preface=f"I recognized the command '{action_name}', but it is not currently supported.",
                reason="Action not found in registry.",
            )

        # Merge intent parameters with target
        params = dict(intent.parameters)
        if intent.target and "target" not in params:
            params["target"] = intent.target

        # Check dangerous actions or action requirements
        requires_confirm = intent.requires_confirmation or (action_def.permission_level.value == "DANGEROUS")

        log_event(
            "PLANNER",
            f"Planned action: {action_name} (Params: {params}, RequiresConfirm: {requires_confirm})",
        )

        return PlannedAction(
            action_name=action_name,
            parameters=params,
            requires_confirmation=requires_confirm,
            conversational_preface=intent.conversational_response,
            is_executable=True,
        )


action_planner = ActionPlanner()
