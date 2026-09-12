"""
Local persistent memory subsystem for EDITH.
SQLite backed storage for history, preferences, and action logs.
Developed by G.Vijay Raj (vijay smart).
"""

from memory.database import Database
from memory.memory_manager import MemoryManager, memory_manager
from memory.models import ActionAuditLog, AppAlias, ConversationEntry, UserPreference

__all__ = [
    "Database",
    "MemoryManager",
    "memory_manager",
    "ConversationEntry",
    "AppAlias",
    "UserPreference",
    "ActionAuditLog",
]
