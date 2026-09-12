"""
Network Actions for EDITH.
Queries WiFi connection status and validates internet reachability.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import socket
import subprocess
from typing import Any, Dict

from actions.action_registry import action_registry
from security.permissions import PermissionLevel
from utils.windows_utils import is_windows


def _has_internet() -> bool:
    try:
        # Connect to Google Public DNS
        socket.setdefaulttimeout(3.0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("8.8.8.8", 53))
        s.close()
        return True
    except Exception:
        return False


@action_registry.register(
    name="GET_WIFI_STATUS",
    description="Check active WiFi network SSID and connection strength.",
    permission_level=PermissionLevel.SAFE,
)
def get_wifi_status(**kwargs: Any) -> Dict[str, Any]:
    online = _has_internet()

    if is_windows():
        try:
            res = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = res.stdout
            ssid = "Unknown"
            signal = "Unknown"
            for line in output.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                elif "Signal" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        signal = parts[1].strip()

            msg = f"WiFi network: '{ssid}' with {signal} signal. Internet is {'connected' if online else 'offline'}."
            return {
                "success": True,
                "message": msg,
                "data": {"ssid": ssid, "signal": signal, "online": online},
            }
        except Exception:
            pass

    return {
        "success": True,
        "message": f"Network is {'online' if online else 'offline'}.",
        "data": {"online": online},
    }
