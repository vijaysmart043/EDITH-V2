"""
Confidence Evaluation Engine for EDITH.
Calculates reliability scores based on lexical match, semantic confidence,
and parameter completeness to prevent ambiguous action executions.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from typing import Any, Dict


class ConfidenceEngine:
    """Evaluates whether an intent possesses adequate certainty for execution."""

    def __init__(self, execution_threshold: float = 0.70) -> None:
        self.execution_threshold = execution_threshold

    def evaluate(
        self,
        intent_name: str,
        confidence_score: float,
        parameters: Dict[str, Any],
        has_target: bool,
    ) -> bool:
        """Return True if intent confidence exceeds threshold and parameters are coherent."""
        if confidence_score < self.execution_threshold:
            return False

        # If it's an application intent, target must be present
        if intent_name in {"OPEN_APPLICATION", "CLOSE_APPLICATION"} and not has_target:
            return False

        # If it's volume setting, value must be present
        if intent_name == "SET_VOLUME" and "value" not in parameters:
            return False

        return True


confidence_engine = ConfidenceEngine()
