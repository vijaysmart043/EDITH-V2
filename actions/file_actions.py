"""
File System Actions for EDITH.
Allows file opening, searching, folder creation, and safe deletion with confirmation.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from actions.action_registry import ActionParameter, action_registry
from security.permissions import PermissionLevel
from security.validator import SecurityValidator


def _validate_file_path_param(params: Dict[str, Any]) -> Tuple[bool, str]:
    path_str = params.get("path") or params.get("target") or params.get("file_name")
    if not path_str:
        return False, "A valid path or file name is required."
    val_res = SecurityValidator.validate_file_path(str(path_str))
    return val_res.is_valid, val_res.error_message


@action_registry.register(
    name="OPEN_FILE",
    description="Open a file or folder in its default Windows program or File Explorer.",
    permission_level=PermissionLevel.NORMAL,
    parameters=[ActionParameter(name="path", type_name="str", description="Path to the file or directory")],
    validator=_validate_file_path_param,
)
def open_file(path: str, **kwargs: Any) -> Dict[str, Any]:
    target_path = Path(path).resolve()
    if not target_path.exists():
        return {"success": False, "message": f"File not found: '{path}'.", "data": {}}

    if os.name == "nt":
        os.startfile(str(target_path))
    else:
        # Cross platform fallback
        import subprocess
        subprocess.Popen(["xdg-open" if os.name == "posix" else "open", str(target_path)])

    return {"success": True, "message": f"Opened '{target_path.name}'.", "data": {"path": str(target_path)}}


@action_registry.register(
    name="CREATE_FOLDER",
    description="Create a new directory at the specified location.",
    permission_level=PermissionLevel.ELEVATED,
    parameters=[ActionParameter(name="path", type_name="str", description="Path of the directory to create")],
    validator=_validate_file_path_param,
)
def create_folder(path: str, **kwargs: Any) -> Dict[str, Any]:
    target_path = Path(path).resolve()
    try:
        target_path.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "message": f"Folder '{target_path.name}' created successfully.",
            "data": {"path": str(target_path)},
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to create folder: {e}", "data": {}}


@action_registry.register(
    name="CREATE_FILE",
    description="Create a new empty text file or write content.",
    permission_level=PermissionLevel.ELEVATED,
    parameters=[
        ActionParameter(name="path", type_name="str", description="Path of the file to create"),
        ActionParameter(name="content", type_name="str", required=False, default="", description="Initial text content"),
    ],
    validator=_validate_file_path_param,
)
def create_file(path: str, content: str = "", **kwargs: Any) -> Dict[str, Any]:
    target_path = Path(path).resolve()
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {
            "success": True,
            "message": f"File '{target_path.name}' created.",
            "data": {"path": str(target_path)},
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to create file: {e}", "data": {}}


@action_registry.register(
    name="DELETE_FILE",
    description="Delete a non-system file. DANGEROUS: Requires explicit user confirmation.",
    permission_level=PermissionLevel.DANGEROUS,
    parameters=[ActionParameter(name="path", type_name="str", description="Path of the file to delete")],
    validator=_validate_file_path_param,
)
def delete_file(path: str, **kwargs: Any) -> Dict[str, Any]:
    target_path = Path(path).resolve()
    if not target_path.exists():
        return {"success": False, "message": f"File does not exist: '{path}'.", "data": {}}

    try:
        if target_path.is_file():
            target_path.unlink()
            return {"success": True, "message": f"File '{target_path.name}' was safely deleted.", "data": {}}
        elif target_path.is_dir():
            target_path.rmdir()
            return {"success": True, "message": f"Empty directory '{target_path.name}' was removed.", "data": {}}
        return {"success": False, "message": "Unknown file type.", "data": {}}
    except Exception as e:
        return {"success": False, "message": f"Failed to delete file: {e}", "data": {}}


@action_registry.register(
    name="SEARCH_FILES",
    description="Search for files by keyword in the user documents or desktop folders.",
    permission_level=PermissionLevel.NORMAL,
    parameters=[
        ActionParameter(name="query", type_name="str", description="Search query or keyword"),
        ActionParameter(name="root_dir", type_name="str", required=False, default=None, description="Starting folder"),
    ],
)
def search_files(query: str, root_dir: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
    start = Path(root_dir).resolve() if root_dir else Path.home() / "Documents"
    matches: List[str] = []
    q_lower = query.lower()

    if start.exists() and start.is_dir():
        for root, dirs, files in os.walk(str(start)):
            # limit depth and skip hidden folders
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if q_lower in f.lower():
                    matches.append(str(Path(root) / f))
                    if len(matches) >= 10:
                        break
            if len(matches) >= 10:
                break

    count = len(matches)
    if count > 0:
        return {
            "success": True,
            "message": f"Found {count} file(s) matching '{query}'.",
            "data": {"matches": matches},
        }
    return {
        "success": True,
        "message": f"No files found matching '{query}' in {start.name}.",
        "data": {"matches": []},
    }
