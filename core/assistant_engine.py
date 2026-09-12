"""
Master Assistant Engine for EDITH.
Unifies voice triggers, intent reasoning, action planning, security validation,
dangerous action confirmations, and response synthesis.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Dict, Optional

from actions.action_executor import action_executor
from app.config import config
from app.logging_config import log_event
from core.action_planner import action_planner
from core.conversation_manager import conversation_manager
from core.intent_engine import intent_engine
from core.response_manager import response_manager
from security.dangerous_actions import dangerous_action_manager
from voice.voice_pipeline import VoicePipeline, VoiceState


class AssistantEngine:
    """Master controller coordinating speech, AI reasoning, and desktop action execution."""

    def __init__(
        self,
        voice_pipeline: Optional[VoicePipeline] = None,
        on_ui_event: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        self.on_ui_event = on_ui_event
        self.voice_pipeline = voice_pipeline or VoicePipeline(
            on_state_change=self._handle_voice_state_change,
            on_command_detected=self.process_command,
        )
        self.intent_engine = intent_engine
        self.planner = action_planner
        self.executor = action_executor
        self.conversation_manager = conversation_manager
        self.response_manager = response_manager

        # Connect dangerous action confirmation prompt to UI
        dangerous_action_manager.set_ui_prompt_handler(self._handle_dangerous_prompt)
        self.conversation_manager.on_session_timeout = self._on_conversation_timeout

    def start(self) -> bool:
        """Start the assistant engine and wake-word detector."""
        log_event("ENGINE", "EDITH Assistant Engine starting...")
        return self.voice_pipeline.start()

    def stop(self) -> None:
        """Stop the assistant engine."""
        log_event("ENGINE", "EDITH Assistant Engine stopping...")
        self.voice_pipeline.stop()

    def process_command(self, user_command: str, is_voice: bool = True) -> None:
        """Process incoming user command from microphone or GUI text input."""
        threading.Thread(
            target=self._process_command_worker,
            args=(user_command, is_voice),
            daemon=True,
            name="CommandWorker",
        ).start()

    def _process_command_worker(self, user_command: str, is_voice: bool) -> None:
        if not user_command or not user_command.strip():
            return

        clean_text = user_command.strip()
        log_event("ENGINE", f"Processing command: '{clean_text}' (Voice: {is_voice})")

        self._emit_ui("USER_COMMAND", {"text": clean_text, "is_voice": is_voice})

        # 1. Check if user is answering a pending dangerous confirmation ("yes confirm" / "no cancel")
        if dangerous_action_manager.has_pending:
            clean_lower = clean_text.lower()
            if any(w in clean_lower for w in ["yes", "confirm", "proceed", "do it", "sure"]):
                dangerous_action_manager.resolve_confirmation(True)
                self.respond("Confirmed. Executing action.", is_voice=is_voice)
                return
            elif any(w in clean_lower for w in ["no", "cancel", "stop", "abort", "don't"]):
                dangerous_action_manager.resolve_confirmation(False)
                self.respond("Action cancelled.", is_voice=is_voice)
                return

        # 2. Touch conversation session
        self.conversation_manager.start_session()
        self.voice_pipeline.set_state(VoiceState.PROCESSING)

        # 3. Parse intent with AI or offline fallback
        intent_res = self.intent_engine.parse_intent(clean_text)
        self.conversation_manager.record_user_turn(clean_text, intent_res.intent, intent_res.target)

        # 4. Plan action
        plan = self.planner.plan(intent_res)

        # 5. Handle conversational answers (e.g. Q&A, greetings)
        if not plan.is_executable:
            response_text = plan.conversational_preface or "I'm not sure how to assist with that."
            self.respond(response_text, is_voice=is_voice)
            return

        # 6. Execute action
        self.voice_pipeline.set_state(VoiceState.EXECUTING)
        self._emit_ui("ACTION_EXECUTING", {"action_name": plan.action_name, "parameters": plan.parameters})

        if plan.requires_confirmation:
            # Request confirmation via DangerousActionManager
            def _on_confirm(confirmed: bool) -> None:
                if confirmed:
                    result = self.executor.execute(plan.action_name, plan.parameters, user_confirmed=True)
                    spoken = self.response_manager.format_action_response(
                        plan.action_name, result.success, result.message, result.data
                    )
                    self.respond(spoken, is_voice=is_voice)
                else:
                    self.respond(f"Operation '{plan.action_name}' was aborted.", is_voice=is_voice)

            dangerous_action_manager.request_confirmation(
                action_name=plan.action_name,
                description=f"Action '{plan.action_name}' requires your confirmation.",
                parameters=plan.parameters,
                on_decision=_on_confirm,
            )
            prompt_msg = self.response_manager.format_confirmation_prompt(plan.action_name, plan.parameters.get("target"))
            self.respond(prompt_msg, is_voice=is_voice)
            return

        # Standard non-dangerous execution
        exec_result = self.executor.execute(plan.action_name, plan.parameters)
        spoken_msg = self.response_manager.format_action_response(
            plan.action_name, exec_result.success, exec_result.message, exec_result.data
        )

        self._emit_ui("ACTION_COMPLETED", exec_result.to_dict())
        self.respond(spoken_msg, is_voice=is_voice)

    def respond(self, message: str, is_voice: bool = True) -> None:
        """Deliver assistant response to speech output and UI."""
        self.conversation_manager.record_assistant_turn(message)
        self._emit_ui("ASSISTANT_RESPONSE", {"text": message})

        if is_voice and config.voice.wake_word_enabled:
            self.voice_pipeline.speak_response(message, return_to_wake_word=True)
        else:
            self.voice_pipeline.set_state(VoiceState.LISTENING_FOR_WAKE_WORD)

    def _handle_voice_state_change(self, state: VoiceState) -> None:
        self._emit_ui("VOICE_STATE_CHANGED", {"state": state.value})

    def _handle_dangerous_prompt(self, pending: Any) -> None:
        self._emit_ui("CONFIRMATION_REQUIRED", {
            "action_name": pending.action_name,
            "description": pending.description,
            "parameters": pending.parameters,
        })

    def _on_conversation_timeout(self) -> None:
        log_event("ENGINE", "Active conversation window timed out. Resetting to wake-word mode.")
        self.voice_pipeline.set_state(VoiceState.LISTENING_FOR_WAKE_WORD)
        self._emit_ui("CONVERSATION_TIMEOUT", {})

    def _emit_ui(self, event_type: str, data: Dict[str, Any]) -> None:
        if self.on_ui_event:
            try:
                self.on_ui_event(event_type, data)
            except Exception as e:
                log_event("ENGINE", f"Error notifying UI: {e}")


assistant_engine = AssistantEngine()
