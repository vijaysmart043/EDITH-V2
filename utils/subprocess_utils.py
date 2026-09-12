"""
Safe Subprocess Execution Utilities for EDITH.
Enforces execution timeouts, disallows untrusted shell execution,
and handles stdout/stderr streaming safely.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
import subprocess
from typing import List, Optional, Tuple

from app.logging_config import log_event


def safe_run_command(
    args: List[str],
    timeout_sec: float = 10.0,
    cwd: Optional[str] = None,
) -> Tuple[bool, str, str]:
    """
    Safely execute a command without shell=True to prevent shell injection.
    Returns (success, stdout, stderr).
    """
    if not args:
        return False, "", "Empty argument list provided."

    log_event("SUBPROCESS", f"Executing safe command: {args[0]} with {len(args)-1} parameters")

    try:
        # Create process without a visible console window on Windows
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

        result = subprocess.run(
            args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=cwd,
            creationflags=creationflags,
        )
        success = result.returncode == 0
        return success, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        log_event("SUBPROCESS", f"Command timed out after {timeout_sec}s: {args[0]}")
        return False, "", f"Operation timed out after {timeout_sec} seconds."
    except FileNotFoundError:
        log_event("SUBPROCESS", f"Target executable not found: {args[0]}")
        return False, "", f"Executable '{args[0]}' was not found on system path."
    except Exception as e:
        log_event("SUBPROCESS", f"Subprocess error executing {args[0]}: {e}")
        return False, "", str(e)


def safe_launch_process(args: List[str], cwd: Optional[str] = None) -> Tuple[bool, str]:
    """Launch a detached background GUI application (e.g. Chrome, Notepad)."""
    if not args:
        return False, "No arguments specified."

    try:
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]

        subprocess.Popen(
            args,
            shell=False,
            cwd=cwd,
            creationflags=creationflags,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True, f"Launched '{args[0]}' successfully."
    except FileNotFoundError:
        return False, f"Executable '{args[0]}' not found."
    except Exception as e:
        return False, f"Failed to launch '{args[0]}': {e}"
