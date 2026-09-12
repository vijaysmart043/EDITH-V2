"""
SQLite Database Layer for EDITH.
Ensures thread-safe connections, WAL mode for high performance,
and reliable schema migrations.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Optional

from app.config import config
from app.logging_config import log_event


class Database:
    """Thread-safe SQLite database manager."""

    _instance: Optional[Database] = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[Path] = None) -> Database:
        if db_path is not None:
            obj = super(Database, cls).__new__(cls)
            obj._initialized = False
            return obj
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if getattr(self, "_initialized", False):
            return
        self.db_path: Path = db_path or config.db_path
        self._local = threading.local()
        self._init_database()
        self._initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """Return a thread-local SQLite connection with row_factory enabled."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=15.0,
                check_same_thread=False,
            )
            conn.row_factory = sqlite3.Row
            # Enable WAL mode and foreign keys for durability and concurrent reads
            try:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA foreign_keys=ON;")
            except sqlite3.Error:
                pass
            self._local.conn = conn
        return self._local.conn

    def _init_database(self) -> None:
        """Create database tables and indices if they do not exist."""
        conn = self.get_connection()
        with conn:
            # 1. Conversations History Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    intent TEXT,
                    target TEXT,
                    success INTEGER DEFAULT 1
                );
            """)

            # 2. Application Aliases Table (e.g., 'browser' -> 'chrome.exe')
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_aliases (
                    alias TEXT PRIMARY KEY COLLATE NOCASE,
                    target_executable_or_path TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL
                );
            """)

            # 3. User Preferences & Key-Value Memory
            conn.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY COLLATE NOCASE,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    updated_at TEXT NOT NULL
                );
            """)

            # 4. Action Audit Log Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_name TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_message TEXT,
                    execution_time_ms REAL NOT NULL,
                    timestamp TEXT NOT NULL
                );
            """)

            # Indices for rapid querying
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON action_audit_logs(timestamp);")

        log_event("DATABASE", f"SQLite Memory initialized at: {self.db_path}")

    def close(self) -> None:
        """Close thread connection."""
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None
