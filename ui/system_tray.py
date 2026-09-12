"""
System Tray Integration for EDITH.
Allows background execution, tray menu actions, audio pausing, and log viewing.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
from typing import Callable, Optional

from app.config import config
from app.lifecycle import lifecycle

try:
    from PySide6.QtGui import QAction, QIcon, QPixmap
    from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QWidget
    HAVE_PYSIDE6 = True
except ImportError:
    HAVE_PYSIDE6 = False
    class QWidget:  # type: ignore[no-redef]
        def __init__(self, parent: Any = None) -> None: pass


class EdithSystemTray:
    """Manages the Windows taskbar notification area icon and tray context menu."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        on_open_dashboard: Optional[Callable[[], None]] = None,
        on_toggle_listening: Optional[Callable[[bool], None]] = None,
        on_open_settings: Optional[Callable[[], None]] = None,
        on_restart: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
    ) -> None:
        self.parent = parent
        self.on_open_dashboard = on_open_dashboard
        self.on_toggle_listening = on_toggle_listening
        self.on_open_settings = on_open_settings
        self.on_restart = on_restart
        self.on_exit = on_exit

        self._is_listening_active = True
        self.tray_icon = None

        if HAVE_PYSIDE6:
            self._init_tray()

    def _init_tray(self) -> None:
        self.tray_icon = QSystemTrayIcon(self.parent)

        # Set tray icon (use default stylized icon or fallback pixmap)
        icon_path = config.assets_dir / "icons" / "edith_tray.png"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            # Generate programmatic cyan circle icon if asset missing
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            self.tray_icon.setIcon(QIcon(pixmap))

        self.tray_icon.setToolTip("EDITH — Windows AI Assistant (Hey EDITH)")

        # Create Context Menu
        menu = QMenu()

        # 1. Open EDITH
        act_open = QAction("Open EDITH Dashboard", menu)
        if self.on_open_dashboard:
            act_open.triggered.connect(self.on_open_dashboard)
        menu.addAction(act_open)

        menu.addSeparator()

        # 2. Pause / Resume Listening
        self.act_pause = QAction("Pause Wake Word Listening", menu)
        self.act_pause.triggered.connect(self._handle_toggle_listening)
        menu.addAction(self.act_pause)

        # 3. Settings
        act_settings = QAction("Settings...", menu)
        if self.on_open_settings:
            act_settings.triggered.connect(self.on_open_settings)
        menu.addAction(act_settings)

        # 4. View Logs
        act_logs = QAction("View Diagnostic Logs", menu)
        act_logs.triggered.connect(self._open_logs)
        menu.addAction(act_logs)

        menu.addSeparator()

        # 5. Restart EDITH
        act_restart = QAction("Restart EDITH", menu)
        if self.on_restart:
            act_restart.triggered.connect(self.on_restart)
        menu.addAction(act_restart)

        # 6. Exit
        act_exit = QAction("Exit Completely", menu)
        if self.on_exit:
            act_exit.triggered.connect(self.on_exit)
        else:
            act_exit.triggered.connect(lifecycle.shutdown)
        menu.addAction(act_exit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason: Any) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            if self.on_open_dashboard:
                self.on_open_dashboard()

    def _handle_toggle_listening(self) -> None:
        self._is_listening_active = not self._is_listening_active
        if self._is_listening_active:
            self.act_pause.setText("Pause Wake Word Listening")
            self.notify("EDITH Listening", "Wake word detection active.")
        else:
            self.act_pause.setText("Resume Wake Word Listening")
            self.notify("EDITH Paused", "Microphone listening paused.")

        if self.on_toggle_listening:
            self.on_toggle_listening(self._is_listening_active)

    def _open_logs(self) -> None:
        folder = str(config.logs_dir)
        if os.name == "nt":
            os.startfile(folder)
        else:
            import subprocess
            subprocess.Popen(["xdg-open", folder])

    def notify(self, title: str, message: str) -> None:
        """Display Windows desktop balloon/toast notification."""
        if self.tray_icon and HAVE_PYSIDE6:
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                3000,
            )
