"""
Intent Recognition Engine for EDITH.
Unifies Gemini API reasoning with offline deterministic fallback heuristics.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from ai.gemini_client import gemini_client
from ai.schemas import IntentResult
from app.logging_config import log_event
from core.confidence_engine import confidence_engine


class IntentEngine:
    """Dispatches user text to AI or local fallback and validates confidence."""

    def __init__(self) -> None:
        self.ai_client = gemini_client
        self.evaluator = confidence_engine

    def parse_intent(self, text: str) -> IntentResult:
        """Parse natural language command into structured intent with safety validation."""
        log_event("INTENT", f"Analyzing command: '{text}'")
        intent_result = self.ai_client.interpret(user_text=text)

        # Evaluate confidence
        is_confident = self.evaluator.evaluate(
            intent_name=intent_result.intent,
            confidence_score=intent_result.confidence,
            parameters=intent_result.parameters,
            has_target=bool(intent_result.target),
        )

        if not is_confident and intent_result.intent != "CONVERSATION":
            log_event(
                "INTENT",
                f"Low confidence ({intent_result.confidence}) for intent '{intent_result.intent}'. Demoting to conversational clarification.",
            )
            intent_result.intent = "CONVERSATION"
            intent_result.conversational_response = (
                f"I understood that as a request to {intent_result.intent.lower().replace('_', ' ')}, "
                f"but I'm not completely certain. Could you please clarify?"
            )

        return intent_result


intent_engine = IntentEngine()
