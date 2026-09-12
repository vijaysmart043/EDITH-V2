"""
Security Permission Levels and Policies for EDITH.
Categorizes actions into strict trust tiers.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from enum import Enum
from typing import Set


class PermissionLevel(str, Enum):
    """Execution security authorization level."""

    SAFE = "SAFE"                # Purely read-only or harmless (e.g. system info, time, volume change)
    NORMAL = "NORMAL"            # Standard desktop interaction (e.g. open application, play media)
    ELEVATED = "ELEVATED"        # Modifies files or user state (e.g. create file, delete non-system file)
    DANGEROUS = "DANGEROUS"      # Critical impact: shutdown, restart, lock, disk formatting, registry changes


# Explicit list of actions classified as DANGEROUS requiring mandatory user confirmation
DANGEROUS_ACTIONS: Set[str] = {
    "SHUTDOWN_COMPUTER",
    "RESTART_COMPUTER",
    "SLEEP_COMPUTER",
    "DELETE_FILE",
    "MODIFY_SYSTEM_SETTINGS",
    "EXECUTE_SCRIPT",
    "INSTALL_SOFTWARE",
    "KILL_PROCESS_FORCE",
}
