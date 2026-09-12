"""
Conversation History Stream and Dialogue Widget for EDITH.
Displays user commands and assistant responses in futuristic chat bubbles.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from typing import Optional

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QScrollArea,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )
    HAVE_PYSIDE6 = True
except ImportError:
    HAVE_PYSIDE6 = False
    class QWidget:  # type: ignore[no-redef]
        def __init__(self, parent: Any = None) -> None: pass


class ChatBubble(QFrame):
    """Individual styled dialogue bubble for User or EDITH."""

    def __init__(self, text: str, role: str = "user", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        if not HAVE_PYSIDE6:
            return

        is_user = (role == "user")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)

        sender_label = QLabel("YOU" if is_user else "EDITH")
        sender_label.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #38bdf8;" if is_user else "font-size: 10px; font-weight: 700; color: #a855f7;"
        )
        layout.addWidget(sender_label)

        msg_label = QLabel(text)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: #f3f4f6; font-size: 12px; line-height: 1.4;")
        layout.addWidget(msg_label)

        # Bubble background and borders
        if is_user:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: rgba(30, 27, 75, 0.7);
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    border-radius: 10px;
                }
            """)


class ChatWidget(QWidget):
    """Scrollable conversation transcript panel."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        if not HAVE_PYSIDE6:
            return

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.chat_layout = QVBoxLayout(self.container)
        self.chat_layout.setContentsMargins(4, 4, 4, 4)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch()

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

    def add_message(self, text: str, role: str = "user") -> None:
        if not HAVE_PYSIDE6:
            return

        bubble = ChatBubble(text=text, role=role)
        # Insert before bottom stretch
        count = self.chat_layout.count()
        self.chat_layout.insertWidget(max(0, count - 1), bubble)

        # Scroll to bottom
        QScrollArea_bar = self.scroll_area.verticalScrollBar()
        if QScrollArea_bar:
            QScrollArea_bar.setValue(QScrollArea_bar.maximum())
