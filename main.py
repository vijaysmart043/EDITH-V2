"""
EDITH — Enhanced Digital Intelligence & Task Handler
Windows Desktop AI Assistant
Developed by G.Vijay Raj (vijay smart)

Main Entry Point for standalone Python and PyInstaller packaged EDITH.exe.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Add project root to sys.path so modules resolve cleanly under both PyInstaller and source
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config import config
from app.lifecycle import lifecycle
from app.logging_config import log_event, setup_logging
from core.assistant_engine import assistant_engine


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EDITH — Windows Desktop AI Assistant developed by G.Vijay Raj (vijay smart)"
    )
    parser.add_argument(
        "--minimized",
        action="store_true",
        default=config.general.start_minimized,
        help="Start EDITH minimized to Windows system tray without popping up the dashboard.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without GUI (console / service mode only).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enable dry-run mode (simulate all Windows actions safely without executing them).",
    )
    parser.add_argument(
        "--test-command",
        type=str,
        help="Execute a single test command non-interactively and exit (e.g. --test-command 'system info').",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    # 1. Initialize Structured Logging
    setup_logging()
    log_event("BOOT", "=== Launching EDITH Windows Desktop AI Assistant ===")
    log_event("BOOT", f"Developer: {config.general.developer_name}")
    log_event("BOOT", f"Platform: {sys.platform} (Python {sys.version.split()[0]})")

    if args.dry_run:
        config.security.dry_run_mode = True
        log_event("BOOT", "Dry-run mode activated.")

    # 2. Boot Lifecycle Manager
    lifecycle.startup()

    # 3. Direct Test Mode (non-interactive single execution)
    if args.test_command:
        log_event("TEST", f"Running non-interactive test command: '{args.test_command}'")
        from core.intent_engine import intent_engine
        from actions.action_executor import action_executor
        from core.action_planner import action_planner

        intent = intent_engine.parse_intent(args.test_command)
        plan = action_planner.plan(intent)
        if plan.is_executable:
            res = action_executor.execute(plan.action_name, plan.parameters)
            print(f"[RESULT] Success: {res.success} | Message: {res.message}")
        else:
            print(f"[RESULT] Conversational: {plan.conversational_preface}")
        return 0

    # 4. Check GUI Mode
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication
        from ui.main_window import EdithMainWindow

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # Keep running in system tray when window closes
        app.setApplicationName("EDITH")
        app.setOrganizationName("VijaySmart")

        # Instantiate Main Window & System Tray
        window = EdithMainWindow(start_minimized=args.minimized)

        # Start Assistant Background Engine
        assistant_engine.start()
        lifecycle.register_shutdown_hook(assistant_engine.stop)

        log_event("BOOT", "GUI and background services initialized. Event loop starting.")
        return app.exec()

    except ImportError as e:
        log_event("BOOT", f"PySide6 GUI not available or display missing ({e}). Starting in headless mode.")
        assistant_engine.start()
        print("\n[EDITH CLI Active] Voice assistant running in background. Type 'exit' to quit.\n")
        try:
            while True:
                user_in = input("EDITH> ").strip()
                if user_in.lower() in {"exit", "quit"}:
                    break
                if user_in:
                    assistant_engine.process_command(user_in, is_voice=False)
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            assistant_engine.stop()
            lifecycle.shutdown()
        return 0


if __name__ == "__main__":
    sys.exit(main())
