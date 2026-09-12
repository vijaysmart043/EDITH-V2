"""
Browser and Web Searching Actions for EDITH.
Launches default web browser and executes secure web searches without shell injection.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import urllib.parse
import webbrowser
from typing import Any, Dict, Tuple

from actions.action_registry import ActionParameter, action_registry
from security.permissions import PermissionLevel


def _validate_query(params: Dict[str, Any]) -> Tuple[bool, str]:
    q = params.get("query") or params.get("target") or params.get("search_term")
    if not q or not str(q).strip():
        return False, "Search query is required."
    return True, ""


@action_registry.register(
    name="OPEN_BROWSER",
    description="Launch the default internet web browser.",
    permission_level=PermissionLevel.NORMAL,
)
def open_browser(**kwargs: Any) -> Dict[str, Any]:
    try:
        webbrowser.open("https://www.google.com")
        return {"success": True, "message": "Browser opened.", "data": {}}
    except Exception as e:
        return {"success": False, "message": f"Could not launch browser: {e}", "data": {}}


@action_registry.register(
    name="SEARCH_WEB",
    description="Search Google, YouTube, or web for a given topic or query.",
    permission_level=PermissionLevel.NORMAL,
    parameters=[
        ActionParameter(name="query", type_name="str", description="Search query keywords"),
        ActionParameter(name="engine", type_name="str", required=False, default="google", description="google or youtube"),
    ],
    validator=_validate_query,
)
def search_web(query: str, engine: str = "google", **kwargs: Any) -> Dict[str, Any]:
    encoded = urllib.parse.quote_plus(query.strip())
    if engine.lower() == "youtube" or "youtube" in query.lower():
        url = f"https://www.youtube.com/results?search_query={encoded}"
        label = "YouTube"
    else:
        url = f"https://www.google.com/search?q={encoded}"
        label = "Google"

    try:
        webbrowser.open(url)
        return {
            "success": True,
            "message": f"Opening {label} search for '{query}'.",
            "data": {"query": query, "url": url},
        }
    except Exception as e:
        return {"success": False, "message": f"Failed opening browser: {e}", "data": {}}


@action_registry.register(
    name="OPEN_URL",
    description="Navigate to a specific web URL.",
    permission_level=PermissionLevel.NORMAL,
    parameters=[ActionParameter(name="url", type_name="str", description="Full web address")],
)
def open_url(url: str, **kwargs: Any) -> Dict[str, Any]:
    target_url = url.strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    try:
        webbrowser.open(target_url)
        return {"success": True, "message": f"Navigating to {target_url}.", "data": {"url": target_url}}
    except Exception as e:
        return {"success": False, "message": f"Failed opening URL: {e}", "data": {}}
