"""
Conversation Session and Multi-Turn Dialogue Manager for EDITH.
Maintains active conversation window, tracks follow-up timeouts,
and logs dialogues to SQLite memory.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import threading
import time
from typing import Callable, List, Optional

from app.config import config
from app.logging_config import log_event
from memory.memory_manager import memory_manager
from memory.models import ConversationEntry


class ConversationManager:
    """Coordinates multi-turn conversational mode after wake word detection."""

    def __init__(self, timeout_sec: Optional[int] = None) -> None:
        self.timeout_sec: float = float(timeout_sec or config.voice.conversation_timeout_sec)
        self.is_active: bool = False
        self.last_interaction_time: float = 0.0
        self._timer_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.on_session_timeout: Optional[Callable[[], None]] = None

    def start_session(self) -> None:
        """Activate conversation window upon wake word detection."""
        with self._lock:
            self.is_active = True
            self.last_interaction_time = time.time()
        log_event("CONVERSATION", f"Conversational session opened (Timeout: {self.timeout_sec}s).")
        self._start_watchdog()

    def touch(self) -> None:
        """Reset conversation timeout on each user utterance."""
        with self._lock:
            self.last_interaction_time = time.time()

    def end_session(self) -> None:
        """Close active conversational mode and return to pure wake-word listening."""
        with self._lock:
            if not self.is_active:
                return
            self.is_active = False
        log_event("CONVERSATION", "Conversational session closed. Returning to wake-word detection.")
        if self.on_session_timeout:
            self.on_session_timeout()

    def _start_watchdog(self) -> None:
        def _check_timeout() -> None:
            while True:
                time.sleep(1.0)
                with self._lock:
                    if not self.is_active:
                        break
                    if time.time() - self.last_interaction_time >= self.timeout_sec:
                        self.is_active = False
                        break

            if self.on_session_timeout:
                self.on_session_timeout()

        threading.Thread(target=_check_timeout, daemon=True, name="ConvTimeoutWatchdog").start()

    def record_user_turn(self, text: str, intent: Optional[str] = None, target: Optional[str] = None) -> None:
        self.touch()
        memory_manager.log_conversation(
            role="user",
            content=text,
            intent=intent,
            target=target,
            success=True,
        )

    def record_assistant_turn(self, text: str, success: bool = True) -> None:
        self.touch()
        memory_manager.log_conversation(
            role="edith",
            content=text,
            success=success,
        )

    def get_recent_history(self, limit: int = 20) -> List[ConversationEntry]:
        return memory_manager.get_recent_conversations(limit=limit)


conversation_manager = ConversationManager()
