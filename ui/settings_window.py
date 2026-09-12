"""
Comprehensive Settings Dialog for EDITH.
Configures General, Voice, AI, Security, Memory, and Diagnostics settings.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
from typing import Optional

from app.config import config
from app.logging_config import log_event
from memory.memory_manager import memory_manager
from startup.windows_startup import WindowsStartupManager
from voice.audio_manager import AudioManager

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QSlider,
        QSpinBox,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )
    HAVE_PYSIDE6 = True
except ImportError:
    HAVE_PYSIDE6 = False
    class QDialog:  # type: ignore[no-redef]
        def __init__(self, parent: Any = None) -> None: pass


class SettingsWindow(QDialog):
    """Full-featured settings and preferences configuration window."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        if not HAVE_PYSIDE6:
            return

        self.setWindowTitle("EDITH — System Preferences & Configuration")
        self.resize(640, 520)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_general_tab(), "General")
        self.tabs.addTab(self._build_voice_tab(), "Voice & Audio")
        self.tabs.addTab(self._build_ai_tab(), "AI & Gemini")
        self.tabs.addTab(self._build_security_tab(), "Security")
        self.tabs.addTab(self._build_memory_tab(), "Memory")
        self.tabs.addTab(self._build_diagnostics_tab(), "Diagnostics")

        layout.addWidget(self.tabs)

        # Bottom Buttons (Save / Cancel)
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Preferences")
        btn_save.setProperty("class", "primary-btn")
        btn_save.clicked.connect(self._save_settings)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    # -------------------------------------------------------------------------
    # Tab 1: General
    # -------------------------------------------------------------------------
    def _build_general_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(16, 16, 16, 16)

        self.cb_startup = QCheckBox("Launch EDITH automatically on Windows login")
        self.cb_startup.setChecked(WindowsStartupManager.is_startup_enabled())
        form.addRow("Windows Startup:", self.cb_startup)

        self.cb_minimized = QCheckBox("Start minimized to System Tray")
        self.cb_minimized.setChecked(config.general.start_minimized)
        form.addRow("Tray Behavior:", self.cb_minimized)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Futuristic Dark Neon (Default)", "Cyberpunk Blue", "Obsidian Stealth"])
        form.addRow("Visual Theme:", self.combo_theme)

        lbl_developer = QLabel(f"Developed by {config.general.developer_name}")
        lbl_developer.setStyleSheet("color: #6b7280; font-size: 11px;")
        form.addRow("Architect:", lbl_developer)

        return widget

    # -------------------------------------------------------------------------
    # Tab 2: Voice & Audio
    # -------------------------------------------------------------------------
    def _build_voice_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(16, 16, 16, 16)

        self.cb_wake_word = QCheckBox("Enable 'Hey EDITH' Wake Word Listener")
        self.cb_wake_word.setChecked(config.voice.wake_word_enabled)
        form.addRow("Wake Word Status:", self.cb_wake_word)

        # Sensitivity Slider
        self.slider_sens = QSlider(Qt.Horizontal)
        self.slider_sens.setRange(10, 100)
        self.slider_sens.setValue(int(config.voice.wake_word_sensitivity * 100))
        form.addRow("Sensitivity:", self.slider_sens)

        # Microphone selector
        self.combo_mic = QComboBox()
        devices = AudioManager.list_input_devices()
        for d in devices:
            self.combo_mic.addItem(d["name"], d["id"])
        form.addRow("Microphone:", self.combo_mic)

        # TTS Rate Slider
        self.slider_rate = QSlider(Qt.Horizontal)
        self.slider_rate.setRange(100, 250)
        self.slider_rate.setValue(config.voice.voice_rate)
        form.addRow("Voice Rate:", self.slider_rate)

        # Conversation timeout
        self.combo_timeout = QComboBox()
        self.combo_timeout.addItems(["5 seconds", "10 seconds", "20 seconds", "30 seconds"])
        idx = {5: 0, 10: 1, 20: 2, 30: 3}.get(config.voice.conversation_timeout_sec, 1)
        self.combo_timeout.setCurrentIndex(idx)
        form.addRow("Active Listening Window:", self.combo_timeout)

        return widget

    # -------------------------------------------------------------------------
    # Tab 3: AI & Gemini
    # -------------------------------------------------------------------------
    def _build_ai_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(16, 16, 16, 16)

        self.combo_model = QComboBox()
        self.combo_model.addItems(["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"])
        curr_model = config.ai.gemini_model
        model_idx = self.combo_model.findText(curr_model)
        if model_idx >= 0:
            self.combo_model.setCurrentIndex(model_idx)
        form.addRow("Gemini Model:", self.combo_model)

        self.edit_api_key = QLineEdit(config.ai.gemini_api_key)
        self.edit_api_key.setEchoMode(QLineEdit.Password)
        self.edit_api_key.setPlaceholderText("Enter Gemini API key (or leave empty for offline mode)")
        form.addRow("Gemini API Key:", self.edit_api_key)

        self.cb_online_reasoning = QCheckBox("Allow cloud Gemini reasoning (Offline fallback if unchecked)")
        self.cb_online_reasoning.setChecked(config.ai.allow_online_reasoning)
        form.addRow("Cloud Reasoning:", self.cb_online_reasoning)

        return widget

    # -------------------------------------------------------------------------
    # Tab 4: Security
    # -------------------------------------------------------------------------
    def _build_security_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(16, 16, 16, 16)

        self.cb_confirm_dangerous = QCheckBox("Require confirmation for dangerous actions (Shutdown, Restart, Delete)")
        self.cb_confirm_dangerous.setChecked(config.security.require_confirmation_for_dangerous)
        form.addRow("Dangerous Safeguard:", self.cb_confirm_dangerous)

        self.cb_advanced_auto = QCheckBox("Advanced Automation Mode (Bypasses dangerous action prompts)")
        self.cb_advanced_auto.setChecked(config.security.allow_advanced_automation)
        form.addRow("Bypass Prompts:", self.cb_advanced_auto)

        self.cb_allow_files = QCheckBox("Allow File System Operations (Create, Search, Delete)")
        self.cb_allow_files.setChecked(config.security.allow_file_operations)
        form.addRow("File Actions:", self.cb_allow_files)

        self.cb_dry_run = QCheckBox("Dry-Run Simulation Mode (Simulate actions without changing Windows state)")
        self.cb_dry_run.setChecked(config.security.dry_run_mode)
        form.addRow("Simulation Mode:", self.cb_dry_run)

        return widget

    # -------------------------------------------------------------------------
    # Tab 5: Memory
    # -------------------------------------------------------------------------
    def _build_memory_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(16, 16, 16, 16)

        self.cb_enable_memory = QCheckBox("Enable persistent memory and conversation logging")
        self.cb_enable_memory.setChecked(memory_manager.enabled)
        form.addRow("SQLite Memory:", self.cb_enable_memory)

        btn_export = QPushButton("Export Memory to JSON")
        btn_export.clicked.connect(self._export_memory)
        form.addRow("Data Export:", btn_export)

        btn_wipe = QPushButton("Clear All Memory & History")
        btn_wipe.setProperty("class", "danger-btn")
        btn_wipe.clicked.connect(self._clear_memory)
        form.addRow("Data Wipe:", btn_wipe)

        return widget

    # -------------------------------------------------------------------------
    # Tab 6: Diagnostics
    # -------------------------------------------------------------------------
    def _build_diagnostics_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(16, 16, 16, 16)

        self.combo_log_level = QComboBox()
        self.combo_log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        idx = self.combo_log_level.findText(config.diagnostics.log_level.upper())
        if idx >= 0:
            self.combo_log_level.setCurrentIndex(idx)
        form.addRow("Logging Level:", self.combo_log_level)

        btn_logs = QPushButton("Open Logs Directory")
        btn_logs.clicked.connect(self._open_logs_dir)
        form.addRow("Logs Folder:", btn_logs)

        btn_test_speaker = QPushButton("Test Speaker (TTS)")
        btn_test_speaker.clicked.connect(self._test_speaker)
        form.addRow("Audio Test:", btn_test_speaker)

        return widget

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def _save_settings(self) -> None:
        # Update General
        config.general.start_minimized = self.cb_minimized.isChecked()
        if self.cb_startup.isChecked():
            WindowsStartupManager.enable_startup()
        else:
            WindowsStartupManager.disable_startup()

        # Update Voice
        config.voice.wake_word_enabled = self.cb_wake_word.isChecked()
        config.voice.wake_word_sensitivity = self.slider_sens.value() / 100.0
        config.voice.voice_rate = self.slider_rate.value()
        timeout_map = {0: 5, 1: 10, 2: 20, 3: 30}
        config.voice.conversation_timeout_sec = timeout_map.get(self.combo_timeout.currentIndex(), 10)

        # Update AI
        config.ai.gemini_model = self.combo_model.currentText()
        config.ai.gemini_api_key = self.edit_api_key.text().strip()
        config.ai.allow_online_reasoning = self.cb_online_reasoning.isChecked()

        # Update Security
        config.security.require_confirmation_for_dangerous = self.cb_confirm_dangerous.isChecked()
        config.security.allow_advanced_automation = self.cb_advanced_auto.isChecked()
        config.security.allow_file_operations = self.cb_allow_files.isChecked()
        config.security.dry_run_mode = self.cb_dry_run.isChecked()

        # Update Memory
        memory_manager.enabled = self.cb_enable_memory.isChecked()

        # Update Diagnostics
        config.diagnostics.log_level = self.combo_log_level.currentText()

        log_event("SETTINGS", "User preferences updated successfully.")
        QMessageBox.information(self, "Settings Saved", "Preferences have been updated.")
        self.accept()

    def _export_memory(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export Memory", "edith_memory_export.json", "JSON Files (*.json)")
        if path:
            import json
            data = memory_manager.export_memory()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, "Export Successful", f"Memory exported to:\n{path}")

    def _clear_memory(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear Memory",
            "Are you sure you want to wipe all conversation logs, aliases, and preferences?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            memory_manager.wipe_all()
            QMessageBox.information(self, "Memory Cleared", "SQLite memory wiped successfully.")

    def _open_logs_dir(self) -> None:
        folder = str(config.logs_dir)
        if os.name == "nt":
            os.startfile(folder)
        else:
            import subprocess
            subprocess.Popen(["xdg-open", folder])

    def _test_speaker(self) -> None:
        from voice.text_to_speech import WindowsSapi5TTSProvider
        tts = WindowsSapi5TTSProvider(rate=self.slider_rate.value())
        tts.speak("Audio output test. EDITH audio subsystem functioning normally.")
