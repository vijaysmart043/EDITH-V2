"""
Gemini AI Client for EDITH.
Wraps the Google Gemini API for structured intent recognition and conversational reasoning.
Implements lazy client initialization, strict error handling, and offline fallback.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from ai.fallback_engine import fallback_engine
from ai.prompts import EDITH_SYSTEM_PROMPT
from ai.schemas import IntentResult
from app.config import config
from app.logging_config import log_event
from utils.validation import parse_json_safely


class GeminiClient:
    """Interfaces with Gemini model using structured JSON prompt schema."""

    def __init__(self) -> None:
        self._client: Any = None
        self._model_name: str = config.ai.gemini_model

    def _get_api_key(self) -> str:
        # Check config or environment variable
        return config.ai.gemini_api_key or os.getenv("GEMINI_API_KEY", "")

    def is_available(self) -> bool:
        """Return True if an API key is present."""
        return bool(self._get_api_key())

    def _initialize_sdk(self) -> bool:
        """Lazy initialization of Google GenAI SDK."""
        if self._client is not None:
            return True

        api_key = self._get_api_key()
        if not api_key:
            return False

        # Attempt 1: Modern google.genai SDK
        try:
            from google import genai
            self._client = genai.Client(api_key=api_key)
            log_event("AI", "Initialized google.genai client successfully.")
            return True
        except ImportError:
            pass
        except Exception as e:
            log_event("AI", f"Failed initializing google.genai client: {e}")

        # Attempt 2: Legacy google.generativeai SDK
        try:
            import google.generativeai as gai
            gai.configure(api_key=api_key)
            self._client = gai.GenerativeModel(
                model_name=self._model_name,
                system_instruction=EDITH_SYSTEM_PROMPT,
            )
            log_event("AI", "Initialized google.generativeai client successfully.")
            return True
        except Exception as e:
            log_event("AI", f"Failed initializing google.generativeai client: {e}")
            return False

    def interpret(self, user_text: str) -> IntentResult:
        """
        Analyze user input with Gemini.
        If Gemini is offline, unavailable, or times out, seamlessly route through FallbackEngine.
        """
        if not user_text or not user_text.strip():
            return IntentResult(intent="UNKNOWN", confidence=0.0, raw_query="")

        # 1. Fast offline regex check first if it's an unambiguous deterministic command
        fast_match = fallback_engine.parse(user_text)
        if fast_match and fast_match.confidence >= 0.98:
            log_event("AI", f"Fast offline deterministic match resolved: {fast_match.intent}")
            return fast_match

        # 2. Check if Gemini is enabled and configured
        if not self.is_available() or not config.ai.allow_online_reasoning:
            log_event("AI", "Gemini API key not configured or online reasoning disabled. Using FallbackEngine.")
            if fast_match:
                return fast_match
            return IntentResult(
                intent="CONVERSATION",
                confidence=0.7,
                conversational_response=(
                    "I heard you, but my online Gemini connection is not configured with an API key. "
                    "I can still run local commands like opening apps, checking CPU, or adjusting volume."
                ),
                raw_query=user_text,
            )

        # 3. Call Gemini
        if not self._initialize_sdk():
            return fast_match or IntentResult(
                intent="CONVERSATION",
                confidence=0.5,
                conversational_response="Unable to contact Gemini AI engine.",
                raw_query=user_text,
            )

        try:
            prompt = f"{EDITH_SYSTEM_PROMPT}\n\nUser command: {user_text}\nJSON Output:"
            raw_text = ""

            # Check SDK type
            if hasattr(self._client, "models"):  # google.genai
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                )
                raw_text = response.text or ""
            elif hasattr(self._client, "generate_content"):  # google.generativeai
                response = self._client.generate_content(prompt)
                raw_text = response.text or ""

            # Parse JSON
            parsed_dict = parse_json_safely(raw_text)
            if parsed_dict:
                intent_res = IntentResult.from_dict(parsed_dict, raw_query=user_text)
                if intent_res:
                    log_event("AI", f"Gemini parsed intent: {intent_res.intent} (conf: {intent_res.confidence})")
                    return intent_res

            log_event("AI", f"Gemini response could not be parsed into intent schema: {raw_text[:120]}")
        except Exception as e:
            log_event("AI", f"Error during Gemini API call: {e}")

        # Fallback if Gemini failed or returned malformed data
        return fast_match or IntentResult(
            intent="CONVERSATION",
            confidence=0.5,
            conversational_response="I encountered an issue analyzing that request.",
            raw_query=user_text,
        )


gemini_client = GeminiClient()
