"""
Memory Manager for EDITH.
Provides high-level CRUD operations for conversation logs,
custom alias mappings, key-value memory, and action audit records.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from memory.database import Database
from memory.models import ActionAuditLog, AppAlias, ConversationEntry, UserPreference


class MemoryManager:
    """Manages conversational recall, contextual application aliases, and action history."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self.db = db or Database()
        self.enabled: bool = True
        self._seed_default_aliases()

    def _seed_default_aliases(self) -> None:
        """Seed common default aliases on fresh installation."""
        defaults = [
            ("browser", "chrome.exe", "Google Chrome Web Browser"),
            ("chrome", "chrome.exe", "Google Chrome Web Browser"),
            ("edge", "msedge.exe", "Microsoft Edge Web Browser"),
            ("notepad", "notepad.exe", "Windows Notepad Text Editor"),
            ("calculator", "calc.exe", "Windows Calculator"),
            ("calc", "calc.exe", "Windows Calculator"),
            ("explorer", "explorer.exe", "Windows File Explorer"),
            ("files", "explorer.exe", "Windows File Explorer"),
            ("cmd", "cmd.exe", "Windows Command Prompt"),
            ("terminal", "wt.exe", "Windows Terminal"),
            ("settings", "ms-settings:", "Windows Settings Hub"),
            ("task manager", "taskmgr.exe", "Windows Task Manager"),
            ("taskmgr", "taskmgr.exe", "Windows Task Manager"),
        ]
        for alias, target, desc in defaults:
            self.set_alias(alias, target, desc, overwrite_if_exists=False)

    # -------------------------------------------------------------------------
    # Conversation History
    # -------------------------------------------------------------------------
    def log_conversation(
        self,
        role: str,
        content: str,
        intent: Optional[str] = None,
        target: Optional[str] = None,
        success: bool = True,
    ) -> Optional[int]:
        if not self.enabled:
            return None
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO conversations (role, content, timestamp, intent, target, success)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (role, content, datetime.now().isoformat(), intent, target, 1 if success else 0),
            )
            return cursor.lastrowid

    def get_recent_conversations(self, limit: int = 50) -> List[ConversationEntry]:
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, role, content, timestamp, intent, target, success
            FROM conversations
            ORDER BY id DESC
            LIMIT ?;
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        entries = [
            ConversationEntry(
                id=row["id"],
                role=row["role"],
                content=row["content"],
                timestamp=row["timestamp"],
                intent=row["intent"],
                target=row["target"],
                success=bool(row["success"]),
            )
            for row in reversed(rows)
        ]
        return entries

    def delete_conversation(self, conversation_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute("DELETE FROM conversations WHERE id = ?;", (conversation_id,))
            return cursor.rowcount > 0

    def clear_conversations(self) -> None:
        conn = self.db.get_connection()
        with conn:
            conn.execute("DELETE FROM conversations;")

    # -------------------------------------------------------------------------
    # Application Aliases
    # -------------------------------------------------------------------------
    def set_alias(
        self,
        alias: str,
        target: str,
        description: str = "",
        overwrite_if_exists: bool = True,
    ) -> bool:
        alias_clean = alias.strip().lower()
        if not alias_clean or not target.strip():
            return False
        conn = self.db.get_connection()
        with conn:
            if overwrite_if_exists:
                conn.execute(
                    """
                    INSERT INTO app_aliases (alias, target_executable_or_path, description, created_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(alias) DO UPDATE SET
                        target_executable_or_path = excluded.target_executable_or_path,
                        description = excluded.description;
                    """,
                    (alias_clean, target.strip(), description, datetime.now().isoformat()),
                )
            else:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO app_aliases (alias, target_executable_or_path, description, created_at)
                    VALUES (?, ?, ?, ?);
                    """,
                    (alias_clean, target.strip(), description, datetime.now().isoformat()),
                )
        return True

    def get_alias(self, alias: str) -> Optional[AppAlias]:
        alias_clean = alias.strip().lower()
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT alias, target_executable_or_path, description, created_at FROM app_aliases WHERE alias = ?;",
            (alias_clean,),
        )
        row = cursor.fetchone()
        if row:
            return AppAlias(
                alias=row["alias"],
                target_executable_or_path=row["target_executable_or_path"],
                description=row["description"],
                created_at=row["created_at"],
            )
        return None

    def resolve_alias(self, alias: str) -> Optional[str]:
        """Resolve an alias string directly to target executable or path."""
        obj = self.get_alias(alias)
        return obj.target_executable_or_path if obj else None

    def get_all_aliases(self) -> List[AppAlias]:
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT alias, target_executable_or_path, description, created_at FROM app_aliases ORDER BY alias ASC;"
        )
        return [
            AppAlias(
                alias=row["alias"],
                target_executable_or_path=row["target_executable_or_path"],
                description=row["description"],
                created_at=row["created_at"],
            )
            for row in cursor.fetchall()
        ]

    def delete_alias(self, alias: str) -> bool:
        alias_clean = alias.strip().lower()
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute("DELETE FROM app_aliases WHERE alias = ?;", (alias_clean,))
            return cursor.rowcount > 0

    # -------------------------------------------------------------------------
    # Key-Value Memory & Preferences
    # -------------------------------------------------------------------------
    def set_preference(self, key: str, value: str, category: str = "general") -> None:
        key_clean = key.strip().lower()
        conn = self.db.get_connection()
        with conn:
            conn.execute(
                """
                INSERT INTO preferences (key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    updated_at = excluded.updated_at;
                """,
                (key_clean, value, category, datetime.now().isoformat()),
            )

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        key_clean = key.strip().lower()
        conn = self.db.get_connection()
        cursor = conn.execute("SELECT value FROM preferences WHERE key = ?;", (key_clean,))
        row = cursor.fetchone()
        return row["value"] if row else default

    def get_all_preferences(self) -> List[UserPreference]:
        conn = self.db.get_connection()
        cursor = conn.execute("SELECT key, value, category, updated_at FROM preferences ORDER BY key ASC;")
        return [
            UserPreference(
                key=row["key"],
                value=row["value"],
                category=row["category"],
                updated_at=row["updated_at"],
            )
            for row in cursor.fetchall()
        ]

    # -------------------------------------------------------------------------
    # Audit Logs
    # -------------------------------------------------------------------------
    def record_audit(
        self,
        action_name: str,
        parameters: Dict[str, Any],
        status: str,
        result_message: str,
        execution_time_ms: float,
    ) -> None:
        conn = self.db.get_connection()
        with conn:
            conn.execute(
                """
                INSERT INTO action_audit_logs (action_name, parameters_json, status, result_message, execution_time_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    action_name,
                    json.dumps(parameters),
                    status,
                    result_message,
                    execution_time_ms,
                    datetime.now().isoformat(),
                ),
            )

    def get_recent_audit_logs(self, limit: int = 50) -> List[ActionAuditLog]:
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, action_name, parameters_json, status, result_message, execution_time_ms, timestamp
            FROM action_audit_logs
            ORDER BY id DESC
            LIMIT ?;
            """,
            (limit,),
        )
        return [
            ActionAuditLog(
                id=row["id"],
                action_name=row["action_name"],
                parameters_json=row["parameters_json"],
                status=row["status"],
                result_message=row["result_message"],
                execution_time_ms=row["execution_time_ms"],
                timestamp=row["timestamp"],
            )
            for row in cursor.fetchall()
        ]

    # -------------------------------------------------------------------------
    # Export & Wipe
    # -------------------------------------------------------------------------
    def export_memory(self) -> Dict[str, Any]:
        """Export non-sensitive memory state to JSON-serializable dictionary."""
        return {
            "exported_at": datetime.now().isoformat(),
            "developer": "G.Vijay Raj (vijay smart)",
            "conversations": [c.to_dict() for c in self.get_recent_conversations(limit=1000)],
            "aliases": [a.to_dict() for a in self.get_all_aliases()],
            "preferences": [p.to_dict() for p in self.get_all_preferences()],
            "recent_actions": [l.to_dict() for l in self.get_recent_audit_logs(limit=100)],
        }

    def wipe_all(self) -> None:
        """Clear all conversations, custom memory, and logs."""
        conn = self.db.get_connection()
        with conn:
            conn.execute("DELETE FROM conversations;")
            conn.execute("DELETE FROM preferences;")
            conn.execute("DELETE FROM action_audit_logs;")
        self._seed_default_aliases()


memory_manager = MemoryManager()
