"""
Data models for EDITH persistent memory.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ConversationEntry:
    id: Optional[int] = None
    role: str = "user"  # "user" or "edith" or "system"
    content: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    intent: Optional[str] = None
    target: Optional[str] = None
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AppAlias:
    alias: str
    target_executable_or_path: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserPreference:
    key: str
    value: str
    category: str = "general"
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActionAuditLog:
    id: Optional[int] = None
    action_name: str = ""
    parameters_json: str = "{}"
    status: str = "SUCCESS"  # SUCCESS, FAILED, CONFIRMATION_REJECTED
    result_message: str = ""
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
