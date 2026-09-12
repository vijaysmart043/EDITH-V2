"""
Safe Per-User Windows Startup Manager for EDITH.
Configures automatic startup upon user login without requiring Administrator privileges.
Uses HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from app.logging_config import log_event

REGISTRY_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "EDITH_Assistant"


class WindowsStartupManager:
    """Configures and inspects per-user Windows login startup state."""

    @staticmethod
    def get_executable_command() -> str:
        """Get the full command line to start EDITH minimized upon login."""
        if getattr(sys, "frozen", False):
            # Bundled with PyInstaller as EDITH.exe
            exe_path = Path(sys.executable).resolve()
            return f'"{exe_path}" --minimized'
        else:
            # Running as Python script
            python_exe = Path(sys.executable).resolve()
            main_py = Path(__file__).resolve().parent.parent / "main.py"
            return f'"{python_exe}" "{main_py}" --minimized'

    @classmethod
    def is_startup_enabled(cls) -> bool:
        """Check if EDITH is registered in HKCU Run registry."""
        if os.name != "nt":
            return False

        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH, 0, winreg.KEY_READ) as key:
                try:
                    val, _ = winreg.QueryValueEx(key, APP_NAME)
                    return bool(val)
                except FileNotFoundError:
                    return False
        except Exception as e:
            log_event("STARTUP", f"Failed reading registry startup key: {e}")
            return False

    @classmethod
    def enable_startup(cls) -> bool:
        """Add EDITH to HKCU Run key so it starts minimized automatically."""
        if os.name != "nt":
            log_event("STARTUP", "[Simulated] Startup enabled in test mode.")
            return True

        cmd = cls.get_executable_command()
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                log_event("STARTUP", f"Successfully registered startup in HKCU: {cmd}")
                return True
        except Exception as e:
            log_event("STARTUP", f"Failed writing registry startup key: {e}")
            return False

    @classmethod
    def disable_startup(cls) -> bool:
        """Remove EDITH from HKCU Run key."""
        if os.name != "nt":
            log_event("STARTUP", "[Simulated] Startup disabled in test mode.")
            return True

        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    log_event("STARTUP", "Successfully removed EDITH from HKCU startup.")
                    return True
                except FileNotFoundError:
                    return True  # Already not present
        except Exception as e:
            log_event("STARTUP", f"Failed deleting registry startup key: {e}")
            return False
