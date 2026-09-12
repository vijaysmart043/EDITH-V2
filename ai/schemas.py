"""
AI Structured Intent Schemas and Data Models for EDITH.
Ensures Gemini and offline fallback engines return strictly validated intents.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class IntentResult:
    """Structured intent representation returned by AI or offline rule engine."""

    intent: str
    target: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    requires_confirmation: bool = False
    conversational_response: Optional[str] = None
    raw_query: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], raw_query: str = "") -> Optional[IntentResult]:
        if not isinstance(data, dict):
            return None
        intent = data.get("intent")
        if not intent or not isinstance(intent, str):
            return None

        # Clean intent string
        intent_clean = intent.strip().upper()

        confidence = data.get("confidence", 1.0)
        try:
            confidence = float(confidence)
        except (ValueError, TypeError):
            confidence = 0.5

        params = data.get("parameters", {})
        if not isinstance(params, dict):
            params = {}

        return cls(
            intent=intent_clean,
            target=data.get("target"),
            parameters=params,
            confidence=confidence,
            requires_confirmation=bool(data.get("requires_confirmation", False)),
            conversational_response=data.get("conversational_response"),
            raw_query=raw_query,
        )
