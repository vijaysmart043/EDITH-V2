"""
Media Playback Control Actions for EDITH.
Simulates global Windows multimedia keyboard inputs.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

from typing import Any, Dict

from actions.action_registry import action_registry
from security.permissions import PermissionLevel
from utils.windows_utils import (
    trigger_media_next,
    trigger_media_play_pause,
    trigger_media_previous,
)


@action_registry.register(
    name="PLAY_MEDIA",
    description="Resume or toggle audio/video playback.",
    permission_level=PermissionLevel.SAFE,
)
def play_media(**kwargs: Any) -> Dict[str, Any]:
    trigger_media_play_pause()
    return {"success": True, "message": "Media playback toggled.", "data": {}}


@action_registry.register(
    name="PAUSE_MEDIA",
    description="Pause ongoing media playback.",
    permission_level=PermissionLevel.SAFE,
)
def pause_media(**kwargs: Any) -> Dict[str, Any]:
    trigger_media_play_pause()
    return {"success": True, "message": "Media playback paused.", "data": {}}


@action_registry.register(
    name="NEXT_MEDIA",
    description="Skip to the next audio track or video.",
    permission_level=PermissionLevel.SAFE,
)
def next_media(**kwargs: Any) -> Dict[str, Any]:
    trigger_media_next()
    return {"success": True, "message": "Skipped to next track.", "data": {}}


@action_registry.register(
    name="PREVIOUS_MEDIA",
    description="Return to previous audio track.",
    permission_level=PermissionLevel.SAFE,
)
def previous_media(**kwargs: Any) -> Dict[str, Any]:
    trigger_media_previous()
    return {"success": True, "message": "Skipped to previous track.", "data": {}}
