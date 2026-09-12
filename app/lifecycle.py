"""
Application Lifecycle Coordinator for EDITH.
Orchestrates startup sequence, subsystem initialization, graceful shutdown,
and Windows background execution.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import atexit
import signal
import sys
from typing import Any, Callable, List, Optional

from app.config import config
from app.logging_config import log_event


class LifecycleManager:
    """Manages application startup, active state, background services, and cleanup."""

    def __init__(self) -> None:
        self._is_running: bool = False
        self._shutdown_hooks: List[Callable[[], None]] = []
        self._tray_visible: bool = False

    def register_shutdown_hook(self, hook: Callable[[], None]) -> None:
        """Register a callback function to execute on application shutdown."""
        self._shutdown_hooks.append(hook)

    def startup(self) -> None:
        """Execute boot initialization checks."""
        log_event("LIFECYCLE", "Starting EDITH Windows Assistant engine...")
        self._is_running = True

        # Hook OS termination signals
        try:
            signal.signal(signal.SIGINT, self._handle_os_signal)
            signal.signal(signal.SIGTERM, self._handle_os_signal)
        except (ValueError, AttributeError):
            pass

        atexit.register(self.shutdown)
        log_event("LIFECYCLE", f"Initialization complete. Running in data dir: {config.data_dir}")

    def shutdown(self) -> None:
        """Gracefully release all resources, stop background threads, and exit."""
        if not self._is_running:
            return
        log_event("LIFECYCLE", "Initiating graceful shutdown sequence...")
        self._is_running = False

        for hook in reversed(self._shutdown_hooks):
            try:
                hook()
            except Exception as e:
                log_event("LIFECYCLE", f"Error during shutdown hook: {e}")

        log_event("LIFECYCLE", "EDITH terminated safely.")

    def _handle_os_signal(self, signum: int, frame: Any) -> None:
        log_event("LIFECYCLE", f"Received OS signal {signum}. Halting...")
        self.shutdown()
        sys.exit(0)

    @property
    def is_running(self) -> bool:
        return self._is_running


lifecycle = LifecycleManager()
