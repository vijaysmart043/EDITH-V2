"""
Response Manager for EDITH.
Formats friendly, concise, and natural speech outputs for both UI and TTS.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class ResponseManager:
    """Generates natural spoken and visual messages."""

    @staticmethod
    def format_action_response(action_name: str, success: bool, message: str, data: Dict[str, Any]) -> str:
        if message:
            return message

        if success:
            return f"{action_name.replace('_', ' ').capitalize()} completed successfully."
        return f"I encountered an error trying to execute {action_name.replace('_', ' ').lower()}."

    @staticmethod
    def format_confirmation_prompt(action_name: str, target: Optional[str] = None) -> str:
        act_display = action_name.replace("_", " ").lower()
        if target:
            return f"Are you sure you want to {act_display} '{target}'? Please say confirm or cancel."
        return f"Are you sure you want to {act_display}? Please say confirm or cancel."

    @staticmethod
    def format_acknowledgment() -> str:
        return "Yes, sir?"

    @staticmethod
    def format_clarification(command: str) -> str:
        return f"I didn't quite catch that. Could you repeat?"


response_manager = ResponseManager()
