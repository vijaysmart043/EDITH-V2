"""
Application Configuration Manager for EDITH.
Handles environment variables, runtime paths (including PyInstaller bundled paths),
user preferences, and persistent configuration.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

# Load local environment if python-dotenv is present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_base_dir() -> Path:
    """Return the application base directory, handling PyInstaller _MEIPASS bundle path."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def get_user_data_dir() -> Path:
    """Return the user local app data directory for EDITH data persistence."""
    if os.name == "nt":
        app_data = os.getenv("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
        base = Path(app_data) / "EDITH"
    else:
        base = Path.home() / ".edith"
    base.mkdir(parents=True, exist_ok=True)
    return base


@dataclass
class GeneralConfig:
    start_with_windows: bool = False
    start_minimized: bool = True
    theme: str = "futuristic_dark"
    developer_name: str = "G.Vijay Raj (vijay smart)"


@dataclass
class VoiceConfig:
    wake_word_enabled: bool = True
    wake_word: str = "Hey EDITH"
    wake_word_sensitivity: float = 0.65
    microphone_index: Optional[int] = None
    voice_rate: int = 185
    voice_volume: float = 0.95
    voice_gender: str = "female"  # "female" or "male"
    stt_provider: str = "local_whisper"  # "local_whisper", "google", "vosk"
    tts_provider: str = "sapi5"  # "sapi5", "pyttsx3", "edge_tts"
    conversation_timeout_sec: int = 10
    cooldown_sec: float = 1.2


@dataclass
class AIConfig:
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    temperature: float = 0.2
    max_tokens: int = 500
    allow_online_reasoning: bool = True


@dataclass
class SecurityConfig:
    require_confirmation_for_dangerous: bool = True
    allow_advanced_automation: bool = False
    allow_file_operations: bool = True
    dry_run_mode: bool = field(default_factory=lambda: os.getenv("DRY_RUN_MODE", "false").lower() == "true")


@dataclass
class DiagnosticsConfig:
    log_level: str = field(default_factory=lambda: os.getenv("EDITH_LOG_LEVEL", "INFO"))
    enable_console_logging: bool = True
    enable_file_logging: bool = True


class AppConfig:
    """Master Application Configuration container."""

    def __init__(self) -> None:
        self.base_dir: Path = get_base_dir()
        self.data_dir: Path = get_user_data_dir()
        self.logs_dir: Path = self.data_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.db_path: Path = self.data_dir / "edith_memory.sqlite3"
        self.assets_dir: Path = self.base_dir / "assets"

        self.general: GeneralConfig = GeneralConfig()
        self.voice: VoiceConfig = VoiceConfig()
        self.ai: AIConfig = AIConfig()
        self.security: SecurityConfig = SecurityConfig()
        self.diagnostics: DiagnosticsConfig = DiagnosticsConfig()

    def reload_from_dict(self, data: Dict[str, Any]) -> None:
        """Update settings from a dictionary (e.g., loaded from SQLite or JSON)."""
        if "general" in data and isinstance(data["general"], dict):
            for k, v in data["general"].items():
                if hasattr(self.general, k):
                    setattr(self.general, k, v)
        if "voice" in data and isinstance(data["voice"], dict):
            for k, v in data["voice"].items():
                if hasattr(self.voice, k):
                    setattr(self.voice, k, v)
        if "ai" in data and isinstance(data["ai"], dict):
            for k, v in data["ai"].items():
                if hasattr(self.ai, k):
                    setattr(self.ai, k, v)
        if "security" in data and isinstance(data["security"], dict):
            for k, v in data["security"].items():
                if hasattr(self.security, k):
                    setattr(self.security, k, v)


# Global singleton instance
config = AppConfig()
