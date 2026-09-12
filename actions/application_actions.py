"""
Application Launching and Management Actions for EDITH.
Resolves custom user aliases, opens desktop programs safely,
and manages running processes using psutil.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from actions.action_registry import ActionParameter, action_registry
from memory.memory_manager import memory_manager
from security.permissions import PermissionLevel
from utils.subprocess_utils import safe_launch_process


COMMON_APP_MAP = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "firefox": "firefox.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "files": "explorer.exe",
    "taskmgr": "taskmgr.exe",
    "task manager": "taskmgr.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "code": "code.cmd",
    "vscode": "code.cmd",
    "visual studio code": "code.cmd",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "paint": "mspaint.exe",
}


def _resolve_executable_target(target: str) -> str:
    """Check custom SQLite alias, common map, or raw name."""
    clean = target.strip().lower()

    # 1. Check user memory aliases in SQLite
    alias_record = memory_manager.get_alias(clean)
    if alias_record:
        return alias_record.target_executable_or_path

    # 2. Check common app dictionary
    if clean in COMMON_APP_MAP:
        return COMMON_APP_MAP[clean]

    # 3. If ends with .exe or has path, return as is
    return target.strip()


def _validate_app_target(params: Dict[str, Any]) -> Tuple[bool, str]:
    target = params.get("target") or params.get("app_name")
    if not target or not isinstance(target, str) or not target.strip():
        return False, "Application name or target is required."
    return True, ""


@action_registry.register(
    name="OPEN_APPLICATION",
    description="Launch a desktop application or program by name or user alias.",
    permission_level=PermissionLevel.NORMAL,
    parameters=[ActionParameter(name="target", type_name="str", description="Name or alias of the application to open")],
    validator=_validate_app_target,
    default_success_response="Application launched successfully.",
    default_failure_response="Could not open the requested application.",
)
def open_application(target: str, **kwargs: Any) -> Dict[str, Any]:
    executable = _resolve_executable_target(target)

    # Windows-native startfile for protocol links or registered apps
    if os.name == "nt":
        try:
            os.startfile(executable)
            return {
                "success": True,
                "message": f"{target.capitalize()} is open.",
                "data": {"target": target, "executable": executable},
            }
        except Exception:
            # Fallback to subprocess
            pass

    # Subprocess launch
    ok, msg = safe_launch_process([executable])
    if ok:
        return {
            "success": True,
            "message": f"{target.capitalize()} is open.",
            "data": {"target": target, "executable": executable},
        }
    else:
        return {
            "success": False,
            "message": f"Unable to launch '{target}'. Please ensure it is installed or configure an alias in EDITH settings.",
            "data": {"target": target, "error": msg},
        }


@action_registry.register(
    name="CLOSE_APPLICATION",
    description="Terminate or close running instances of a specified desktop application.",
    permission_level=PermissionLevel.NORMAL,
    parameters=[ActionParameter(name="target", type_name="str", description="Name or executable of the application to close")],
    validator=_validate_app_target,
)
def close_application(target: str, **kwargs: Any) -> Dict[str, Any]:
    import psutil

    executable = _resolve_executable_target(target).lower()
    base_name = os.path.basename(executable).lower()
    if not base_name.endswith(".exe") and "." not in base_name:
        base_name += ".exe"

    closed_count = 0
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                p_name = (proc.info["name"] or "").lower()
                if p_name == base_name or target.lower() in p_name:
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        return {"success": False, "message": f"Failed while scanning processes: {e}", "data": {}}

    if closed_count > 0:
        return {
            "success": True,
            "message": f"Closed {closed_count} running process(es) for {target}.",
            "data": {"closed_count": closed_count, "target": target},
        }
    return {
        "success": False,
        "message": f"No running processes found matching '{target}'.",
        "data": {"closed_count": 0},
    }
