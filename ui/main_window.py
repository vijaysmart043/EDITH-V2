"""
Primary Futuristic Dashboard Window for EDITH.
Displays system telemetry, active orb visualizer, dialogue history,
and rapid action controls with smooth glassmorphic styling.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from app.config import config
from app.logging_config import log_event
from core.assistant_engine import assistant_engine
from ui.chat_widget import ChatWidget
from ui.settings_window import SettingsWindow
from ui.status_widget import EdithCoreOrbWidget
from ui.styles import EDITH_QSS
from ui.system_tray import EdithSystemTray
from utils.windows_utils import get_system_telemetry

try:
    from PySide6.QtCore import QPoint, Qt, QTimer
    from PySide6.QtGui import QCloseEvent, QIcon
    from PySide6.QtWidgets import (
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
    HAVE_PYSIDE6 = True
except ImportError:
    HAVE_PYSIDE6 = False
    class QMainWindow:  # type: ignore[no-redef]
        def __init__(self) -> None: pass


class EdithMainWindow(QMainWindow):
    """Futuristic desktop HUD interface for EDITH."""

    def __init__(self, start_minimized: bool = False) -> None:
        super().__init__()
        if not HAVE_PYSIDE6:
            return

        self.setWindowTitle("EDITH — Enhanced Digital Intelligence & Task Handler")
        self.resize(980, 680)
        self.setMinimumSize(850, 580)
        self.setStyleSheet(EDITH_QSS)

        self._assistant = assistant_engine
        self._assistant.on_ui_event = self._on_assistant_ui_event

        self._build_ui()
        self._init_tray()

        # Telemetry refresh timer (every 2.5s)
        self._telemetry_timer = QTimer(self)
        self._telemetry_timer.timeout.connect(self._refresh_telemetry)
        self._telemetry_timer.start(2500)
        self._refresh_telemetry()

        if start_minimized:
            self.hide()
        else:
            self.show()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        # ---------------------------------------------------------------------
        # Top Header Bar
        # ---------------------------------------------------------------------
        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)

        title_box = QVBoxLayout()
        lbl_title = QLabel("EDITH")
        lbl_title.setProperty("class", "edith-title")
        lbl_subtitle = QLabel("Enhanced Digital Intelligence & Task Handler • by G.Vijay Raj (vijay smart)")
        lbl_subtitle.setProperty("class", "edith-subtitle")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_subtitle)
        header.addLayout(title_box)

        header.addStretch()

        # Header Status Pills
        self.lbl_ai_provider = QLabel("AI: GEMINI")
        self.lbl_ai_provider.setStyleSheet("background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 11px;")
        header.addWidget(self.lbl_ai_provider)

        self.lbl_wake_status = QLabel("WAKE: ACTIVE")
        self.lbl_wake_status.setStyleSheet("background: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 11px;")
        header.addWidget(self.lbl_wake_status)

        btn_settings = QPushButton("Preferences")
        btn_settings.clicked.connect(self._open_settings_modal)
        header.addWidget(btn_settings)

        root_layout.addLayout(header)

        # ---------------------------------------------------------------------
        # Main Split Content (Left: Orb & Telemetry, Right: Chat Transcript)
        # ---------------------------------------------------------------------
        content_split = QHBoxLayout()
        content_split.setSpacing(16)

        # Left Column: Orb Visualizer & System Stats Card
        left_col = QVBoxLayout()
        left_col.setSpacing(12)

        # 1. Core Orb Card
        orb_card = QFrame()
        orb_card.setProperty("class", "edith-card")
        orb_card_layout = QVBoxLayout(orb_card)
        orb_card_layout.setContentsMargins(16, 16, 16, 16)
        orb_card_layout.setAlignment(Qt.AlignCenter)

        self.orb_widget = EdithCoreOrbWidget()
        orb_card_layout.addWidget(self.orb_widget, alignment=Qt.AlignCenter)

        self.lbl_activity = QLabel("Awaiting wake phrase 'Hey EDITH'...")
        self.lbl_activity.setStyleSheet("color: #9ca3af; font-size: 12px; margin-top: 8px;")
        self.lbl_activity.setAlignment(Qt.AlignCenter)
        orb_card_layout.addWidget(self.lbl_activity)

        left_col.addWidget(orb_card)

        # 2. System Telemetry Card
        telem_card = QFrame()
        telem_card.setProperty("class", "edith-card")
        telem_layout = QVBoxLayout(telem_card)
        telem_layout.setContentsMargins(16, 14, 16, 14)
        telem_layout.setSpacing(10)

        lbl_telem_head = QLabel("SYSTEM TELEMETRY")
        lbl_telem_head.setProperty("class", "edith-section-header")
        telem_layout.addWidget(lbl_telem_head)

        grid = QGridLayout()
        grid.setSpacing(8)

        # CPU
        grid.addWidget(QLabel("CPU:"), 0, 0)
        self.bar_cpu = QProgressBar()
        grid.addWidget(self.bar_cpu, 0, 1)
        self.lbl_cpu_val = QLabel("0%")
        grid.addWidget(self.lbl_cpu_val, 0, 2)

        # RAM
        grid.addWidget(QLabel("RAM:"), 1, 0)
        self.bar_ram = QProgressBar()
        grid.addWidget(self.bar_ram, 1, 1)
        self.lbl_ram_val = QLabel("0%")
        grid.addWidget(self.lbl_ram_val, 1, 2)

        # Battery / Power
        grid.addWidget(QLabel("Power:"), 2, 0)
        self.lbl_bat_val = QLabel("AC Power")
        grid.addWidget(self.lbl_bat_val, 2, 1, 1, 2)

        telem_layout.addLayout(grid)
        left_col.addWidget(telem_card)

        # 3. Quick Action Buttons
        quick_box = QHBoxLayout()
        quick_box.setSpacing(6)

        btn_screenshot = QPushButton("Screenshot")
        btn_screenshot.clicked.connect(lambda: self._assistant.process_command("take a screenshot", is_voice=False))
        quick_box.addWidget(btn_screenshot)

        btn_lock = QPushButton("Lock Workstation")
        btn_lock.clicked.connect(lambda: self._assistant.process_command("lock computer", is_voice=False))
        quick_box.addWidget(btn_lock)

        left_col.addLayout(quick_box)
        content_split.addLayout(left_col, stretch=4)

        # Right Column: Conversation Stream & Input Bar
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        chat_card = QFrame()
        chat_card.setProperty("class", "edith-card")
        chat_card_layout = QVBoxLayout(chat_card)
        chat_card_layout.setContentsMargins(12, 12, 12, 12)

        self.chat_widget = ChatWidget()
        chat_card_layout.addWidget(self.chat_widget)
        right_col.addWidget(chat_card, stretch=1)

        # Command Input Bar
        input_bar = QHBoxLayout()
        input_bar.setSpacing(8)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Type a command or say 'Hey EDITH'...")
        self.input_edit.returnPressed.connect(self._handle_manual_send)
        input_bar.addWidget(self.input_edit, stretch=1)

        self.btn_mic = QPushButton("Voice")
        self.btn_mic.setStyleSheet("background: #0284c7; color: #ffffff; font-weight: 700;")
        self.btn_mic.clicked.connect(self._handle_push_to_talk)
        input_bar.addWidget(self.btn_mic)

        btn_send = QPushButton("Execute")
        btn_send.setProperty("class", "primary-btn")
        btn_send.clicked.connect(self._handle_manual_send)
        input_bar.addWidget(btn_send)

        right_col.addLayout(input_bar)
        content_split.addLayout(right_col, stretch=6)

        root_layout.addLayout(content_split, stretch=1)

        # Seed initial greeting
        self.chat_widget.add_message(
            "Greetings. I am EDITH (Enhanced Digital Intelligence & Task Handler). "
            "Say 'Hey EDITH' or type a command to begin.",
            role="edith",
        )

    def _init_tray(self) -> None:
        self.tray = EdithSystemTray(
            parent=self,
            on_open_dashboard=self._restore_from_tray,
            on_toggle_listening=self._handle_tray_toggle_listening,
            on_open_settings=self._open_settings_modal,
            on_exit=self._exit_application,
        )

    def _refresh_telemetry(self) -> None:
        try:
            t = get_system_telemetry()
            self.bar_cpu.setValue(int(t.cpu_percent))
            self.lbl_cpu_val.setText(f"{t.cpu_percent}%")

            self.bar_ram.setValue(int(t.ram_percent))
            self.lbl_ram_val.setText(f"{t.ram_percent}% ({t.ram_used_gb}G)")

            if t.battery_percent is not None:
                state = "Plugged In" if t.power_plugged else "Battery"
                self.lbl_bat_val.setText(f"{t.battery_percent}% ({state})")
            else:
                self.lbl_bat_val.setText("Desktop AC")
        except Exception:
            pass

    def _handle_manual_send(self) -> None:
        text = self.input_edit.text().strip()
        if not text:
            return
        self.input_edit.clear()
        self._assistant.process_command(text, is_voice=False)

    def _handle_push_to_talk(self) -> None:
        """Simulate or trigger instantaneous push-to-talk listening."""
        self.orb_widget.set_state("LISTENING_FOR_COMMAND")
        self.lbl_activity.setText("Listening for command...")

    def _open_settings_modal(self) -> None:
        dlg = SettingsWindow(self)
        dlg.exec()

    def _handle_tray_toggle_listening(self, active: bool) -> None:
        if active:
            self._assistant.start()
            self.lbl_wake_status.setText("WAKE: ACTIVE")
            self.lbl_wake_status.setStyleSheet("background: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 6px;")
        else:
            self._assistant.stop()
            self.lbl_wake_status.setText("WAKE: PAUSED")
            self.lbl_wake_status.setStyleSheet("background: #7f1d1d; color: #f87171; padding: 4px 10px; border-radius: 6px;")

    def _restore_from_tray(self) -> None:
        self.show()
        self.activateWindow()
        self.raise_()

    def _exit_application(self) -> None:
        self._telemetry_timer.stop()
        self._assistant.stop()
        from app.lifecycle import lifecycle
        lifecycle.shutdown()
        import sys
        sys.exit(0)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Minimize to system tray on window close."""
        if config.general.start_minimized:
            event.ignore()
            self.hide()
            self.tray.notify("EDITH Minimized", "EDITH is running in the background. Double-click tray icon to restore.")
        else:
            event.accept()

    def _on_assistant_ui_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Slot for thread-safe asynchronous updates from assistant engine."""
        if event_type == "USER_COMMAND":
            self.chat_widget.add_message(data.get("text", ""), role="user")
            self.lbl_activity.setText(f"Command: {data.get('text', '')}")

        elif event_type == "ASSISTANT_RESPONSE":
            self.chat_widget.add_message(data.get("text", ""), role="edith")
            self.lbl_activity.setText("Awaiting 'Hey EDITH'...")

        elif event_type == "VOICE_STATE_CHANGED":
            state = data.get("state", "IDLE")
            self.orb_widget.set_state(state)
            self.lbl_activity.setText(f"Status: {state.replace('_', ' ').title()}")

        elif event_type == "CONFIRMATION_REQUIRED":
            # Show interactive confirmation popup dialog
            reply = QMessageBox.warning(
                self,
                "Security Confirmation Required",
                f"Dangerous action requested: {data.get('action_name')}\n\n"
                f"{data.get('description')}\n\nDo you authorize EDITH to proceed?",
                QMessageBox.Yes | QMessageBox.No,
            )
            from security.dangerous_actions import dangerous_action_manager
            dangerous_action_manager.resolve_confirmation(reply == QMessageBox.Yes)
