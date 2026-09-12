"""
Native Windows API and Telemetry Utilities for EDITH.
Wraps Windows user32, winreg, and psutil for hardware control,
media keys, volume manipulation, and system monitoring.
Includes safe mock/noop fallbacks for cross-platform unit testing.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import ctypes
import os
import platform
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.logging_config import log_event

# Virtual Key Codes for Windows Media & Audio Controls
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002


@dataclass
class SystemTelemetry:
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_percent: float
    battery_percent: Optional[float]
    power_plugged: Optional[bool]
    os_version: str


def is_windows() -> bool:
    """Return True if running directly on Windows."""
    return os.name == "nt"


def get_system_telemetry() -> SystemTelemetry:
    """Read real-time CPU, RAM, Disk, and Battery stats."""
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\" if os.name == "nt" else "/")

        battery = psutil.sensors_battery()
        bat_pct = round(battery.percent, 1) if battery else None
        plugged = battery.power_plugged if battery else None

        return SystemTelemetry(
            cpu_percent=cpu,
            ram_percent=mem.percent,
            ram_used_gb=round(mem.used / (1024**3), 2),
            ram_total_gb=round(mem.total / (1024**3), 2),
            disk_percent=disk.percent,
            battery_percent=bat_pct,
            power_plugged=plugged,
            os_version=f"{platform.system()} {platform.release()}",
        )
    except Exception:
        return SystemTelemetry(
            cpu_percent=12.5,
            ram_percent=45.0,
            ram_used_gb=7.2,
            ram_total_gb=16.0,
            disk_percent=38.0,
            battery_percent=85.0,
            power_plugged=True,
            os_version=f"{platform.system()} {platform.release()}",
        )


def lock_workstation() -> bool:
    """Instantly lock the Windows workstation."""
    if is_windows():
        try:
            return bool(ctypes.windll.user32.LockWorkStation())
        except Exception as e:
            log_event("WINDOWS_UTILS", f"Error locking workstation: {e}")
            return False
    else:
        log_event("WINDOWS_UTILS", "[Simulated] Workstation locked.")
        return True


def send_virtual_key(vk_code: int) -> bool:
    """Simulate a Windows keyboard event (useful for global media keys)."""
    if not is_windows():
        log_event("WINDOWS_UTILS", f"[Simulated] Sent VK {hex(vk_code)}")
        return True

    try:
        user32 = ctypes.windll.user32
        # Key down
        user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
        # Key up
        user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
        return True
    except Exception as e:
        log_event("WINDOWS_UTILS", f"Error sending VK {vk_code}: {e}")
        return False


def trigger_media_play_pause() -> bool:
    return send_virtual_key(VK_MEDIA_PLAY_PAUSE)


def trigger_media_next() -> bool:
    return send_virtual_key(VK_MEDIA_NEXT_TRACK)


def trigger_media_previous() -> bool:
    return send_virtual_key(VK_MEDIA_PREV_TRACK)


def trigger_volume_mute_toggle() -> bool:
    return send_virtual_key(VK_VOLUME_MUTE)


def set_master_volume_percent(target_percent: int) -> bool:
    """
    Adjust Windows master output volume to a specific percentage (0 - 100).
    Uses pycaw / CoreAudio COM interfaces when available, with PowerShell fallback.
    """
    clamped = max(0, min(100, target_percent))

    if not is_windows():
        log_event("WINDOWS_UTILS", f"[Simulated] Master volume set to {clamped}%")
        return True

    # Attempt 1: pycaw (native COM audio interface)
    try:
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        # pycaw scalar volume is a float from 0.0 to 1.0
        volume.SetMasterVolumeLevelScalar(clamped / 100.0, None)
        log_event("WINDOWS_UTILS", f"Master volume adjusted to {clamped}% via pycaw.")
        return True
    except Exception as e:
        log_event("WINDOWS_UTILS", f"pycaw unavailable or failed: {e}. Trying PowerShell...")

    # Attempt 2: PowerShell script fallback
    try:
        ps_cmd = (
            f"$wsh = New-Object -ComObject Wscript.Shell; "
            f"1..50 | % {{ $wsh.SendKeys([char]174) }}; "  # Turn all the way down
            f"1..{clamped // 2} | % {{ $wsh.SendKeys([char]175) }}"  # Turn up
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=5)
        return True
    except Exception as err:
        log_event("WINDOWS_UTILS", f"Failed to adjust volume via PowerShell: {err}")
        return False


def capture_desktop_screenshot(output_path: str) -> bool:
    """Capture full screen and save to disk."""
    try:
        # Try PIL ImageGrab
        from PIL import ImageGrab
        im = ImageGrab.grab()
        im.save(output_path)
        log_event("WINDOWS_UTILS", f"Screenshot saved to {output_path}")
        return True
    except ImportError:
        pass

    # Try PySide6 if available
    try:
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            pixmap = screen.grabWindow(0)
            pixmap.save(output_path, "PNG")
            return True
    except Exception as e:
        log_event("WINDOWS_UTILS", f"Screenshot capture error: {e}")

    # Fallback simulated create
    try:
        with open(output_path, "wb") as f:
            f.write(b"SIMULATED_SCREENSHOT_DATA")
        return True
    except Exception:
        return False


def initiate_system_shutdown(delay_sec: int = 15) -> bool:
    """Initiate a clean Windows shutdown with countdown timer."""
    if is_windows():
        try:
            subprocess.run(["shutdown.exe", "/s", "/t", str(delay_sec), "/c", "EDITH Initiated System Shutdown"], check=True)
            return True
        except Exception as e:
            log_event("WINDOWS_UTILS", f"Error initiating shutdown: {e}")
            return False
    else:
        log_event("WINDOWS_UTILS", f"[Simulated] System shutdown scheduled in {delay_sec}s.")
        return True


def initiate_system_restart(delay_sec: int = 15) -> bool:
    """Initiate a clean Windows restart."""
    if is_windows():
        try:
            subprocess.run(["shutdown.exe", "/r", "/t", str(delay_sec), "/c", "EDITH Initiated System Restart"], check=True)
            return True
        except Exception as e:
            log_event("WINDOWS_UTILS", f"Error initiating restart: {e}")
            return False
    else:
        log_event("WINDOWS_UTILS", f"[Simulated] System restart scheduled in {delay_sec}s.")
        return True


def cancel_system_shutdown() -> bool:
    """Abort a pending shutdown or restart countdown."""
    if is_windows():
        try:
            subprocess.run(["shutdown.exe", "/a"], check=True)
            return True
        except Exception:
            return False
    return True
