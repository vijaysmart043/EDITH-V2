"""
Futuristic Dark Glassmorphic QSS Styling for EDITH.
Features cyan, electric blue, and purple neon accents, rounded cards,
and smooth high-tech visual hierarchy.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

COLOR_BG_DARK = "#0a0e17"
COLOR_BG_CARD = "#111827"
COLOR_BG_CARD_TRANSPARENT = "rgba(17, 24, 39, 0.85)"
COLOR_ACCENT_CYAN = "#00f2fe"
COLOR_ACCENT_BLUE = "#4facfe"
COLOR_ACCENT_PURPLE = "#8b5cf6"
COLOR_TEXT_PRIMARY = "#f3f4f6"
COLOR_TEXT_SECONDARY = "#9ca3af"
COLOR_TEXT_MUTED = "#6b7280"
COLOR_BORDER = "#1f2937"
COLOR_BORDER_GLOW = "rgba(0, 242, 254, 0.4)"
COLOR_DANGER = "#ef4444"
COLOR_SUCCESS = "#10b981"


EDITH_QSS = f"""
QMainWindow, QDialog {{
    background-color: {COLOR_BG_DARK};
    color: {COLOR_TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
}}

QWidget {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}

/* Cards and Panels */
QFrame.edith-card {{
    background-color: {COLOR_BG_CARD_TRANSPARENT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
}}

QFrame.edith-card:hover {{
    border: 1px solid {COLOR_BORDER_GLOW};
}}

/* Typography */
QLabel.edith-title {{
    font-size: 20px;
    font-weight: 700;
    color: {COLOR_ACCENT_CYAN};
    letter-spacing: 1px;
}}

QLabel.edith-subtitle {{
    font-size: 12px;
    font-weight: 500;
    color: {COLOR_TEXT_SECONDARY};
}}

QLabel.edith-section-header {{
    font-size: 14px;
    font-weight: 600;
    color: {COLOR_ACCENT_BLUE};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel.telemetry-val {{
    font-size: 16px;
    font-weight: 700;
    color: {COLOR_TEXT_PRIMARY};
}}

/* Push Buttons */
QPushButton {{
    background-color: #1f2937;
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid #374151;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: #374151;
    border-color: {COLOR_ACCENT_CYAN};
    color: #ffffff;
}}

QPushButton:pressed {{
    background-color: #111827;
}}

QPushButton.primary-btn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4facfe, stop:1 #00f2fe);
    color: #050b14;
    border: none;
    font-weight: 700;
}}

QPushButton.primary-btn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f2fe, stop:1 #4facfe);
}}

QPushButton.danger-btn {{
    background-color: rgba(239, 68, 68, 0.2);
    border: 1px solid {COLOR_DANGER};
    color: {COLOR_DANGER};
}}

QPushButton.danger-btn:hover {{
    background-color: {COLOR_DANGER};
    color: #ffffff;
}}

/* Line Edits and Inputs */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: {COLOR_ACCENT_BLUE};
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {COLOR_ACCENT_CYAN};
}}

/* Progress Bars */
QProgressBar {{
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    font-size: 10px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #00f2fe);
    border-radius: 4px;
}}

/* Tabs in Settings */
QTabWidget::pane {{
    border: 1px solid {COLOR_BORDER};
    background-color: {COLOR_BG_CARD};
    border-radius: 8px;
}}

QTabBar::tab {{
    background-color: #1e293b;
    color: {COLOR_TEXT_SECONDARY};
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: {COLOR_BG_CARD};
    color: {COLOR_ACCENT_CYAN};
    border-bottom: 2px solid {COLOR_ACCENT_CYAN};
}}

QTabBar::tab:hover:!selected {{
    background-color: #334155;
    color: {COLOR_TEXT_PRIMARY};
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: #0f172a;
    width: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: #334155;
    border-radius: 3px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_ACCENT_CYAN};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""
