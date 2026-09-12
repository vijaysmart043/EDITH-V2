"""
AI subsystem package for EDITH.
Developed by G.Vijay Raj (vijay smart).
"""

from ai.fallback_engine import FallbackEngine, fallback_engine
from ai.gemini_client import GeminiClient, gemini_client
from ai.prompts import EDITH_SYSTEM_PROMPT
from ai.schemas import IntentResult

__all__ = [
    "GeminiClient",
    "gemini_client",
    "FallbackEngine",
    "fallback_engine",
    "IntentResult",
    "EDITH_SYSTEM_PROMPT",
]
