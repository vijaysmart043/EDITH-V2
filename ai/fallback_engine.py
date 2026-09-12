"""
Offline Deterministic Fallback Engine for EDITH.
Resolves natural language commands directly to structured intents using regex and keyword heuristics
without requiring any network connection or Gemini API call.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import re
from typing import Optional

from ai.schemas import IntentResult


class FallbackEngine:
    """Deterministic local parser for offline-first actions."""

    def parse(self, text: str) -> Optional[IntentResult]:
        """Attempt to match natural language user input against deterministic rules."""
        if not text:
            return None

        clean = text.strip().lower()
        # Remove wake word if present in prefix
        clean = re.sub(r"^(hey\s+)?edith[,.\s]*", "", clean).strip()

        # 1. Volume Controls
        # "Set volume to 50", "Turn volume down to 40", "Turn volume to 80%"
        m_vol = re.search(r"(?:set|change|turn|adjust)?\s*(?:the\s+)?volume\s+(?:up\s+to|down\s+to|to)?\s*(\d{1,3})%?", clean)
        if m_vol:
            val = int(m_vol.group(1))
            return IntentResult(
                intent="SET_VOLUME",
                target="system",
                parameters={"value": val},
                confidence=0.99,
                conversational_response=f"Setting volume to {val} percent.",
                raw_query=text,
            )

        if any(w in clean for w in ["volume down", "lower the volume", "reduce volume", "turn down volume"]):
            return IntentResult(
                intent="SET_VOLUME",
                target="system",
                parameters={"value": 30},
                confidence=0.95,
                conversational_response="Lowering volume.",
                raw_query=text,
            )

        if any(w in clean for w in ["volume up", "raise the volume", "increase volume", "turn up volume"]):
            return IntentResult(
                intent="SET_VOLUME",
                target="system",
                parameters={"value": 80},
                confidence=0.95,
                conversational_response="Increasing volume.",
                raw_query=text,
            )

        if any(w in clean for w in ["mute audio", "mute volume", "mute sound", "mute computer", "mute"]):
            return IntentResult(
                intent="MUTE_VOLUME",
                target="system",
                parameters={},
                confidence=0.98,
                conversational_response="Muting audio.",
                raw_query=text,
            )

        if any(w in clean for w in ["unmute", "unmute audio", "unmute volume"]):
            return IntentResult(
                intent="UNMUTE_VOLUME",
                target="system",
                parameters={},
                confidence=0.98,
                conversational_response="Unmuting audio.",
                raw_query=text,
            )

        # 2. System Telemetry
        if any(w in clean for w in ["cpu usage", "processor usage", "cpu status", "how is the cpu"]):
            return IntentResult(
                intent="GET_CPU_USAGE",
                target="system",
                confidence=0.98,
                raw_query=text,
            )

        if any(w in clean for w in ["ram usage", "memory usage", "how much ram", "memory status"]):
            return IntentResult(
                intent="GET_MEMORY_USAGE",
                target="system",
                confidence=0.98,
                raw_query=text,
            )

        if any(w in clean for w in ["battery status", "battery level", "battery percent", "how much battery"]):
            return IntentResult(
                intent="GET_BATTERY_STATUS",
                target="system",
                confidence=0.98,
                raw_query=text,
            )

        if any(w in clean for w in ["disk usage", "disk space", "storage space", "how much storage"]):
            return IntentResult(
                intent="GET_DISK_USAGE",
                target="system",
                confidence=0.98,
                raw_query=text,
            )

        if any(w in clean for w in ["system info", "system status", "system diagnostics", "pc status"]):
            return IntentResult(
                intent="SYSTEM_INFO",
                target="system",
                confidence=0.97,
                raw_query=text,
            )

        if any(w in clean for w in ["wifi status", "wifi signal", "network status", "internet status"]):
            return IntentResult(
                intent="GET_WIFI_STATUS",
                target="network",
                confidence=0.97,
                raw_query=text,
            )

        # 3. Screenshot & Lock
        if any(w in clean for w in ["take a screenshot", "take screenshot", "capture screen", "screenshot"]):
            return IntentResult(
                intent="SCREENSHOT",
                target="display",
                confidence=0.99,
                conversational_response="Capturing screenshot.",
                raw_query=text,
            )

        if any(w in clean for w in ["lock computer", "lock pc", "lock screen", "lock workstation", "lock the pc"]):
            return IntentResult(
                intent="LOCK_COMPUTER",
                target="system",
                confidence=0.99,
                conversational_response="Locking workstation.",
                raw_query=text,
            )

        # 4. Dangerous Actions
        if any(w in clean for w in ["shutdown computer", "shut down", "turn off the pc", "shutdown the pc"]):
            return IntentResult(
                intent="SHUTDOWN_COMPUTER",
                target="system",
                requires_confirmation=True,
                confidence=0.99,
                conversational_response="System shutdown requested. Awaiting confirmation.",
                raw_query=text,
            )

        if any(w in clean for w in ["restart computer", "reboot computer", "restart the pc", "reboot the pc"]):
            return IntentResult(
                intent="RESTART_COMPUTER",
                target="system",
                requires_confirmation=True,
                confidence=0.99,
                conversational_response="System restart requested. Awaiting confirmation.",
                raw_query=text,
            )

        if any(w in clean for w in ["sleep computer", "put pc to sleep", "suspend computer"]):
            return IntentResult(
                intent="SLEEP_COMPUTER",
                target="system",
                requires_confirmation=True,
                confidence=0.98,
                conversational_response="Sleep mode requested. Awaiting confirmation.",
                raw_query=text,
            )

        # 5. Media Controls
        if any(w in clean for w in ["pause media", "pause music", "pause video", "pause song"]):
            return IntentResult(intent="PAUSE_MEDIA", target="media", confidence=0.97, raw_query=text)

        if any(w in clean for w in ["play media", "play music", "resume music", "resume playback"]):
            return IntentResult(intent="PLAY_MEDIA", target="media", confidence=0.97, raw_query=text)

        if any(w in clean for w in ["next track", "next song", "skip track", "skip song", "next media"]):
            return IntentResult(intent="NEXT_MEDIA", target="media", confidence=0.97, raw_query=text)

        if any(w in clean for w in ["previous track", "previous song", "last song"]):
            return IntentResult(intent="PREVIOUS_MEDIA", target="media", confidence=0.97, raw_query=text)

        # 6. Web & Search
        m_yt = re.search(r"search\s+youtube\s+for\s+(.+)", clean)
        if m_yt:
            query = m_yt.group(1).strip()
            return IntentResult(
                intent="SEARCH_WEB",
                target="youtube",
                parameters={"query": query, "engine": "youtube"},
                confidence=0.99,
                conversational_response=f"Searching YouTube for {query}.",
                raw_query=text,
            )

        m_search = re.search(r"(?:search\s+(?:google|the\s+web)?\s*for|google)\s+(.+)", clean)
        if m_search:
            query = m_search.group(1).strip()
            return IntentResult(
                intent="SEARCH_WEB",
                target="google",
                parameters={"query": query, "engine": "google"},
                confidence=0.98,
                conversational_response=f"Searching Google for {query}.",
                raw_query=text,
            )

        # 7. Application Launching & Termination
        m_close = re.search(r"(?:close|exit|terminate|kill|quit)\s+([a-zA-Z0-9\s]+)", clean)
        if m_close:
            app_target = m_close.group(1).strip()
            return IntentResult(
                intent="CLOSE_APPLICATION",
                target=app_target,
                parameters={"target": app_target},
                confidence=0.96,
                conversational_response=f"Closing {app_target}.",
                raw_query=text,
            )

        m_open = re.search(r"(?:open|launch|start|run)\s+(?:my\s+)?([a-zA-Z0-9\s]+)", clean)
        if m_open:
            app_target = m_open.group(1).strip()
            if app_target in ["settings", "windows settings"]:
                return IntentResult(intent="OPEN_SETTINGS", target="settings", confidence=0.98, raw_query=text)
            if app_target in ["browser", "web browser", "internet"]:
                return IntentResult(intent="OPEN_BROWSER", target="browser", confidence=0.98, raw_query=text)
            return IntentResult(
                intent="OPEN_APPLICATION",
                target=app_target,
                parameters={"target": app_target},
                confidence=0.95,
                conversational_response=f"Opening {app_target}.",
                raw_query=text,
            )

        # 8. Creator / Identity
        if any(w in clean for w in ["who made you", "who created you", "who developed you", "your developer"]):
            return IntentResult(
                intent="CONVERSATION",
                confidence=1.0,
                conversational_response="I am EDITH (Enhanced Digital Intelligence & Task Handler), architected and developed by G.Vijay Raj (vijay smart).",
                raw_query=text,
            )

        return None


fallback_engine = FallbackEngine()
