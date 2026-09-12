"""
User Interface subsystem for EDITH.
Developed by G.Vijay Raj (vijay smart).
"""

from ui.chat_widget import ChatBubble, ChatWidget
from ui.main_window import EdithMainWindow
from ui.settings_window import SettingsWindow
from ui.status_widget import EdithCoreOrbWidget
from ui.styles import EDITH_QSS
from ui.system_tray import EdithSystemTray

__all__ = [
    "EdithMainWindow",
    "EdithSystemTray",
    "EdithCoreOrbWidget",
    "ChatWidget",
    "ChatBubble",
    "SettingsWindow",
    "EDITH_QSS",
]
