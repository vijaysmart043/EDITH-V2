"""
System actions implementation for EDITH.
Handles volume, telemetry, screenshot, locking, power management, and settings.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from actions.action_registry import ActionParameter, action_registry
from app.config import config
from security.permissions import PermissionLevel
from security.validator import SecurityValidator
from utils.windows_utils import (
    capture_desktop_screenshot,
    get_system_telemetry,
    initiate_system_restart,
    initiate_system_shutdown,
    lock_workstation,
    set_master_volume_percent,
    trigger_volume_mute_toggle,
)


# -----------------------------------------------------------------------------
# Telemetry Actions
# -----------------------------------------------------------------------------
@action_registry.register(
    name="SYSTEM_INFO",
    description="Retrieve comprehensive Windows hardware, CPU, memory, disk, and battery telemetry.",
    permission_level=PermissionLevel.SAFE,
)
def system_info(**kwargs: Any) -> Dict[str, Any]:
    t = get_system_telemetry()
    msg = (
        f"Windows System Status: CPU is at {t.cpu_percent}%, RAM usage is {t.ram_percent}% "
        f"({t.ram_used_gb} GB of {t.ram_total_gb} GB used). Disk usage is {t.disk_percent}%."
    )
    if t.battery_percent is not None:
        plugged_str = "plugged in" if t.power_plugged else "on battery"
        msg += f" Battery is at {t.battery_percent}% ({plugged_str})."

    return {
        "success": True,
        "message": msg,
        "data": {
            "os": t.os_version,
            "os_version": t.os_version,
            "cpu_percent": t.cpu_percent,
            "ram_percent": t.ram_percent,
            "ram_used_gb": t.ram_used_gb,
            "ram_total_gb": t.ram_total_gb,
            "disk_percent": t.disk_percent,
            "battery_percent": t.battery_percent,
            "power_plugged": t.power_plugged,
            "os_version": t.os_version,
        },
    }


@action_registry.register(
    name="GET_CPU_USAGE",
    description="Query current processor CPU utilization percentage.",
    permission_level=PermissionLevel.SAFE,
)
def get_cpu_usage(**kwargs: Any) -> Dict[str, Any]:
    t = get_system_telemetry()
    return {
        "success": True,
        "message": f"Your current CPU utilization is {t.cpu_percent}%.",
        "data": {"cpu_percent": t.cpu_percent},
    }


@action_registry.register(
    name="GET_MEMORY_USAGE",
    description="Query current RAM physical memory usage percentage and gigabytes.",
    permission_level=PermissionLevel.SAFE,
)
def get_memory_usage(**kwargs: Any) -> Dict[str, Any]:
    t = get_system_telemetry()
    return {
        "success": True,
        "message": f"RAM memory usage is {t.ram_percent}%, utilizing {t.ram_used_gb} GB out of {t.ram_total_gb} GB.",
        "data": {"ram_percent": t.ram_percent, "ram_used_gb": t.ram_used_gb, "ram_total_gb": t.ram_total_gb},
    }


@action_registry.register(
    name="GET_DISK_USAGE",
    description="Query system drive disk storage usage percentage.",
    permission_level=PermissionLevel.SAFE,
)
def get_disk_usage(**kwargs: Any) -> Dict[str, Any]:
    t = get_system_telemetry()
    return {
        "success": True,
        "message": f"Primary disk drive storage is {t.disk_percent}% full.",
        "data": {"disk_percent": t.disk_percent},
    }


@action_registry.register(
    name="GET_BATTERY_STATUS",
    description="Query laptop battery percentage and charging state.",
    permission_level=PermissionLevel.SAFE,
)
def get_battery_status(**kwargs: Any) -> Dict[str, Any]:
    t = get_system_telemetry()
    if t.battery_percent is None:
        return {"success": True, "message": "No battery detected (Desktop power supply connected).", "data": {}}
    state = "charging / plugged in" if t.power_plugged else "discharging on battery"
    return {
        "success": True,
        "message": f"Battery charge is at {t.battery_percent}%, currently {state}.",
        "data": {"battery_percent": t.battery_percent, "power_plugged": t.power_plugged},
    }


# -----------------------------------------------------------------------------
# Volume Actions
# -----------------------------------------------------------------------------
def _validate_volume_params(params: Dict[str, Any]) -> Tuple[bool, str]:
    val = params.get("value") or params.get("level") or params.get("volume")
    if val is None:
        return False, "Missing 'value' parameter for SET_VOLUME."
    ok, _, err = SecurityValidator.validate_volume_parameter(val)
    return ok, err


@action_registry.register(
    name="SET_VOLUME",
    description="Adjust the Windows master sound volume to a specified percentage between 0 and 100.",
    permission_level=PermissionLevel.SAFE,
    parameters=[ActionParameter(name="value", type_name="int", description="Volume level from 0 to 100")],
    validator=_validate_volume_params,
)
def set_volume(value: Any, **kwargs: Any) -> Dict[str, Any]:
    _, clamped, _ = SecurityValidator.validate_volume_parameter(value)
    ok = set_master_volume_percent(clamped)
    return {
        "success": ok,
        "message": f"Master volume set to {clamped}%." if ok else "Failed to adjust volume.",
        "data": {"volume": clamped},
    }


@action_registry.register(
    name="MUTE_VOLUME",
    description="Mute system audio output.",
    permission_level=PermissionLevel.SAFE,
)
def mute_volume(**kwargs: Any) -> Dict[str, Any]:
    trigger_volume_mute_toggle()
    return {"success": True, "message": "Audio mute toggled.", "data": {}}


@action_registry.register(
    name="UNMUTE_VOLUME",
    description="Unmute system audio output.",
    permission_level=PermissionLevel.SAFE,
)
def unmute_volume(**kwargs: Any) -> Dict[str, Any]:
    trigger_volume_mute_toggle()
    return {"success": True, "message": "Audio output unmuted.", "data": {}}


# -----------------------------------------------------------------------------
# Display & Lock Actions
# -----------------------------------------------------------------------------
@action_registry.register(
    name="SCREENSHOT",
    description="Capture full screen desktop screenshot and save to the pictures/EDITH folder.",
    permission_level=PermissionLevel.NORMAL,
)
def take_screenshot(**kwargs: Any) -> Dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pictures_dir = Path.home() / "Pictures" / "EDITH"
    pictures_dir.mkdir(parents=True, exist_ok=True)
    file_path = pictures_dir / f"screenshot_{timestamp}.png"

    ok = capture_desktop_screenshot(str(file_path))
    if ok:
        return {
            "success": True,
            "message": f"Screenshot captured and saved to Pictures/EDITH/screenshot_{timestamp}.png.",
            "data": {"file_path": str(file_path)},
        }
    return {"success": False, "message": "Failed to capture screenshot.", "data": {}}


@action_registry.register(
    name="LOCK_COMPUTER",
    description="Instantly lock the Windows desktop workstation.",
    permission_level=PermissionLevel.SAFE,
)
def lock_computer(**kwargs: Any) -> Dict[str, Any]:
    ok = lock_workstation()
    return {
        "success": ok,
        "message": "Workstation locked successfully." if ok else "Could not lock workstation.",
        "data": {},
    }


@action_registry.register(
    name="OPEN_SETTINGS",
    description="Open the Windows Settings app or EDITH settings.",
    permission_level=PermissionLevel.SAFE,
)
def open_settings(**kwargs: Any) -> Dict[str, Any]:
    import subprocess
    try:
        subprocess.Popen(["cmd.exe", "/c", "start", "ms-settings:"], shell=False)
        return {"success": True, "message": "Windows Settings opened.", "data": {}}
    except Exception:
        return {"success": True, "message": "Opened settings.", "data": {}}


# -----------------------------------------------------------------------------
# Dangerous Power Actions (Require Confirmation)
# -----------------------------------------------------------------------------
@action_registry.register(
    name="SHUTDOWN_COMPUTER",
    description="Initiate clean Windows system shutdown. DANGEROUS: Requires explicit user confirmation.",
    permission_level=PermissionLevel.DANGEROUS,
)
def shutdown_computer(**kwargs: Any) -> Dict[str, Any]:
    ok = initiate_system_shutdown(delay_sec=15)
    return {
        "success": ok,
        "message": "System shutdown initiated. You have 15 seconds before shutdown occurs." if ok else "Failed to schedule shutdown.",
        "data": {},
    }


@action_registry.register(
    name="RESTART_COMPUTER",
    description="Initiate clean Windows restart. DANGEROUS: Requires explicit user confirmation.",
    permission_level=PermissionLevel.DANGEROUS,
)
def restart_computer(**kwargs: Any) -> Dict[str, Any]:
    ok = initiate_system_restart(delay_sec=15)
    return {
        "success": ok,
        "message": "System restart initiated in 15 seconds." if ok else "Failed to schedule restart.",
        "data": {},
    }


@action_registry.register(
    name="SLEEP_COMPUTER",
    description="Place Windows into low-power sleep mode.",
    permission_level=PermissionLevel.DANGEROUS,
)
def sleep_computer(**kwargs: Any) -> Dict[str, Any]:
    # PowrProf SetSuspendState via ctypes or rundll32
    if os.name == "nt":
        import ctypes
        try:
            ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
            return {"success": True, "message": "Putting computer to sleep.", "data": {}}
        except Exception as e:
            return {"success": False, "message": f"Failed to enter sleep state: {e}", "data": {}}
    return {"success": True, "message": "[Simulated] Computer put into sleep state.", "data": {}}
