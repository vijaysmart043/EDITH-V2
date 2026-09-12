"""
Dangerous Action Confirmation Manager for EDITH.
Ensures destructive operations halt and demand explicit user verification.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from app.logging_config import log_event


@dataclass
class PendingConfirmation:
    action_id: str
    action_name: str
    description: str
    parameters: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    callback: Optional[Callable[[bool], None]] = None


class DangerousActionManager:
    """Coordinates interactive user prompts for actions classified as DANGEROUS."""

    def __init__(self) -> None:
        self._pending: Optional[PendingConfirmation] = None
        self._lock = threading.Lock()
        self._ui_prompt_handler: Optional[Callable[[PendingConfirmation], None]] = None

    def set_ui_prompt_handler(self, handler: Callable[[PendingConfirmation], None]) -> None:
        """Register the PySide6 UI dialog callback that presents the confirmation modal."""
        self._ui_prompt_handler = handler

    def request_confirmation(
        self,
        action_name: str,
        description: str,
        parameters: Dict[str, Any],
        on_decision: Callable[[bool], None],
    ) -> None:
        """Queue a pending action requiring confirmation and alert UI."""
        with self._lock:
            self._pending = PendingConfirmation(
                action_id=f"act_{int(datetime.now().timestamp())}",
                action_name=action_name,
                description=description,
                parameters=parameters,
                callback=on_decision,
            )
            log_event(
                "SECURITY",
                f"Confirmation requested for dangerous action: {action_name} ({description})",
            )

        if self._ui_prompt_handler:
            self._ui_prompt_handler(self._pending)
        else:
            log_event("SECURITY", "Pending confirmation queued. Waiting for user authorization.")

    def resolve_confirmation(self, confirmed: bool) -> None:
        """Invoked by UI (Yes/No dialog or voice 'Yes confirm') to proceed or abort."""
        with self._lock:
            pending = self._pending
            self._pending = None

        if pending and pending.callback:
            log_event(
                "SECURITY",
                f"Dangerous action '{pending.action_name}' resolved with decision: {'CONFIRMED' if confirmed else 'REJECTED'}",
            )
            pending.callback(confirmed)

    @property
    def has_pending(self) -> bool:
        with self._lock:
            return self._pending is not None


dangerous_action_manager = DangerousActionManager()
