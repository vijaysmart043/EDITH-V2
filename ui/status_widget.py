"""
Futuristic Glowing Core Orb and Voice State Hologram for EDITH.
Renders smooth pulsating animated rings and color shifts corresponding to assistant states.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import math
from typing import Optional

try:
    from PySide6.QtCore import QPointF, QRectF, QTimer, Qt
    from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPaintEvent, QPen, QRadialGradient
    from PySide6.QtWidgets import QWidget
    HAVE_PYSIDE6 = True
except ImportError:
    HAVE_PYSIDE6 = False
    # Stub for headless or test environments
    class QWidget:  # type: ignore[no-redef]
        def __init__(self, parent: Any = None) -> None: pass
        def setFixedSize(self, w: int, h: int) -> None: pass
        def update(self) -> None: pass


class EdithCoreOrbWidget(QWidget):
    """Futuristic holographic orb animating the active assistant state."""

    STATE_COLORS = {
        "IDLE": ("#00f2fe", "#4facfe"),
        "LISTENING_FOR_WAKE_WORD": ("#00f2fe", "#1e40af"),
        "WAKE_WORD_DETECTED": ("#38bdf8", "#0284c7"),
        "LISTENING_FOR_COMMAND": ("#00f2fe", "#3b82f6"),
        "PROCESSING": ("#a855f7", "#7c3aed"),
        "EXECUTING": ("#06b6d4", "#2563eb"),
        "RESPONDING": ("#22d3ee", "#818cf8"),
        "ERROR": ("#ef4444", "#991b1b"),
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self._state = "IDLE"
        self._phase: float = 0.0

        if HAVE_PYSIDE6:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._animate_step)
            self._timer.start(33)  # ~30 FPS

    def set_state(self, state: str) -> None:
        self._state = state
        self.update()

    def _animate_step(self) -> None:
        speed = 0.06 if self._state in {"LISTENING_FOR_COMMAND", "PROCESSING"} else 0.03
        self._phase = (self._phase + speed) % (2 * math.pi)
        self.update()

    def paintEvent(self, event: Any) -> None:
        if not HAVE_PYSIDE6:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        center = QPointF(w / 2.0, h / 2.0)

        primary_hex, secondary_hex = self.STATE_COLORS.get(self._state, ("#00f2fe", "#4facfe"))
        col_primary = QColor(primary_hex)
        col_secondary = QColor(secondary_hex)

        pulse = (math.sin(self._phase) + 1.0) / 2.0  # 0.0 to 1.0

        # 1. Outer Ambient Glow
        glow_radius = 65.0 + (pulse * 8.0)
        radial = QRadialGradient(center, glow_radius)
        c_glow = QColor(col_primary)
        c_glow.setAlpha(int(35 + pulse * 25))
        radial.setColorAt(0.0, c_glow)
        c_trans = QColor(col_primary)
        c_trans.setAlpha(0)
        radial.setColorAt(1.0, c_trans)
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, glow_radius, glow_radius)

        # 2. Outer Rotating Particle Ring
        ring_radius = 52.0
        pen_ring = QPen(col_primary, 1.5)
        pen_ring.setStyle(Qt.DashLine)
        painter.setPen(pen_ring)
        painter.setBrush(Qt.NoBrush)
        painter.save()
        painter.translate(center)
        painter.rotate(math.degrees(self._phase) * 1.5)
        painter.drawEllipse(QPointF(0, 0), ring_radius, ring_radius)
        painter.restore()

        # 3. Inner Pulsing Core Orb
        core_radius = 32.0 + (pulse * 4.0)
        core_grad = QRadialGradient(center, core_radius)
        core_col = QColor(col_primary)
        core_col.setAlpha(220)
        core_grad.setColorAt(0.0, QColor("#ffffff"))
        core_grad.setColorAt(0.4, core_col)
        core_grad.setColorAt(1.0, col_secondary)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(core_grad))
        painter.drawEllipse(center, core_radius, core_radius)

        # 4. State Subtitle Badge
        painter.setPen(QColor("#9ca3af"))
        font = painter.font()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        display_text = self._state.replace("LISTENING_FOR_", "").replace("_", " ")
        text_rect = QRectF(0, h - 22, w, 20)
        painter.drawText(text_rect, Qt.AlignCenter, display_text)
