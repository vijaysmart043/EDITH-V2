"""
Unit Tests for SQLite Memory Manager and Preferences Storage.
Developed by G.Vijay Raj (vijay smart).
"""

import os
import tempfile
import unittest
from pathlib import Path

from memory.database import Database
from memory.memory_manager import MemoryManager


class TestMemory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_memory.db"
        self.db = Database(db_path=self.db_path)
        self.memory = MemoryManager(db=self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_conversation_logging(self):
        self.memory.log_conversation("user", "Open Chrome", intent="OPEN_APPLICATION", target="chrome")
        self.memory.log_conversation("edith", "Chrome is open.", success=True)

        history = self.memory.get_recent_conversations(limit=10)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[0].content, "Open Chrome")
        self.assertEqual(history[1].role, "edith")

    def test_aliases_crud(self):
        self.memory.set_alias("browser", "chrome.exe")
        resolved = self.memory.resolve_alias("browser")
        self.assertEqual(resolved, "chrome.exe")

    def test_preferences_crud(self):
        self.memory.set_preference("dark_mode", "true")
        val = self.memory.get_preference("dark_mode")
        self.assertEqual(val, "true")

    def test_memory_export(self):
        self.memory.set_alias("calc", "calc.exe")
        self.memory.log_conversation("user", "Hello")
        data = self.memory.export_memory()
        self.assertIn("aliases", data)
        self.assertIn("conversations", data)
        self.assertGreater(len(data["conversations"]), 0)


if __name__ == "__main__":
    unittest.main()
