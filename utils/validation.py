"""
Input sanitization and validation helpers.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional


def sanitize_input_text(text: str, max_length: int = 500) -> str:
    """Strip dangerous control characters while preserving unicode and alphanumeric punctuation."""
    if not text:
        return ""
    # Strip null bytes and non-printable control characters (except newline/tab)
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    return cleaned.strip()[:max_length]


def parse_json_safely(raw_json: str) -> Optional[Dict[str, Any]]:
    """Parse JSON string safely, stripping markdown fences if present."""
    if not raw_json:
        return None
    cleaned = raw_json.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
        return None
    except json.JSONDecodeError:
        return None
