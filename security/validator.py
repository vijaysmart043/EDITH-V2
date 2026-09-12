"""
Security Validator for EDITH.
Ensures path traversal prevention, parameter sanitization,
blacklist enforcement, and strict schema validation.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from security.permissions import DANGEROUS_ACTIONS, PermissionLevel

# Disallowed dangerous executables or system commands
BLOCKED_EXECUTABLES: Set[str] = {
    "format.com",
    "format.exe",
    "diskpart.exe",
    "regedit.exe",
    "reg.exe",
    "bcdedit.exe",
    "vssadmin.exe",
    "cipher.exe",
    "takeown.exe",
    "icacls.exe",
    "attrib.exe",
}

# Protected system paths that must never be targeted for file modification/deletion
PROTECTED_PATH_PREFIXES = [
    r"C:\Windows",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Boot",
    r"C:\Recovery",
    r"/etc",
    r"/boot",
    r"/sys",
    r"/proc",
    r"/bin",
    r"/sbin",
]


class ValidationResult:
    """Outcome of a security validation check."""

    def __init__(self, is_valid: bool, error_message: str = "", requires_confirmation: bool = False) -> None:
        self.is_valid = is_valid
        self.error_message = error_message
        self.requires_confirmation = requires_confirmation

    def __bool__(self) -> bool:
        return self.is_valid


class SecurityValidator:
    """Validates intents, action targets, and parameters before execution."""

    @classmethod
    def is_executable_safe(cls, executable: str) -> bool:
        """Check whether an executable string or command is safe to execute."""
        res = cls.validate_action_target("OPEN_APPLICATION", executable)
        return bool(res.is_valid)

    @staticmethod
    def validate_action_target(action_name: str, target: Optional[str]) -> ValidationResult:
        """Validate the target string (e.g. executable name, app alias, or URL)."""
        if not target:
            return ValidationResult(True)

        target_lower = target.strip().lower()

        # Check for blocked executables
        for blocked in BLOCKED_EXECUTABLES:
            if blocked in target_lower:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Security Alert: Execution of prohibited binary '{target}' is blocked.",
                )

        # Check for obfuscated or dangerous PowerShell execution flags
        if "powershell" in target_lower and any(flag in target_lower for flag in ["-enc", "-encodedcommand", "downloadstring", "invoke-expression", "iex", "-w hidden", "-nop"]):
            return ValidationResult(
                is_valid=False,
                error_message="Security Alert: Obfuscated or dangerous PowerShell execution flag detected.",
            )

        # Disallow arbitrary bash / cmd / powershell piping attacks
        suspicious_symbols = [";", "&&", "||", "|", "`", "$", "<", ">", "%", "\n", "\r"]
        for sym in suspicious_symbols:
            if sym in target and action_name not in {"SEARCH_WEB", "OPEN_URL"}:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Security Alert: Disallowed character '{sym}' detected in command target.",
                )

        return ValidationResult(True)

    @staticmethod
    def validate_file_path(file_path_str: str, check_writable: bool = False) -> ValidationResult:
        """Prevent directory traversal, null byte injections, and system directory modifications."""
        if not file_path_str:
            return ValidationResult(False, "File path cannot be empty.")

        # Check for null bytes
        if "\0" in file_path_str:
            return ValidationResult(False, "Security Alert: Null byte in file path.")

        # Prevent directory traversal
        if ".." in file_path_str:
            return ValidationResult(False, "Security Alert: Path traversal sequence ('..') detected.")

        try:
            resolved = Path(file_path_str).resolve()
        except Exception as e:
            return ValidationResult(False, f"Invalid path syntax: {e}")

        resolved_str = str(resolved).lower()

        # Disallow targeting protected Windows directories
        for protected in PROTECTED_PATH_PREFIXES:
            if resolved_str.startswith(protected.lower()):
                return ValidationResult(
                    False,
                    f"Security Alert: Target path resides inside protected system directory '{protected}'.",
                )

        return ValidationResult(True)

    @staticmethod
    def validate_volume_parameter(value: Any) -> Tuple[bool, int, str]:
        """Validate and clamp audio volume between 0 and 100."""
        try:
            val_int = int(value)
            clamped = max(0, min(100, val_int))
            return True, clamped, ""
        except (ValueError, TypeError):
            return False, 0, f"Invalid volume level: '{value}'. Expected an integer between 0 and 100."

    @staticmethod
    def check_permissions(
        action_name: str,
        permission_level: PermissionLevel,
        require_confirmation_setting: bool,
        advanced_automation_setting: bool,
    ) -> ValidationResult:
        """Determine if an action requires explicit confirmation or is outright denied."""
        # If action is inherently dangerous
        if action_name in DANGEROUS_ACTIONS or permission_level == PermissionLevel.DANGEROUS:
            if advanced_automation_setting:
                # Advanced automation bypass enabled by user in settings
                return ValidationResult(True, requires_confirmation=False)
            if require_confirmation_setting:
                return ValidationResult(True, requires_confirmation=True)

        return ValidationResult(True, requires_confirmation=False)
